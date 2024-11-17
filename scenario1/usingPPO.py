from stable_baselines3 import PPO
from env import SumoEnv


e = SumoEnv(gui=True, noWarnings=True, epLen=750, traffic=True, bunched=False, continuous=True, save=None)#'scenario1/results/continuous/timeReward/traffic90/')

model = PPO.load('scenario1/models/continuous/timeReward200000')

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print('Action: {}'.format(action*90))
    obs, reward, done, info = e.step(action)
    if done:
        break
e.close()