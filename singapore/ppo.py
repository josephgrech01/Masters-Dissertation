from stable_baselines3 import PPO
from env import sumoMultiLine
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
e = sumoMultiLine(gui=False)

# model = PPO('MlpPolicy', e, verbose=1, tensorboard_log='singapore/tensorboard/skipping/nonWeighted/ppo/', device=device)
model = PPO.load('singapore/models/skipping/nonWeighted/ppo1100000', tensorboard_log='singapore/tensorboard/skipping/nonWeighted/ppo/', device=device)
model.set_env(e)
model.learn(total_timesteps=400000, log_interval=1, reset_num_timesteps=False)
model.save('singapore/models/skipping/nonWeighted/ppo1500000')

e.close()