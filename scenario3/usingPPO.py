from stable_baselines3 import PPO
from env import SumoEnv


e = SumoEnv(gui=True, noWarnings=True, epLen=3000, traffic=True, bunched=False, continuous=True, headwayReward=False, save=None)#'scenario3/results/continuous/timeReward/traffic90/')

model = PPO.load('scenario3/models/continuous/timeReward550000_2')

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print('Action: {}'.format(action*90))
    obs, reward, done, info = e.step(action)
    if done:
        break
e.close()