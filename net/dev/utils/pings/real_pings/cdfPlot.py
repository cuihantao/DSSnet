import sys
import matplotlib.pyplot as plt
import numpy as np
baseFile = sys.argv[1] 
vtFile = sys.argv[2] 
no_vtFile = sys.argv[3] 


vt = np.loadtxt(vtFile)# with pause
bl = np.loadtxt(baseFile)
nvt = np.loadtxt(no_vtFile)


# sort the data:
vt_sorted = np.sort(vt)# paused
nvt_sorted = np.sort(nvt)# paused
bl_sorted = np.sort(bl)


# calculate the proportional values of samples
pvt = 1. * np.arange(len(vt)) / (len(vt) - 1) #paused
pnvt = 1. * np.arange(len(nvt)) / (len(nvt) - 1) #paused
pbl = 1. * np.arange(len(bl)) / (len(bl) -1)

# plot the sorted data:
fig = plt.figure()

ax1 = fig.add_subplot(111)#121
ax1.axis([0.00, 0.004, 0, 1])
ax1.set_title('Ping rtt in DSSnet')
ax1.plot(bl_sorted,pbl,color='b', label='BaseLine')
ax1.set_xlabel('$rtt-seconds$')
ax1.set_ylabel('$p$')
ax1.plot(vt_sorted,pvt,color='r',label='OVS in vt')
ax1.plot(nvt_sorted,pnvt,color='g',label='OVS not in vt')
plt.legend(loc='lower right',shadow = True,fancybox=True)#,fontsize='small')

'''
ax2 = fig.add_subplot(122)#121
ax2.axis([float(sys.argv[3]),
          float(sys.argv[4]),
          float(sys.argv[5]),
          float(sys.argv[6])])
ax2.set_title('pause_red_vs_noPause_blue')
ax2.plot(bl_sorted,pbl,color='b')
ax2.set_xlabel('$rtt-ms$')
ax2.set_ylabel('$p$')
ax2.plot(vt_sorted,pvt,color='r')
'''

plt.show()
