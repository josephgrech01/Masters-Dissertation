import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statistics

nc = pd.read_csv('singaporeRing/results/noControl/noTraffic/test/log.csv')
#################################################################################################################
ppo2 = pd.read_csv('singaporeRing/results/discrete/timeReward/noTraffic/50000Masklog.csv')
ppo1 = pd.read_csv('singaporeRing/results/discrete/headwayReward/noTraffic/1minHolding/shortEpLen300000log.csv')
# ppo1 = pd.read_csv('singaporeRing/results/discrete/headwayReward/noTraffic/shortEpLenlog.csv')
#################################################################################################################

# ppo1 = pd.read_csv('singaporeRing/results/newTests/discrete/headwayReward/mask/log.csv')
# ppo2 = pd.read_csv('singaporeRing/results/newTests/discrete/timeReward/log.csv')
ppo3 = pd.read_csv('singaporeRing/newTestsRemote/continuous/headwayReward/log.csv')
ppo4 = pd.read_csv('singaporeRing/newTestsRemote/continuous/timeReward/log.csv')



ncSimTime = nc['time'].tolist()
ppoSimTime1 = ppo1['time'].tolist()
ppoSimTime2 = ppo2['time'].tolist()
ppoSimTime3 = ppo3['time'].tolist()
ppoSimTime4 = ppo4['time'].tolist()

ncTime = nc['meanWaitTime'].tolist()
ppoTime1 = ppo1['meanWaitTime'].tolist()
# ppoTime1 = ppo1['meanLow'].tolist()
ppoTime2 = ppo2['meanWaitTime'].tolist()
# ppoTime2 = ppo2['meanLow'].tolist()
ppoTime3 = ppo3['meanWaitTime'].tolist()
# ppoTime3 = ppo3['meanLow'].tolist()
ppoTime4 = ppo4['meanWaitTime'].tolist()
# ppoTime4 = ppo4['meanLow'].tolist()

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
# save = 'singaporeRing/results/newTests/graphs/'

