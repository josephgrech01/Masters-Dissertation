from stable_baselines3 import PPO
from env import sumoMultiLine

for i in range(0, 5):
    print('ITERATION: {}'.format(i))
    e = sumoMultiLine(gui=False, traffic=False, save='singapore/results/skipping/ppo/run'+str(i)+'/')

    model = PPO.load('singapore/models/skipping/nonWeighted/ppo1500000')

    obs = e.reset()
    while True:
        action, states = model.predict(obs)
        # print('Action: {}'.format(action))
        obs, reward, done, info = e.step(action)
        if done:
            break
    e.close()