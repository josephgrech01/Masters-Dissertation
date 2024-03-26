import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

log = pd.read_csv('results/log.csv')

time = log['time'].tolist()
meanWaitTime = log['meanWaitTime'].tolist()


fig, ax1 = plt.subplots(1, 1)
ax1.set_xbound(6,23)
ax1.set_xlabel('Time')
ax1.set_ylabel('Mean Waiting Time')
ax1.plot([(t/3600) + 6.5 for t in time], meanWaitTime, linewidth=1.5)
ax1.grid()
plt.savefig('results/speed3.9.jpg')
plt.show()

