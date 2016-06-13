#####################
# power coordinator #
#####################
#  channon@iit.edu  #
#####################
#      DSSnet       #
#    Version 2.0    #
#####################

import win32com.client
import zmq
import numpy
from numpy import array
import sys
import argparse
from gen import updateG
from load import updateL
import ied
import DSSnet_handler as handler

###########
#  Setup  #
###########

parser = argparse.ArgumentParser(description= 'Manages power system simulation and synchronizes with the network coordinator')
parser.add_argument('--version', action='version',version='DSSnet 2.0')
parser.add_argument('--ip', help='ip of power coordinator',default='10.47.142.26',type=str)
parser.add_argument('--port', help='port reserved for power coordinator',default='50021',type=str)
parser.add_argument('--IED_config', help='path to IED file',default='IED.config',type=str)
parser.add_argument('--circuit_filename', help='path to main circuit file',default = 'master.dss', type=str)
args = parser.parse_args()

engine=win32com.client.Dispatch("OpenDSSEngine.DSS")
engine.Start("0")
engine.Text.Command='clear'
circuit=engine.ActiveCircuit

def setupCircuit():
    print('starting circuit')
    engine.Text.Command='compile '+ args.circuit_filename
    print('circuit compiled')
 
# socket to network coordinator
def setupSocket():
    print('setting up socket')
    contextIn = zmq.Context()
    serverIn = contextIn.socket(zmq.REP)
    serverIn.bind("tcp://%s:%s" % (args.ip,args.port))
    print('socket is setup')
    return serverIn

##################
#  load in IEDs  #
##################

pmu = []
loads = []
gens = []

def read_config():
    with open(args.IED_config, 'r') as ied_config:
        for line in ied_config:
            if line[0] != '#':
                ied = line.split()
                if ied[0] =='load':
                    add_load(ied)
                if ied[0] =='gen':
                    add_gen(ied)
                if ied[0] =='pmu':
                    add_pmu(ied)

#load = load
def add_load(ied):
    loads.append(ied[1])

#gen = generator
def add_gen(ied):
    gens.append(ied[1])

# pmu = monitor
def add_pmu(ied):
    pmu.append(ied[1])

######################
#  Helper Functions  #
######################

def print_vsource():
    source = engine.ActiveCircuit.vsource
    return source

def getBusVolts():
    busNames=engine.ActiveCircuit.AllBusNames
    n_bus=len(busNames)

    V1_tup= engine.ActiveCircuit.AllBusVolts
    V1=array(V1_tup)
    V1=V.reshape(n_bus,3,2)
    return V1

def updateLoads(t):
    for x in loads:
        result = updateL(x,t)
        update_controllable_loads(x,result)

def updateGeneration(t):
    for x in gens:
        result = updateG(g,t)       
        update_controllable_gens(x,result)

def update_controllable_loads(load,val):
    engine.Text.Command= 'load.%s.kW=%s'% (str(int(load)),str(int(val)))

def update_controllable_gens(gen,val):
    engine.Text.Command= 'generator.%s.kW=%s'% (str(int(gen)),str(int(val)))
    
def read_monitor(element):
    DSSMonitors = circuit.Monitors
    direct('sample')

    DSSMonitors.saveAll()
    DSSMonitors.Name = element
    time=DSSMonitors.dblHour[0]
    v1 = DSSMonitors.Channel(1)[0]
    vang1 = DSSMonitors.Channel(2)[0]
    v2 = DSSMonitors.Channel(3)[0]
    vang2 = DSSMonitors.Channel(4)[0]
    v3 = DSSMonitors.Channel(5)[0]
    vang3 = DSSMonitors.Channel(6)[0]
    i1 = DSSMonitors.Channel(7)[0]
    iang1 = DSSMonitors.Channel(8)[0]
    i2 = DSSMonitors.Channel(9)[0]
    iang2 = DSSMonitors.Channel(10)[0]
    i3 = DSSMonitors.Channel(11)[0]
    iang3 = DSSMonitors.Channel(12)[0]
    
    #clear
    DSSMonitors.resetAll()
    return ('%d %d %d %d %d %d %d %d %d %d %d %d %d' % 
            ( time, 
                v1, vang1,
                v2, vang2,
                v3, vang3,
                i1, iang1,
                i2, iang2,
                i3, iang3))

def fault(name,phase,node1,node2):
    if node2 == 'a' :
        print('New Fault.%s phases=%s Bus1=%s' % (name,phase,node1))
        engine.Text.Command='New Fault.%s phases=%s Bus1=%s' % (name,phase,node1)
    else:
        engine.Text.Command='New Fault.%s phases=%s Bus1=%s Bus2=%s' % (name,phase,node1,node2)
        print('New Fault.%s phases=%s Bus1=%s Bus2=%s' % (name,phase,node1,node2))

def direct(cmd):
    engine.Text.Command=cmd
    
def updateTime(dt):
    cmd='set sec=%s' % dt
    engine.Text.Command=cmd
    updateLoads(dt)
    updateGeneration(dt)
    engine.Text.Command='solve'

##############################
#  communicate with Comm net #
##############################

def commNet(serverIn):
    print('waiting for request')
    requestIn_bytes = serverIn.recv()
    requestIn_str = requestIn_bytes.decode('utf-8')
    line0 = requestIn_str
    line=line0.split()
    if line[0] == 'update':
        print ('update request recieved from emulation coordinator: %s' % line0)
        length=len(line)

        # what does mininet want us to do????
        if length > 1 :
            newTime = line[5]
            updateTime(newTime)

            reply='ok'
            
            #do preprocessing
            try:
                preprocess=getattr(handler,line[3])
                pre_processed_event=preprocess(line)
                # RUN MAIN EVENT
                funkName = pre_processed_event
                try:
                    processed_event = eval(funkName)
                except NameError :
                    print('error with eval' % pre_processed_event)

            except AttributeError:
                print('error with pre_processed_event %s' % line)

            #do postprocessing
            try:
                postprocess=getattr(handler,line[4])
                reply=postprocess(line,processed_event)
            except AttributeError:
                print('error with post %s' % line)
            ok=reply.encode('utf-8')
            serverIn.send(ok)

            return (1)
        else:
            print('request recieved but with no content')
            # solve anyway? crash? ignore?  

    ok='ok'.encode('utf-8')
    serverIn.send(ok)

def main():
    setupCircuit()
    server = setupSocket()
    read_config()
    while True:
        commNet(server)

main()