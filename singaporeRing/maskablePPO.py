from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

from env import sumoMultiLine

def mask_fn(env):
    return env.valid_action_mask()

e = sumoMultiLine(gui=False, epLen=22000, traffic=False, headwayReward=True, saveState=False, continuous=False, bunched=False, save=None)
e = ActionMasker(e, mask_fn) 

# model = MaskablePPO(MaskableActorCriticPolicy, e, verbose=1, learning_rate=0.001, tensorboard_log="singaporeRing/tensorboard/discrete/timeReward/epLen22000")

model = MaskablePPO.load('singaporeRing/models/discrete/headwayReward1150000', tensorboard_log="singaporeRing/tensorboard/discrete/headwayReward/epLen22000Part4")
model.set_env(e)

model.learn(total_timesteps=50000, log_interval=1, reset_num_timesteps=False)
model.save("singaporeRing/models/discrete/headwayReward1200000")

e.close()