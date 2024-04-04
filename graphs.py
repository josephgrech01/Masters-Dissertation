import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

log = pd.read_csv('results/test/log3by10num1.csv')

time = log['time'].tolist()
meanWaitTime = log['meanWaitTime'].tolist()


fig, ax1 = plt.subplots(1, 1)
ax1.set_xbound(6,23)
ax1.set_xlabel('Time of day')
ax1.set_ylabel('Mean Waiting Time')
ax1.plot([(t/3600) + 6.5 for t in time][350:4850], meanWaitTime[350:4850], linewidth=1.5)
ax1.grid()
plt.savefig('results/test/3by10Temp1.jpg')
plt.show()

print('Average 9by4.5: {}'.format(sum(meanWaitTime[350:4850])/len(meanWaitTime[350:4850])))