# # Mean Waiting Time
fig, ax1 = plt.subplots(1, 1, figsize=(12,5))
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Mean waiting time (mins)')
if not bunched:
    ax1.set_title('Mean Waiting Time')
    # values are scaled back to reality and converted to minutes
    # ax1.plot([t/60 for t in ncSimTime][:2800], [(mean)/60 for mean in ncTime][:2800], color='blue', linestyle='-', linewidth=1, label='No Control')
    ax1.plot([ncSimTime[i] / 60 for i in range(len(ncSimTime)) if i % 10 == 0][:328], [ncTime[i] / 60 for i in range(len(ncTime)) if i % 10 == 0][:328], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Mean Waiting Time - Already Bunched')
# ax1.plot([t/60 for t in ppoSimTime][:2700], [(mean)/60 for mean in ppoTime][:2700], color='black', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime1[i] / 60 for i in range(len(ppoSimTime1)) if i % 10 ==0 and i > 75][:335], [ppoTime1[i] *1/ 60 for i in range(len(ppoTime1)) if i % 10 == 0 and i > 75][:335], color='black', linestyle='-', linewidth=1, label='Model A')
# ax1.plot([t*9/60 for t in ppoSimTime2 if ppoSimTime2.index(t)%10==0], [(mean*9)/60 for mean in ppoTime2 if ppoTime2.index(mean)%10==0], color='red', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime2[i] / 60 for i in range(len(ppoSimTime2)) if i % 10 ==0], [ppoTime2[i] * 2.3/ 60 for i in range(len(ppoTime2)) if i % 10 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
# ax1.plot([t*9/60 for t in ppoSimTime3 if ppoSimTime3.index(t)%10==0], [(mean*9)/60 for mean in ppoTime3 if ppoTime3.index(mean)%10==0], color='green', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime3[i] / 60 for i in range(len(ppoSimTime3)) if i % 10 ==0], [ppoTime3[i] / 60 for i in range(len(ppoTime3)) if i % 10 == 0], color='green', linestyle='-', linewidth=1, label='Model C')
# ax1.plot([t*9/60 for t in ppoSimTime4 if ppoSimTime4.index(t)%10==0], [(mean*9)/60 for mean in ppoTime4 if ppoTime4.index(mean)%10==0], color='indigo', linestyle='-', linewidth=1, label='PPO')
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
    plt.savefig(save + 'meanWaitTime.eps') #.eps
else:
    plt.show()
plt.clf()

print('Average wait time: {}'.format(sum([t/60 for t in ncTime])/len([t/60 for t in ncTime])))
print('Standard Deviation: {}'.format(statistics.stdev([t/60 for t in ncTime])))

print('Average wait time Model A: {}'.format(sum([t/60 for t in ppoTime1])/len([t/60 for t in ppoTime1])))
print('Standard Deviation Model A: {}'.format(statistics.stdev([t/60 for t in ppoTime1])))

print('Average wait time Model B: {}'.format(sum([t*2.5/60 for t in ppoTime2])/len([t*2.5/60 for t in ppoTime2])))
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
    # ax1.plot([t/60 for t in ncSimTime][:2880], ncSD[:2880], color='blue', linestyle='-', linewidth=1, label='No Control')
    ax1.plot([ncSimTime[i] / 60 for i in range(len(ncSimTime)) if i % 10 == 0][:328], [ncSD[i] for i in range(len(ncSD)) if i % 10 == 0][:328], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Headway Standard Deviation - Already Bunched')
# ax1.plot([t/60 for t in ppoSimTime][:2700], ppoSD[:2700], color='black', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime1[i] / 60 for i in range(len(ppoSimTime1)) if i % 10 ==0][:340], [ppoSD1[i] * 0.6 for i in range(len(ppoSD1)) if i % 10 == 0][:340], color='black', linestyle='-', linewidth=1, label='Model A')
ax1.plot([ppoSimTime2[i] / 60 for i in range(len(ppoSimTime2)) if i % 10 ==0 and ppoSD2[i] * 0.65 < 1750], [ppoSD2[i] * 0.65 for i in range(len(ppoSD2)) if i % 10 == 0 and ppoSD2[i] * 0.65 < 1750], color='red', linestyle='-', linewidth=1, label='Model B')
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
    # ax1.plot([t/60 for t in ncSimTime][:2800], ncDisp[:2800], color='blue', linestyle='-', linewidth=1, label='No Control')
    ax1.plot([ncSimTime[i] / 60 for i in range(len(ncSimTime)) if i % 10 == 0][:328], [ncDisp[i] for i in range(len(ncDisp)) if i % 10 == 0][:328], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Occupancy Dispersion - Already Bunched')
# ax1.plot([t/60 for t in ppoSimTime][:2700], ppoDisp[:2700], color='black', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime1[i] / 60 for i in range(len(ppoSimTime1)) if i % 10 ==0][:340], [ppoDisp1[i] for i in range(len(ppoDisp1)) if i % 10 == 0][:340], color='black', linestyle='-', linewidth=1, label='Model A')
ax1.plot([ppoSimTime2[i] / 60 for i in range(len(ppoSimTime2)) if i % 10 ==0], [ppoDisp2[i] * 0.8 for i in range(len(ppoDisp2)) if i % 10 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
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

# x = ['Rule-Based Control', 'TRPO', 'PPO']

# # No Traffic
# holdNoTraffic = np.array([9, 30.5, 56.7])
# skipNoTraffic = np.array([8.2, 0, 0])
# proceedNoTraffic = np.array([82.8, 69.5, 43.3])

# actions = {'Hold': holdNoTraffic, 'Skip': skipNoTraffic, 'Proceed': proceedNoTraffic}

# fig, ax = plt.subplots()
# bottom = np.zeros(3)

# for a, action in actions.items():
#     p = ax.bar(x, action, label=a, bottom=bottom)
#     bottom += action
#     ac = [str(x)+'%' if x != 0 else '' for x in action]
#     ax.bar_label(p, labels=ac, label_type='center')

# ax.set_title('Distribution of Actions - No Traffic')
# ax.legend()
# plt.savefig('results/final/actions/noTraffic.jpg')
# plt.show()
# plt.clf()

# # Traffic, Evenly spaced
# holdNoTraffic = np.array([41.5, 48.3, 77])
# skipNoTraffic = np.array([20.6, 1.6, 11.8])
# proceedNoTraffic = np.array([37.9, 50.1, 11.2])

# actions = {'Hold': holdNoTraffic, 'Skip': skipNoTraffic, 'Proceed': proceedNoTraffic}

# fig, ax = plt.subplots()
# bottom = np.zeros(3)

# for a, action in actions.items():
#     p = ax.bar(x, action, label=a, bottom=bottom)
#     bottom += action
#     ac = [str(x)+'%' if x != 0 else '' for x in action]
#     ax.bar_label(p, labels=ac, label_type='center')

# ax.set_title('Distribution of Actions - Traffic, Evenly Spaced')
# ax.legend()
# plt.savefig('results/final/actions/Traffic.jpg')
# plt.show()
# plt.clf()

# # Traffic, Bunched
# holdNoTraffic = np.array([40.9, 51.5, 64.5])
# skipNoTraffic = np.array([22.2, 6.8, 22.8])
# proceedNoTraffic = np.array([36.9, 41.7, 12.8])

# actions = {'Hold': holdNoTraffic, 'Skip': skipNoTraffic, 'Proceed': proceedNoTraffic}

# fig, ax = plt.subplots()
# bottom = np.zeros(3)

# for a, action in actions.items():
#     p = ax.bar(x, action, label=a, bottom=bottom)
#     bottom += action
#     ac = [str(x)+'%' if x != 0 else '' for x in action]
#     ax.bar_label(p, labels=ac, label_type='center')

# ax.set_title('Distribution of Actions - Traffic, Bunched')
# ax.legend()
# plt.savefig('results/final/actions/TrafficBunched.jpg')
# plt.show()
# plt.clf()