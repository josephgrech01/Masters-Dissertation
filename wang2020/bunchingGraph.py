import pickle
import matplotlib.pyplot as plt

with open('wang2020/results/maskablePPO/2route1.pkl', 'rb') as f:
    route1 = pickle.load(f)
with open('wang2020/results/maskablePPO/2route2.pkl', 'rb') as f:
    route2 = pickle.load(f)

strategy = 'PPO'
save = 'wang2020/results/graphs/PPO/'

for y in range(0, 6):
    for z in route1[y]:
        x_values = []
        y_values = []

        for i in z:
            x_values.append((i[0]*9)/60)
            y_values.append(i[1])

        plt.plot(x_values, y_values, color='maroon')
plt.yticks(range(1,13))
plt.title(strategy + ' - Route 1')
plt.xlabel('Time (mins')
plt.ylabel('Bus Stop')
# plt.legend(loc=4)
plt.savefig(save + 'route1Bunching.jpg')
plt.show()
plt.clf()



for y in range(0, 6):
    for z in route2[y]:
        x_values = []
        y_values = []

        for i in z:
            x_values.append((i[0]*9)/60)
            y_values.append(i[1])

        plt.plot(x_values, y_values, color='blue')

plt.yticks(range(1,13))
plt.title(strategy + ' - Route 2')
plt.xlabel('Time (mins')
plt.ylabel('Bus Stop')
# plt.legend(loc=4)
plt.savefig(save + 'route2Bunching.jpg')
plt.show()
plt.clf()


labelled = [False, False]
for y in range(0, 6):
    for z in route1[y]:
        x_values = []
        y_values = []

        for i in z:
            if i[1] > 9:
                x_values.append((i[0]*9)/60)
                y_values.append(i[1]-9)

        if not labelled[0]:
            plt.plot(x_values, y_values, color='maroon', label='Route 1', linewidth=1)
            labelled[0] = True
        else:
            plt.plot(x_values, y_values, color='maroon', linewidth=1)

    for z in route2[y]:
        x_values = []
        y_values = []

        for i in z:
            if i[1] > 9:
                x_values.append((i[0]*9)/60)
                y_values.append(i[1]-9)

        if not labelled[1]:
            plt.plot(x_values, y_values, color='blue', label='Route 2', linewidth=1)
            labelled[1] = True
        else:
            plt.plot(x_values, y_values, color='blue', linewidth=1)

plt.yticks(range(1,4))
plt.title(strategy + ' - Shared Stops')
plt.xlabel('Time (mins)')
plt.ylabel('Bus Stop')
plt.legend(loc=4)
plt.savefig(save + 'sharedStopsBunching.jpg')
plt.show()
plt.clf()



        