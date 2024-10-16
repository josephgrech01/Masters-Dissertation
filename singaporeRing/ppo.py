from stable_baselines3 import PPO

from env import sumoMultiLine

e = sumoMultiLine(gui=False, saveState=False, noWarnings=True, epLen=22000, traffic=False, bunched=False, save=None, continuous=True, headwayReward=True)

# model = PPO("MlpPolicy", e, verbose=1, learning_rate=0.001, tensorboard_log="singaporeRing/tensorboard/continuous/headwayReward/eplen22000New")

model = PPO.load('singaporeRing/models/continuous/headwayReward400000', tensorboard_log="singaporeRing/tensorboard/continuous/headwayReward/eplen22000New")
model.set_env(e)

model.learn(total_timesteps=50000, log_interval=1, reset_num_timesteps=False)
model.save("singaporeRing/models/continuous/headwayReward450000")

e.close()