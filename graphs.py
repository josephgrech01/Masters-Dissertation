import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

log = pd.read_csv('singapore/results/sidewalks/test/noControl.csv')
# log = pd.read_csv('singapore/results/sidewalks/test/fyp1800000.csv')

time = log['time'].tolist()
meanWaitTime = log['meanWaitTime'].tolist()

a = 580
b = 4250

fig, ax1 = plt.subplots(1, 1)
ax1.set_xbound(6,23)
ax1.set_xlabel('Time of day')
ax1.set_ylabel('Mean Waiting Time')
ax1.plot([(t/3600) + 6.5 for t in time][a:b], meanWaitTime[a:b], linewidth=0.8)
ax1.grid()
# plt.savefig('singapore/results/sidewalks/ppoFYPreward.jpg')
plt.show()

print('Average: {}'.format(sum(meanWaitTime[a:b])/len(meanWaitTime[a:b])))

