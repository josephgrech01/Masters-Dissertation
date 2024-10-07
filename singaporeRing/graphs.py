import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statistics

nc = pd.read_csv('singaporeRing/results/noControl/noTraffic/test/log.csv')
# ppo = pd.read_csv('singaporeRing/results/discrete/timeReward/noTraffic/50000Masklog.csv')
ppo = pd.read_csv('singaporeRing/results/discrete/headwayReward/noTraffic/1minHolding/shortEpLen300000log.csv')
# ppo = pd.read_csv('singaporeRing/results/discrete/headwayReward/noTraffic/shortEpLenlog.csv')

ncSimTime = nc['time'].tolist()
ppoSimTime = ppo['time'].tolist()

ncTime = nc['meanWaitTime'].tolist()
ppoTime = ppo['meanWaitTime'].tolist()

ncSD = nc['headwaySD'].tolist()
ppoSD = ppo['headwaySD'].tolist()
 
ncDisp = nc['disperion'].tolist()
ppoDisp = ppo['dispersion'].tolist()

bunched = False
save = None
# save = 'singaporeRing/results/graphs/discrete/timeReward/'

# # Mean Waiting Time
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Mean waiting time (mins)')
if not bunched:
    ax1.set_title('Mean Waiting Time')
    # values are scaled back to reality and converted to minutes
    ax1.plot([t/60 for t in ncSimTime][:2800], [(mean)/60 for mean in ncTime][:2800], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Mean Waiting Time - Already Bunched')
ax1.plot([t/60 for t in ppoSimTime][:2700], [(mean)/60 for mean in ppoTime][:2700], color='black', linestyle='-', linewidth=1, label='PPO')
ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'meanWaitTime.jpg') #.eps
else:
    plt.show()
plt.clf()

print('Average wait time: {}'.format(sum([t/60 for t in ncTime])/len([t/60 for t in ncTime])))
print('Standard Deviation: {}'.format(statistics.stdev([t/60 for t in ncTime])))

print('Average wait time: {}'.format(sum([t/60 for t in ppoTime])/len([t/60 for t in ppoTime])))
print('Standard Deviation: {}'.format(statistics.stdev([t/60 for t in ppoTime])))

# # Headway Standard Deviation
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('Time (mins)')
ax1.set_ylabel('Headway Standard Deviation')
if not bunched:
    ax1.set_title('Headway Standard Deviation')
    ax1.plot([t/60 for t in ncSimTime][:2880], ncSD[:2880], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Headway Standard Deviation - Already Bunched')
ax1.plot([t/60 for t in ppoSimTime][:2700], ppoSD[:2700], color='black', linestyle='-', linewidth=1, label='PPO')
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
if not bunched:
    ax1.set_title('Occupancy Dispersion')
    ax1.plot([t/60 for t in ncSimTime][:2800], ncDisp[:2800], color='blue', linestyle='-', linewidth=1, label='No Control')
else:
    ax1.set_title('Occupancy Dispersion - Already Bunched')
ax1.plot([t/60 for t in ppoSimTime][:2700], ppoDisp[:2700], color='black', linestyle='-', linewidth=1, label='PPO')
ax1.grid()
plt.legend()
if save is not None:
    plt.savefig(save + 'occDisp.jpg')
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