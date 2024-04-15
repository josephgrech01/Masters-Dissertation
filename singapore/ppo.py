from stable_baselines3 import PPO
from env import sumoMultiLine
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
e = sumoMultiLine(gui=False)

# model = PPO('MlpPolicy', e, verbose=1, tensorboard_log='singapore/tensorboard/sidewalks/ppo1000000fypReward', device=device)
model = PPO.load('ppo500000fypReward', tensorboard_log='singapore/tensorboard/sidewalks/ppo500000fypReward')
model.learn(total_timesteps=500000, log_interval=1)
model.save('singapore/models/sidewalks/ppo1000000fypReward')

e.close()