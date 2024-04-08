from stable_baselines3 import DDPG
from env import sumoMultiLine
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise

e = sumoMultiLine(gui=False)
# model = DDPG('MultiInputPolicy', e, verbose=1)
model = DDPG('MultiInputPolicy', e, verbose=1, tensorboard_log='singapore/tensorboard/ddpg100000')
# model.set_env(e) #?????
model.learn(total_timesteps=100000, log_interval=1) ############# calculate total_timesteps
model.save('singapore/models/ddpg100000')

print("EPISODE: {}".format(e.episodes))


e.close()

