import pickle
import matplotlib.pyplot as plt

with open('scenario3/results/continuous/timeReward/noTraffic/route1.pkl', 'rb') as f:
    route1 = pickle.load(f)
with open('scenario3/results/continuous/timeReward/noTraffic/route2.pkl', 'rb') as f:
    route2 = pickle.load(f)
with open('scenario3/results/continuous/timeReward/noTraffic/route3.pkl', 'rb') as f:
    route3 = pickle.load(f)

strategy = 'PPO'
bunched = False

save = 'scenario3/results/graphs/continuous/timeReward/'
# save = None

for y in range(0, 6):
    for z in route1[y]:
        x_values = []
        y_values = []

        for i in z:
            x_values.append((i[0]*9)/60)
            y_values.append(i[1])

        plt.plot(x_values, y_values, color='maroon')
plt.yticks(range(1,13))
if not bunched:
    plt.title(strategy + ' - Route 1')
else:
    plt.title(strategy + ' - Route 1, Already Bunched')
plt.xlabel('Time (mins)')
plt.ylabel('Bus Stop')
# plt.legend(loc=4)
if save is not None:
    plt.savefig(save + 'route1Bunching.jpg')
else:
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
if not bunched:
    plt.title(strategy + ' - Route 2')
else:
    plt.title(strategy + ' - Route 2, Already Bunched')
plt.xlabel('Time (mins)')
plt.ylabel('Bus Stop')
# plt.legend(loc=4)
if save is not None:
    plt.savefig(save + 'route2Bunching.jpg')
else:
    plt.show()
plt.clf()



for y in range(0, 6):
    for z in route3[y]:
        x_values = []
        y_values = []

        for i in z:
            x_values.append((i[0]*9)/60)
            y_values.append(i[1])

        plt.plot(x_values, y_values, color='darkGreen')

plt.yticks(range(1,13))
if not bunched:
    plt.title(strategy + ' - Route 3')
else:
    plt.title(strategy + ' - Route 3, Already Bunched')
plt.xlabel('Time (mins)')
plt.ylabel('Bus Stop')
# plt.legend(loc=4)
if save is not None:
    plt.savefig(save + 'route3Bunching.jpg')
else:
    plt.show()
plt.clf()


labelled = [False, False, False]
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

    for z in route3[y]:
        x_values = []
        y_values = []

        for i in z:
            if i[1] > 9:
                x_values.append((i[0]*9)/60)
                y_values.append(i[1]-9)

        if not labelled[2]:
            plt.plot(x_values, y_values, color='darkGreen', label='Route 3', linewidth=1)
            labelled[2] = True
        else:
            plt.plot(x_values, y_values, color='darkGreen', linewidth=1)

plt.yticks(range(1,4))
if not bunched:
    plt.title(strategy + ' - Shared Stops')
else:
    plt.title(strategy + ' - Shared Stops, Already Bunched')
plt.xlabel('Time (mins)')
plt.ylabel('Bus Stop')
plt.legend(loc=4)
if save is not None:
    plt.savefig(save + 'sharedStopsBunching.jpg')
else:
    plt.show()
plt.clf()



        