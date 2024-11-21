import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statistics

nc = pd.read_csv('singaporeRing/results/noControl/log.csv')
ppo1 = pd.read_csv('singaporeRing/results/discrete/headwayReward/log.csv')
ppo2 = pd.read_csv('singaporeRing/results/discrete/timeReward/log.csv')
ppo3 = pd.read_csv('singaporeRing/results/continuous/headwayReward/log.csv')
ppo4 = pd.read_csv('singaporeRing/results/continuous/timeReward/log.csv')

ncSimTime = nc['time'].tolist()
ppoSimTime1 = ppo1['time'].tolist()
ppoSimTime2 = ppo2['time'].tolist()
ppoSimTime3 = ppo3['time'].tolist()
ppoSimTime4 = ppo4['time'].tolist()

ncTime = nc['meanWaitTime'].tolist()
ppoTime1 = ppo1['meanWaitTime'].tolist()
ppoTime2 = ppo2['meanWaitTime'].tolist()
ppoTime3 = ppo3['meanWaitTime'].tolist()
ppoTime4 = ppo4['meanWaitTime'].tolist()

ncSD = nc['headwaySD'].tolist()
ppoSD1 = ppo1['headwaySD'].tolist()
ppoSD2 = ppo2['headwaySD'].tolist()
ppoSD3 = ppo3['headwaySD'].tolist()
ppoSD4 = ppo4['headwaySD'].tolist()
 
ncDisp = nc['disperion'].tolist()
ppoDisp1 = ppo1['dispersion'].tolist()
ppoDisp2 = ppo2['dispersion'].tolist()
ppoDisp3 = ppo3['dispersion'].tolist()
ppoDisp4 = ppo4['dispersion'].tolist()

bunched = False
save = None
# save = 'singaporeRing/results/graphs/'

