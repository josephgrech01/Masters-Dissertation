from stable_baselines3 import PPO
from env import sumoMultiLine

for i in range(0, 5):
    print('ITERATION: {}'.format(i))
    e = sumoMultiLine(gui=False, traffic=False, save='singapore/results/sidewalks/tls/normalFreq/ppoWeightedReward/run'+str(i)+'/')

    # model = PPO.load('singapore/models/sidewalks/ppo1800000fypReward')

    model = PPO.load('singapore/models/sidewalks/weightedReward/normalFreq/ppo1750000WeightedRewardTLS')

    obs = e.reset()
    while True:
        action, states = model.predict(obs)
        # print('action: {}'.format(action))
        # print('Action: {}'.format(action))
        obs, reward, done, info = e.step(action)
        if done:
            break
    e.close()