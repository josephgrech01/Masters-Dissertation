from stable_baselines3 import PPO
from env import sumoMultiLine

for i in range(0, 4):
    print('ITERATION: {}'.format(i))
    e = sumoMultiLine(gui=False, traffic=False, save='singapore/results/sidewalks/tls/ppo/run'+str(i+1)+'/')

    model = PPO.load('singapore/models/sidewalks/ppo1800000fypReward')

    # model = PPO.load('singapore/models/sidewalks/weightedReward/ppo500000WeightedRewardTLS')

    obs = e.reset()
    while True:
        action, states = model.predict(obs)
        # print('action: {}'.format(action))
        print('Action: {}'.format(action))
        obs, reward, done, info = e.step(action)
        if done:
            break
    e.close()