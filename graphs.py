import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

l = []
save = 'singapore/results/sidewalks/doubleFreq/nc/'
metric = 'Standard Deviation'
for i in range(0,1):
    log = pd.read_csv('singapore/results/sidewalks/doubleFreq/ncall.csv')
    # log = pd.read_csv('singapore/results/sidewalks/averages/ppo/run'+str(i)+'/all.csv')
    # log = pd.read_csv('singapore/results/sidewalks/test/traffic/nc.csv')

    time = log['time'].tolist()
    median = log['sd'].tolist()

    a = 600
    b = 4250

    fig, ax1 = plt.subplots(1, 1)
    ax1.set_xbound(6,23)
    ax1.set_title(metric+' Waiting Time (All Stops) - No Control')
    ax1.set_xlabel('Time of day')
    ax1.set_ylabel(metric+' Waiting Time')
    ax1.plot([(t/3600) + 6.5 for t in time][a:b], median[a:b], linewidth=0.8)
    ax1.grid()
    # plt.savefig(save+'run'+str(i)+'all.jpg')
    plt.savefig(save+'allSD.jpg')
    # plt.show()
    plt.clf()

    average = sum(median[a:b])/len(median[a:b])
    l.append(average)
# print('Average: {}'.format(sum(meanWaitTime[a:b])/len(meanWaitTime[a:b])))

l.append(sum(l)/len(l))

dict = {'means':l}
df = pd.DataFrame(dict)
df.to_csv(save+'allSD.csv')

