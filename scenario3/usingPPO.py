from stable_baselines3 import PPO
from env import SumoEnv


e = SumoEnv(gui=True, noWarnings=True, epLen=3000, traffic=True, bunched=False, continuous=True, headwayReward=False, save='scenario3/results/continuous/timeReward/traffic90/')

# model = PPO.load('singapore/models/sidewalks/ppo1800000fypReward')

# model = PPO.load('singapore/models/sidewalks/weightedReward/normalFreq/ppo1750000WeightedRewardTLS')

model = PPO.load('scenario3/models/continuous/timeReward450000')

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print('Action: {}'.format(action*90))
    obs, reward, done, info = e.step(action)
    if done:
        break
e.close()