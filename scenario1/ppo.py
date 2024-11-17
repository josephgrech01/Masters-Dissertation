from stable_baselines3 import PPO

from env import SumoEnv

e = SumoEnv(gui=False, noWarnings=True, epLen=250, traffic=False, mixedConfigs=False, bunched=False, save=None, continuous=True)

# model = PPO("MlpPolicy", e, verbose=1, learning_rate=0.001, tensorboard_log="wang2020/tensorboard/continuous/timeReward/")

model = PPO.load('wang2020/models/continuous/timeReward150000', tensorboard_log="wang2020/tensorboard/continuous/timeReward/")
model.set_env(e)


model.learn(total_timesteps=50000, log_interval=1, reset_num_timesteps=False)
model.save("wang2020/models/continuous/timeReward200000")

e.close()