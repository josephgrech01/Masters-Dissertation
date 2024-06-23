import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

traffic29 = pd.read_csv('wang2020/results/maskablePPO/updatedHeadwaysDur15/traffic29/log.csv')
traffic56 = pd.read_csv('wang2020/results/maskablePPO/updatedHeadwaysDur15/traffic56/log.csv')
traffic90 = pd.read_csv('wang2020/results/maskablePPO/updatedHeadwaysDur15/traffic90/log.csv')

simTime1 = traffic29['time'].tolist()
simTime2 = traffic56['time'].tolist()
simTime3 = traffic90['time'].tolist()

time29 = traffic29['meanWaitTime'].tolist()
time56 = traffic56['meanWaitTime'].tolist()
time90 = traffic90['meanWaitTime'].tolist()

sd1 = traffic29['headwaySD'].tolist()
sd2 = traffic56['headwaySD'].tolist()
sd3 = traffic90['headwaySD'].tolist()
 
disp1 = traffic29['dispersion'].tolist()
disp2 = traffic56['dispersion'].tolist()
disp3 = traffic90['dispersion'].tolist()

save = None#'wang2020/results/graphs/initial/'

# # Mean Waiting Time
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Mean waiting time (mins)')
ax1.set_title('Mean Waiting Time')
# values are scaled back to reality and converted to minutes
ax1.plot([t*9/60 for t in simTime1], [(mean*9)/60 for mean in time29], color='blue', linestyle='-', linewidth=1, label='A')
ax1.plot([t*9/60 for t in simTime2], [(mean*9)/60 for mean in time56], color='black', linestyle='-', linewidth=1, label='B')
ax1.plot([t*9/60 for t in simTime3], [(mean*9)/60 for mean in time90], color='red', linestyle='-', linewidth=1, label='C')
ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'meanWaitTime.jpg')
else:
    plt.show()
plt.clf()

print('Average A: {}'.format(sum([(mean*9)/60 for mean in time29])/len([(mean*9)/60 for mean in time29])))
print('Average B: {}'.format(sum([(mean*9)/60 for mean in time56])/len([(mean*9)/60 for mean in time56])))
print('Average C: {}'.format(sum([(mean*9)/60 for mean in time90])/len([(mean*9)/60 for mean in time90])))

# # Headway Standard Deviation
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Headway Standard Deviation')
ax1.set_title('Headway Standard Deviation')
ax1.plot([t*9/60 for t in ncSimTime], ncSD, color='blue', linestyle='-', linewidth=1, label='No Control')
ax1.plot([t*9/60 for t in ppoSimTime], ppoSD, color='black', linestyle='-', linewidth=1, label='PPO')
ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'headwaySD.jpg')
else:
    plt.show()
plt.clf()

# # Occupancy Dispersion
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Occupancy Dispersion')
ax1.set_title('Occupancy Dispersion')
ax1.plot([t*9/60 for t in ncSimTime], ncDisp, color='blue', linestyle='-', linewidth=1, label='No Control')
ax1.plot([t*9/60 for t in ppoSimTime], ppoDisp, color='black', linestyle='-', linewidth=1, label='PPO')
ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'occDisp.jpg')
else:
    plt.show()
plt.clf()