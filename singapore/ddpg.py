import gymnasium as gym
from stable_baselines3 import DDPG
from env import sumoMultiLine

e = sumoMultiLine()

model = DDPG('MultiInputPolicy', e, verbose=1)
model.set_env(e) #?????
# model.learn(total_timesteps=6, log_interval=10) ############# calculate total_timesteps
# model.save('models/ddpg')



e.close()

