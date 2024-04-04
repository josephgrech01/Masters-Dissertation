import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('results/test/rates3by10num1.csv')

rates = df['rate'].tolist()

fig, ax1 = plt.subplots(1,1)
plt.boxplot(rates)
plt.savefig('results/test/boxplot3by10.jpg')
plt.show()