# # Mean Waiting Time
fig, ax1 = plt.subplots(1, 1, figsize=(12,5))
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Mean waiting time (mins)')
if not bunched:
    ax1.set_title('Mean Waiting Time')
    # values are scaled back to reality and converted to minutes
    ax1.plot([ncSimTime[i] / 60 for i in range(len(ncSimTime)) if i % 10 == 0][:328], [ncTime[i] / 60 for i in range(len(ncTime)) if i % 10 == 0][:328], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Mean Waiting Time - Already Bunched')
ax1.plot([ppoSimTime1[i] / 60 for i in range(len(ppoSimTime1)) if i % 10 ==0][:335], [ppoTime1[i] / 60 for i in range(len(ppoTime1)) if i % 10 == 0][:335], color='black', linestyle='-', linewidth=1, label='Model A')
ax1.plot([ppoSimTime2[i] / 60 for i in range(len(ppoSimTime2)) if i % 10 ==0], [ppoTime2[i] / 60 for i in range(len(ppoTime2)) if i % 10 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
ax1.plot([ppoSimTime3[i] / 60 for i in range(len(ppoSimTime3)) if i % 10 ==0], [ppoTime3[i] / 60 for i in range(len(ppoTime3)) if i % 10 == 0], color='green', linestyle='-', linewidth=1, label='Model C')
ax1.plot([ppoSimTime4[i] / 60 for i in range(len(ppoSimTime4)) if i % 10 ==0], [ppoTime4[i] / 60 for i in range(len(ppoTime4)) if i % 10 == 0], color='orange', linestyle='-', linewidth=1, label='Model D')

initial_offset = ncSimTime[0] / 60
tick_interval = 100
max_time = ncSimTime[-1] / 60
new_ticks = list(range(0, int(max_time - initial_offset) + tick_interval, tick_interval))

ax1.set_xticks([tick + initial_offset for tick in new_ticks])
ax1.set_xticklabels(new_ticks)

ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'meanWaitTime.eps')
else:
    plt.show()
plt.clf()

print('Average wait time: {}'.format(sum([t/60 for t in ncTime])/len([t/60 for t in ncTime])))
print('Standard Deviation: {}'.format(statistics.stdev([t/60 for t in ncTime])))

print('Average wait time Model A: {}'.format(sum([t/60 for t in ppoTime1])/len([t/60 for t in ppoTime1])))
print('Standard Deviation Model A: {}'.format(statistics.stdev([t/60 for t in ppoTime1])))

print('Average wait time Model B: {}'.format(sum([t/60 for t in ppoTime2])/len([t/60 for t in ppoTime2])))
print('Standard Deviation Model B: {}'.format(statistics.stdev([t/60 for t in ppoTime2])))

print('Average wait time Model C: {}'.format(sum([t/60 for t in ppoTime3])/len([t/60 for t in ppoTime3])))
print('Standard Deviation Model C: {}'.format(statistics.stdev([t/60 for t in ppoTime3])))

print('Average wait time Model D: {}'.format(sum([t/60 for t in ppoTime4])/len([t/60 for t in ppoTime4])))
print('Standard Deviation Model D: {}'.format(statistics.stdev([t/60 for t in ppoTime4])))

# # Headway Standard Deviation
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Headway Standard Deviation')
if not bunched:
    ax1.set_title('Headway Standard Deviation')
    ax1.plot([ncSimTime[i] / 60 for i in range(len(ncSimTime)) if i % 10 == 0][:328], [ncSD[i] for i in range(len(ncSD)) if i % 10 == 0][:328], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Headway Standard Deviation - Already Bunched')
ax1.plot([ppoSimTime1[i] / 60 for i in range(len(ppoSimTime1)) if i % 10 ==0][:340], [ppoSD1[i] for i in range(len(ppoSD1)) if i % 10 == 0][:340], color='black', linestyle='-', linewidth=1, label='Model A')
ax1.plot([ppoSimTime2[i] / 60 for i in range(len(ppoSimTime2)) if i % 10 ==0], [ppoSD2[i] for i in range(len(ppoSD2)) if i % 10 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
ax1.plot([ppoSimTime3[i] / 60 for i in range(len(ppoSimTime3)) if i % 10 ==0], [ppoSD3[i] for i in range(len(ppoSD3)) if i % 10 == 0], color='green', linestyle='-', linewidth=1, label='Model C')
ax1.plot([ppoSimTime4[i] / 60 for i in range(len(ppoSimTime4)) if i % 10 ==0], [ppoSD4[i] for i in range(len(ppoSD4)) if i % 10 == 0], color='orange', linestyle='-', linewidth=1, label='Model D')

initial_offset = ncSimTime[0] / 60
tick_interval = 100
max_time = ncSimTime[-1] / 60
new_ticks = list(range(0, int(max_time - initial_offset) + tick_interval, tick_interval))

ax1.set_xticks([tick + initial_offset for tick in new_ticks])
ax1.set_xticklabels(new_ticks)

ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'headwaySD.eps')
else:
    plt.show()
plt.clf()

# # Occupancy Dispersion
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Occupancy Dispersion')
if not bunched:
    ax1.set_title('Occupancy Dispersion')
    ax1.plot([ncSimTime[i] / 60 for i in range(len(ncSimTime)) if i % 10 == 0][:328], [ncDisp[i] for i in range(len(ncDisp)) if i % 10 == 0][:328], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Occupancy Dispersion - Already Bunched')
ax1.plot([ppoSimTime1[i] / 60 for i in range(len(ppoSimTime1)) if i % 10 ==0][:340], [ppoDisp1[i] for i in range(len(ppoDisp1)) if i % 10 == 0][:340], color='black', linestyle='-', linewidth=1, label='Model A')
ax1.plot([ppoSimTime2[i] / 60 for i in range(len(ppoSimTime2)) if i % 10 ==0], [ppoDisp2[i] for i in range(len(ppoDisp2)) if i % 10 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
ax1.plot([ppoSimTime3[i] / 60 for i in range(len(ppoSimTime3)) if i % 10 ==0], [ppoDisp3[i] for i in range(len(ppoDisp3)) if i % 10 == 0], color='green', linestyle='-', linewidth=1, label='Model C')
ax1.plot([ppoSimTime4[i] / 60 for i in range(len(ppoSimTime4)) if i % 10 ==0], [ppoDisp4[i] for i in range(len(ppoDisp4)) if i % 10 == 0], color='orange', linestyle='-', linewidth=1, label='Model D')
ax1.grid()

initial_offset = ncSimTime[0] / 60
tick_interval = 100
max_time = ncSimTime[-1] / 60
new_ticks = list(range(0, int(max_time - initial_offset) + tick_interval, tick_interval))

ax1.set_xticks([tick + initial_offset for tick in new_ticks])
ax1.set_xticklabels(new_ticks)

plt.legend()
if save is not None:
    plt.savefig(save + 'occDisp.eps')
else:
    plt.show()
plt.clf()