import pickle
import matplotlib.pyplot as plt

with open('singapore/results/sidewalks/tls/normalFreq/nc/bunchingGraph.pkl', 'rb') as f:
    data = pickle.load(f)

print(data)

fig, ax = plt.subplots()
for k, v in data.items():
    x_values = []
    y_values = []
    for d in v:
        # if (k[4:6] == '22' and d[1] > 8 and d[1] < 22) or (k[4:6] == '43' and d[1] > 22 and d[1] < 36):
        if (k[4:6] == '22' and d[1] > 5 and d[1] < 27) or (k[4:6] == '43' and d[1] > 15 and d[1] < 45):
            x_values.append(d[0]/3600 + 6.5)
            if k[4:6] == '22':
                y_values.append(d[1] - 8)
                c = 'blue'
            else:
                y_values.append(d[1] - 22)
                c = 'red'

            # y_values.append(d[1])

    plt.plot(x_values, y_values, color=c, linewidth=1)
ax.set_xlim(8,17)
ax.set_ylim(1,13)
plt.show()


    