from stable_baselines3 import PPO
from env import sumoMultiLine

e = sumoMultiLine(gui=True)

model = PPO.load('singapore/models/sidewalks/ppo500000fypReward')

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print('action: {}'.format(action))
    obs, reward, done, info = e.step(action)
    if done:
        break
e.close()