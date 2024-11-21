from stable_baselines3 import PPO
from env import sumoMultiLine

e = sumoMultiLine(gui=False, noWarnings=True, epLen=50000, traffic=False, bunched=False, continuous=True, headwayReward=True, saveState=False, save='singaporeRing/results/newTests/continuous/headwayReward/')

model = PPO.load('singaporeRing/models/continuous/headwayReward900000')

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print('Action: {}'.format(action*60))
    obs, reward, done, info = e.step(action)
    if done:
        break
e.close()