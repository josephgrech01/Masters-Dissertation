import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

metrics = ['mean', 'median', 'sd']
sections = ['All', 'Shared', 'Unshared']

control = 'ppo'

if control == 'nc':
    c = 'No Control'
if control == 'ppo':
    c = 'PPO'
if control == 'ppoWeightedReward':
    c = 'PPO with Weighted Reward'

for i_m, m in enumerate(metrics):
    for i_s, s in enumerate(sections):
        l = []
        save = 'singapore/results/skipping/'+control+'/graphs/'+metrics[i_m]+'/'
        if i_m == 0:
            metric = 'Mean'
        if i_m == 1:
            metric = 'Median'
        if i_m == 2:
            metric = 'Standard Deviation'
        for i in range(0,5):
            log = pd.read_csv('singapore/results/skipping/'+control+'/run'+str(i)+'/'+sections[i_s]+'.csv')
            # log = pd.read_csv('singapore/results/sidewalks/averages/ppo/run'+str(i)+'/all.csv')
            # log = pd.read_csv('singapore/results/sidewalks/test/traffic/nc.csv')

            time = log['time'].tolist()
            median = log[metrics[i_m]].tolist()

            a = 600
            b = 4000

            fig, ax1 = plt.subplots(1, 1)
            ax1.set_xbound(6,23)
            ax1.set_title(metric+' Waiting Time ('+sections[i_s]+' Stops) - '+c)
            ax1.set_xlabel('Time of day')
            ax1.set_ylabel(metric+' Waiting Time')
            ax1.plot([(t/3600) + 6.5 for t in time][a:b], median[a:b], linewidth=0.8)
            ax1.grid()
            # plt.savefig(save+'run'+str(i)+'all.jpg')
            plt.savefig(save+'run'+str(i)+metrics[i_m]+sections[i_s]+'.jpg')
            # plt.show()
            # plt.clf()

            average = sum(median[a:b])/len(median[a:b])
            l.append(average)
        # print('Average: {}'.format(sum(meanWaitTime[a:b])/len(meanWaitTime[a:b])))

        l.append(sum(l)/len(l))

        dict = {'means':l}
        df = pd.DataFrame(dict)
        df.to_csv(save+metrics[i_m]+sections[i_s]+'.csv')

