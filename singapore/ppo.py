from stable_baselines3 import PPO
from env import sumoMultiLine
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
e = sumoMultiLine(gui=False)

# model = PPO('MlpPolicy', e, verbose=1, tensorboard_log='singapore/tensorboard/sidewalks/ppoWeightedRewardTLS', device=device)
model = PPO.load('singapore/models/sidewalks/weightedReward/ppo500000WeightedRewardTLS', tensorboard_log='singapore/tensorboard/sidewalks/ppoWeightedRewardTLS', device=device)
model.set_env(e)
model.learn(total_timesteps=250000, log_interval=1, reset_num_timesteps=False)
model.save('singapore/models/sidewalks/weightedReward/ppo750000WeightedRewardTLS')

e.close()