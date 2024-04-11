from stable_baselines3 import PPO
from env import sumoMultiLine

e = sumoMultiLine(gui=False)

model = PPO('MlpPolicy', e, verbose=1, tensorboard_log='singapore/tensorboard/sidewalks/ppo2500000tempReward')

model.learn(total_timesteps=200000, log_interval=1)
model.save('singapore/models/ppo200000tempReward')

e.close()