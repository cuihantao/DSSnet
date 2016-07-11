#!/bin/python

# file used for processing synchronization events

# pre-processing events

import pipes


def pre_gen(msg,net,hosts):
    return msg

def pre_load(msg,net,hosts):
    return msg

def pre_pmu(msg,net,hosts):
    return msg


# post processing events

def post_load(event,reply,net,hosts,pipes):
    return reply

def post_gen(event,reply,net,hosts,pipes):
    return reply

def post_pmu(event,reply,net,hosts,pipes):
    print event
    print reply
    return reply

def pre_load_report(msg,net,hosts):
    return msg

def pre_gen_report(msg,net,hosts):
    return msg

def post_load_report(event,reply,net,hosts,pipes):
    i = (event.split()[6])
    value = reply
    send_sync_event(value,pipes[i])
    return reply

def post_gen_report(event,reply,net,hosts,pipes):
    i = (event.split()[6])
    value = reply
    send_sync_event(value,pipes[i])
    return reply

def pre_energyStorage(msg,net,hosts):
    return msg

def post_energyStorage(event,reply,net,hosts,pipes):
    return reply
