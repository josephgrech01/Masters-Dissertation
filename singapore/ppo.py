from stable_baselines3 import PPO
from env import sumoMultiLine

e = sumoMultiLine(gui=False)

model = PPO('MlpPolicy', e, verbose=1, tensorboard_log='singapore/tensorboard/ppo100000')

model.learn(total_timesteps=100000, log_interval=1)
model.save('singapore/models/ppo100000')

e.close()