from stable_baselines3 import PPO
from env import SumoEnv


e = SumoEnv(gui=True, noWarnings=True, epLen=750, traffic=True, bunched=False, continuous=True, save='wang2020/results/continuous/headwayReward/traffic90/')

# model = PPO.load('singapore/models/sidewalks/ppo1800000fypReward')

# model = PPO.load('singapore/models/sidewalks/weightedReward/normalFreq/ppo1750000WeightedRewardTLS')

model = PPO.load('wang2020/models/continuous/headwayReward150000')

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print('Action: {}'.format(action*90))
    obs, reward, done, info = e.step(action)
    if done:
        break
e.close()