import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statistics

nc = pd.read_csv('scenario2/results/noControl/noTraffic/log.csv')
# ppo = pd.read_csv('scenario2/results/continuous/timeReward/traffic90/log.csv')
ppo1 = pd.read_csv('scenario2/results/discrete/headwayReward/noTraffic/log.csv')
ppo2 = pd.read_csv('scenario2/results/discrete/timeReward/noTraffic/log.csv')
ppo3 = pd.read_csv('scenario2/results/continuous/headwayReward/noTraffic/log.csv')
ppo4 = pd.read_csv('scenario2/results/continuous/timeReward/noTraffic/log.csv')

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
 
ncDisp = nc['dispersion'].tolist()
ppoDisp1 = ppo1['dispersion'].tolist()
ppoDisp2 = ppo2['dispersion'].tolist()
ppoDisp3 = ppo3['dispersion'].tolist()
ppoDisp4 = ppo4['dispersion'].tolist()

bunched = False
# bunched = True

# save = 'scenario2/results/graphs/continuous/timeReward/bunched/'
save = None

# # Mean Waiting Time
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Mean waiting time (mins)')
if not bunched:
    ax1.set_title('Mean Waiting Time')
    # values are scaled back to reality and converted to minutes
    # ax1.plot([t*9/60 for t in ncSimTime], [(mean*9)/60 for mean in ncTime], color='blue', linestyle='-', linewidth=1, label='No Control')
    ax1.plot([ncSimTime[i] * 9 /60 for i in range(len(ncSimTime)) if i % 7 == 0], [ncTime[i] * 9 / 60 for i in range(len(ncTime)) if i % 7 == 0], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Mean Waiting Time - Already Bunched')
# ax1.plot([t*9/60 for t in ppoSimTime1 if ppoSimTime1.index(t)%10==0], [(mean*9)/60 for mean in ppoTime1 if ppoTime1.index(mean)%10==0], color='black', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime1[i] * 9 / 60 for i in range(len(ppoSimTime1)) if i % 7 ==0], [ppoTime1[i] * 9 / 60 for i in range(len(ppoTime1)) if i % 7 == 0], color='black', linestyle='-', linewidth=1, label='Model A')
# ax1.plot([t*9/60 for t in ppoSimTime2 if ppoSimTime2.index(t)%10==0], [(mean*9)/60 for mean in ppoTime2 if ppoTime2.index(mean)%10==0], color='red', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime2[i] * 9 / 60 for i in range(len(ppoSimTime2)) if i % 7 ==0], [ppoTime2[i] * 9 / 60 for i in range(len(ppoTime2)) if i % 7 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
# ax1.plot([t*9/60 for t in ppoSimTime3 if ppoSimTime3.index(t)%10==0], [(mean*9)/60 for mean in ppoTime3 if ppoTime3.index(mean)%10==0], color='green', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime3[i] * 9 / 60 for i in range(len(ppoSimTime3)) if i % 7 ==0], [ppoTime3[i] * 9 / 60 for i in range(len(ppoTime3)) if i % 7 == 0], color='green', linestyle='-', linewidth=1, label='Model C')
# ax1.plot([t*9/60 for t in ppoSimTime4 if ppoSimTime4.index(t)%10==0], [(mean*9)/60 for mean in ppoTime4 if ppoTime4.index(mean)%10==0], color='indigo', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime4[i] * 9 / 60 for i in range(len(ppoSimTime4)) if i % 7 ==0], [ppoTime4[i] * 9 / 60 for i in range(len(ppoTime4)) if i % 7 == 0], color='orange', linestyle='-', linewidth=1, label='Model D')
ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'meanWaitTime.eps')
else:
    plt.show()
plt.clf()

# print('Average wait time: {}'.format(sum([t*9/60 for t in ppoTime])/len([t*9/60 for t in ppoTime])))
# print('Standard Deviation: {}'.format(statistics.stdev([t*9/60 for t in ppoTime])))

# # Headway Standard Deviation
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Headway Standard Deviation')
if not bunched:
    ax1.set_title('Headway Standard Deviation')
    # ax1.plot([t*9/60 for t in ncSimTime], ncSD, color='blue', linestyle='-', linewidth=1, label='No Control')
    ax1.plot([ncSimTime[i] * 9 / 60 for i in range(len(ncSimTime)) if i % 7 == 0], [ncSD[i] for i in range(len(ncSD)) if i % 7 == 0], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Headway Standard Deviation - Already Bunched')# ax1.plot([t*9/60 for t in ppoSimTime], ppoSD, color='black', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime1[i] * 9 / 60 for i in range(len(ppoSimTime1)) if i % 7 ==0], [ppoSD1[i] for i in range(len(ppoSD1)) if i % 7 == 0], color='black', linestyle='-', linewidth=1, label='Model A')
ax1.plot([ppoSimTime2[i] * 9 / 60 for i in range(len(ppoSimTime2)) if i % 7 ==0], [ppoSD2[i] for i in range(len(ppoSD2)) if i % 7 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
ax1.plot([ppoSimTime3[i] * 9 / 60 for i in range(len(ppoSimTime3)) if i % 7 ==0], [ppoSD3[i] for i in range(len(ppoSD3)) if i % 7 == 0], color='green', linestyle='-', linewidth=1, label='Model C')
ax1.plot([ppoSimTime4[i] * 9 / 60 for i in range(len(ppoSimTime4)) if i % 7 ==0], [ppoSD4[i] for i in range(len(ppoSD4)) if i % 7 == 0], color='orange', linestyle='-', linewidth=1, label='Model D')
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
    # ax1.plot([t*9/60 for t in ncSimTime], ncDisp, color='blue', linestyle='-', linewidth=1, label='No Control')
    ax1.plot([ncSimTime[i] * 9 / 60 for i in range(len(ncSimTime)) if i % 7 == 0], [ncDisp[i] for i in range(len(ncDisp)) if i % 7 == 0], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Occupancy Dispersion - Already Bunched')
# ax1.plot([t*9/60 for t in ppoSimTime], ppoDisp, color='black', linestyle='-', linewidth=1, label='PPO')
ax1.plot([ppoSimTime1[i] * 9 / 60 for i in range(len(ppoSimTime1)) if i % 7 ==0], [ppoDisp1[i] for i in range(len(ppoDisp1)) if i % 7 == 0], color='black', linestyle='-', linewidth=1, label='Model A')
ax1.plot([ppoSimTime2[i] * 9 / 60 for i in range(len(ppoSimTime2)) if i % 7 ==0], [ppoDisp2[i] for i in range(len(ppoDisp2)) if i % 7 == 0], color='red', linestyle='-', linewidth=1, label='Model B')
ax1.plot([ppoSimTime3[i] * 9 / 60 for i in range(len(ppoSimTime3)) if i % 7 ==0], [ppoDisp3[i] for i in range(len(ppoDisp3)) if i % 7 == 0], color='green', linestyle='-', linewidth=1, label='Model C')
ax1.plot([ppoSimTime4[i] * 9 / 60 for i in range(len(ppoSimTime4)) if i % 7 ==0], [ppoDisp4[i] for i in range(len(ppoDisp4)) if i % 7 == 0], color='orange', linestyle='-', linewidth=1, label='Model D')
ax1.grid()
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