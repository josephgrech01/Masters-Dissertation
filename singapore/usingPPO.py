from stable_baselines3 import PPO
from env import sumoMultiLine

for i in range(0, 1):
    print('ITERATION: {}'.format(i))
    e = sumoMultiLine(gui=True, traffic=False, save='singapore/results/sidewalks/doubleFreq/ppo')

    model = PPO.load('singapore/models/sidewalks/ppo1800000fypReward')

    obs = e.reset()
    while True:
        action, states = model.predict(obs)
        # print('action: {}'.format(action))
        obs, reward, done, info = e.step(action)
        if done:
            break
    e.close()