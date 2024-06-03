import pandas as pd

log = pd.read_csv('singapore/results/skipping/ppo/run4/Unshared.csv')

mins = log['min'].tolist()
maxs = log['max'].tolist()

minOverall = min(mins[600:4000])
maxOverall = max(maxs[600:4000])

print('Min: {}'.format(minOverall))
print('Max: {}'.format(maxOverall))