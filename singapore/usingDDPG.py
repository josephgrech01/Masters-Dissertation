from stable_baselines3 import DDPG
from env import sumoMultiLine

e = sumoMultiLine(gui=True)

model = DDPG.load('singapore/models/ddpg100000')

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print('Action: {}'.format(action))
    obs, reward, done, info = e.step(action)
    print('reward: {}'.format(reward))
    if done:
        break

e.close()
