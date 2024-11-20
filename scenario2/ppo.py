from stable_baselines3 import PPO

from env import SumoEnv

e = SumoEnv(gui=False, noWarnings=True, epLen=3000, traffic=False, mixedConfigs=False, bunched=False, save=None, continuous=True, headwayReward=False)

# model = PPO("MlpPolicy", e, verbose=1, learning_rate=0.001, tensorboard_log="scenario2/tensorboard/continuous/timeReward/")

model = PPO.load('scenario2/models/continuous/timeReward300000', tensorboard_log="scenario2/tensorboard/continuous/timeReward/")
model.set_env(e)

model.learn(total_timesteps=150000, log_interval=1, reset_num_timesteps=False)
model.save("scenario2/models/continuous/timeReward450000")

e.close()