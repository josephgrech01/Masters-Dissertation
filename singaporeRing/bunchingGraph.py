import pickle
import matplotlib.pyplot as plt

with open('singaporeRing/results/continuous/headwayReward/bunchingGraph.pkl', 'rb') as f:
    data = pickle.load(f)

# save = 'singaporeRing/results/graphs/modelC'
save = None

# strategy = 'No Control'
strategy = 'PPO'

graph = 'shared'

fig, ax = plt.subplots()
fig.set_figwidth(10)
labelled = {'Route 22': False, 'Route 43': False}
for k, v in data.items():
    x_values = []
    y_values = []
    for d in v:
        if (k[4:6] == '22' and d[1] > 5 and d[1] < 27) or (k[4:6] == '43' and d[1] > 15 and d[1] < 45):
            x_values.append(d[0]/3600 + 6.5)
            if k[4:6] == '22':
                y_values.append(d[1] - 8)
                c = 'blue'
                label = 'Route 22'
            else:
                y_values.append(d[1] - 22)
                c = 'red'
                label = 'Route 43'

            if len(y_values) > 1 and y_values[-1] < y_values[-2]:
                plt.plot(x_values[:-1], y_values[:-1], color=c, linewidth=1, label=label if not labelled[label] else "")
                labelled[label] = True
                x_values = [x_values[-1]]
                y_values = [y_values[-1]]

    plt.plot(x_values, y_values, color=c, linewidth=1)
ax.set_xlim(8,20)
ax.set_ylim(1,13)
plt.legend(loc=1)
plt.title(strategy + ' - Shared Stops')
plt.xlabel('Time of Day')
plt.ylabel('Bus Stop')
if save is not None:
    plt.savefig(save + 'SharedStopsBunching.eps')
else:
    plt.show()

plt.clf()


graph = '22'

fig, ax = plt.subplots()
fig.set_figwidth(10)
labelled = {'Route 22': False, 'Route 43': False}
for k, v in data.items():
    x_values = []
    y_values = []
    for d in v:
        if graph == '22':
            label = 'Route 22'
            c = 'blue'
            if k[4:6] == '22':
                x_values.append(d[0]/3600 + 6.5)
                y_values.append(d[1])
                
                if len(y_values) > 1 and y_values[-1] < y_values[-2]:
                    plt.plot(x_values[:-1], y_values[:-1], color=c, linewidth=1, label=label if not labelled[label] else "")
                    labelled[label] = True
                    x_values = [x_values[-1]]
                    y_values = [y_values[-1]]
                
                    
        elif graph == '43':
            label = 'Route 43'
            c = 'red'
            if k[4:6] == '43':
                x_values.append(d[0]/3600 + 6.5)
                y_values.append(d[1])
                
                if len(y_values) > 1 and y_values[-1] < y_values[-2]:
                    plt.plot(x_values[:-1], y_values[:-1], color=c, linewidth=1, label=label if not labelled[label] else "")
                    labelled[label] = True
                    x_values = [x_values[-1]]
                    y_values = [y_values[-1]]

    plt.plot(x_values, y_values, color=c, linewidth=1, label=label if not labelled[label] else "")
    labelled[label] = True

ax.set_xlim(8,20)

plt.legend(loc=1)
if graph == '22':
    ax.set_ylim(0,33)
    plt.title(strategy + ' - Route 22')
else:
    ax.set_ylim(0,61)
    plt.title('Route 43 Trajectories - PPO with Weighted Reward')
plt.xlabel('Time of Day')
plt.ylabel('Bus Stop')
if save is not None:
    plt.savefig(save + 'Route22Bunching.eps')
else:
    plt.show()

plt.clf()


graph = '43'
fig, ax = plt.subplots()
fig.set_figwidth(10)
labelled = {'Route 22': False, 'Route 43': False}
for k, v in data.items():
    x_values = []
    y_values = []
    for d in v:
        if graph == '22':
            label = 'Route 22'
            c = 'blue'
            if k[4:6] == '22':
                x_values.append(d[0]/3600 + 6.5)
                y_values.append(d[1])

                if len(y_values) > 1 and y_values[-1] < y_values[-2]:
                    plt.plot(x_values[:-1], y_values[:-1], color=c, linewidth=1, label=label if not labelled[label] else "")
                    labelled[label] = True
                    x_values = [x_values[-1]]
                    y_values = [y_values[-1]]
                
                    
        elif graph == '43':
            label = 'Route 43'
            c = 'red'
            if k[4:6] == '43':
                x_values.append(d[0]/3600 + 6.5)
                y_values.append(d[1])

                if len(y_values) > 1 and y_values[-1] < y_values[-2]:
                    plt.plot(x_values[:-1], y_values[:-1], color=c, linewidth=1, label=label if not labelled[label] else "")
                    labelled[label] = True
                    x_values = [x_values[-1]]
                    y_values = [y_values[-1]]

    plt.plot(x_values, y_values, color=c, linewidth=1, label=label if not labelled[label] else "")
    labelled[label] = True

ax.set_xlim(8,20)

plt.legend(loc=1)
if graph == '22':
    ax.set_ylim(0,33)
    plt.title('Route 22 Trajectories - PPO with Weighted Reward')
else:
    ax.set_ylim(0,61)
    plt.title(strategy + ' - Route 43')
plt.xlabel('Time of Day')
plt.ylabel('Bus Stop')
if save is not None:
    plt.savefig(save + 'Route43Bunching.eps')
else:
    plt.show()
plt.clf()


    