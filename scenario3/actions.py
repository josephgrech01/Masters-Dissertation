import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

ppo1 = pd.read_csv('scenario3/results/discrete/headwayReward/traffic29/log.csv')
ppo2 = pd.read_csv('scenario3/results/discrete/timeReward/traffic29/log.csv')
ppo3 = pd.read_csv('scenario3/results/continuous/headwayReward/traffic29/log.csv')
ppo4 = pd.read_csv('scenario3/results/continuous/timeReward/traffic29/log.csv')

action1 = ppo1['action']
action2 = ppo2['action']
action3 = ppo3['action']
action4 = ppo4['action']

save = None
# save = 'scenario3/results/graphs/'

percentages = [{},{}]

for index, ppo in enumerate([ppo1, ppo2]):
    total_actions = len(ppo['action'])
    holding_count = ppo['action'].tolist().count('Hold')
    skipping_count = ppo['action'].tolist().count('Skip')
    proceed_count = ppo['action'].tolist().count('No action')

    hold = (holding_count / total_actions) * 100
    skip = (skipping_count / total_actions) * 100
    proceed = (proceed_count / total_actions) * 100

    percentages[index] = {'hold': hold, 'skip': skip, 'proceed': proceed}

x = ['Model A', 'Model B']

actions = {'Hold': [percentages[0]['hold'], percentages[1]['hold']], 'Skip': [percentages[0]['skip'], percentages[1]['skip']], 'Proceed': [percentages[0]['proceed'], percentages[1]['proceed']]}

fig, ax = plt.subplots()
bottom = np.zeros(2)

bar_width = 0.45

for a, action in actions.items():
    p = ax.bar(x, action, label=a, bottom=bottom, width=bar_width, edgecolor='black')
    bottom += action
    # ac = [str(round(x, 1))+'%' if x != 0 else '' for x in action]
    # ax.bar_label(p, label_type='center')#, labels=ac)

ax.set_title('Distribution of Actions')
ax.legend(loc=4)

ax.set_xlim([-0.45, 1.45])

ax.set_ylabel('Percentage')

if save is not None:
    plt.savefig(save + 'discreteActions.eps')
else:
    plt.show()
plt.clf()

#########################################

model_c = [float(x[1:-2]) * 60 for x in action3.tolist()]
model_d = [float(x[1:-2]) * 60 for x in action4.tolist()]

data = model_c + model_d
models = ['Model C'] * len(model_c) + ['Model D'] * len(model_d)

df = pd.DataFrame({
    'Holding Time (Seconds)': model_c + model_d,
    'Model': ['Model C'] * len(model_c) + ['Model D'] * len(model_d)
})

sns.histplot(data=df, x='Holding Time (Seconds)', bins=6, shrink=0.8, hue='Model', multiple='dodge', edgecolor='black', stat='percent')

bins = np.arange(0, 70, 10)
bin_ranges = [f'{int(bins[i])}-{int(bins[i+1])}' for i in range(len(bins)-1)]

plt.xticks(ticks=bins[:-1] + (bins[1] - bins[0])/2, labels=bin_ranges)

# update the y-axis to double the tick values for each tickS
current_yticks = plt.gca().get_yticks()
plt.gca().set_yticklabels([f'{int(tick * 2)}' for tick in current_yticks])


plt.title('Distribution of Holding Times (Percentage)')
if save is not None:
    plt.savefig(save + 'continuousActions.eps')
else:
    plt.show()
plt.clf()




