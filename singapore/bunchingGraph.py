import pickle
import matplotlib.pyplot as plt

with open('singapore/results/skipping/nc/bunchingGraphNC.pkl', 'rb') as f:
    data = pickle.load(f)

graph = 'shared'

if graph == 'shared':
    fig, ax = plt.subplots()
    fig.set_figwidth(10)
    labelled = {'Route 22': False, 'Route 43': False}
    for k, v in data.items():
        x_values = []
        y_values = []
        for d in v:
            # if (k[4:6] == '22' and d[1] > 8 and d[1] < 22) or (k[4:6] == '43' and d[1] > 22 and d[1] < 36): # original limits
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

                # y_values.append(d[1])
        if not labelled[label]:
            plt.plot(x_values, y_values, color=c, linewidth=1, label=label)
            labelled[label] = True
        else:
            plt.plot(x_values, y_values, color=c, linewidth=1)
    ax.set_xlim(8,20)
    ax.set_ylim(1,13)
    plt.legend(loc=1)
    plt.title('Shared Corridor Trajectories - No Control')
    plt.xlabel('Time of Day')
    plt.ylabel('Stop along Shared Corridor')
    plt.savefig('singapore/results/skipping/nc/graphs/BunchingShared.jpg')
    plt.show()

else:
    fig, ax = plt.subplots()
    fig.set_figwidth(10)
    labelled = {'Route 22': False, 'Route 43': False}
    for k, v in data.items():
        x_values = []
        y_values = []
        for d in v:
            # if (k[4:6] == '22' and d[1] > 8 and d[1] < 22) or (k[4:6] == '43' and d[1] > 22 and d[1] < 36): # original limits
            if graph == '22':
                label = 'Route 22'
                c = 'blue'
                if k[4:6] == '22':
                    x_values.append(d[0]/3600 + 6.5)
                    y_values.append(d[1])
                    # c = 'blue'
                    # label = 'Route 22'
                    
                        
            elif graph == '43':
                label = 'Route 43'
                c = 'red'
                if k[4:6] == '43':
                    x_values.append(d[0]/3600 + 6.5)
                    y_values.append(d[1])
                    # c = 'red'
                    # label = 'Route 43'

        if not labelled[label]:
            plt.plot(x_values, y_values, color=c, linewidth=1, label=label)
            labelled[label] = True
        else:
            plt.plot(x_values, y_values, color=c, linewidth=1)
    ax.set_xlim(8,20)
    
    plt.legend(loc=1)
    if graph == '22':
        ax.set_ylim(0,33)
        plt.title('Route 22 Trajectories - PPO with Weighted Reward')
    else:
        ax.set_ylim(0,61)
        plt.title('Route 43 Trajectories - PPO with Weighted Reward')
    plt.xlabel('Time of Day')
    plt.ylabel('Stop along Route')
    # plt.savefig('singapore/results/Route22Bunching.jpg')
    plt.show()


    