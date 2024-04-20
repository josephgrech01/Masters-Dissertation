import pandas as pd
import numpy as np

means = []
for i in range(1,10):
    log = pd.read_csv('singapore/results/sidewalks/test/fypReward/fyp' + str(i) + '.csv')

    meanWaitTime = log['meanWaitTime'].tolist()[580:4250]

    average = sum(meanWaitTime)/len(meanWaitTime)
    means.append(average)

average = sum(means) / len(means)
print('Average PPO: {}'.format(average))