from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

from env import SumoEnv

def mask_fn(env):
    return env.valid_action_mask()

e = SumoEnv(gui=False, noWarnings=True, epLen=250, traffic=False, mixedConfigs=False, bunched=False, save=None, continuous=False)
e = ActionMasker(e, mask_fn)

model = MaskablePPO(MaskableActorCriticPolicy, e, verbose=1, learning_rate=0.001, tensorboard_log="scenario1/tensorboard/maskablePPO/tuned/headwayReward2")

# model = MaskablePPO.load('scenario1/models/maskablePPOtimeReward250000', tensorboard_log="scenario1/tensorboard/maskablePPO/MaxTimeReward")
# model.set_env(e)
model.learn(total_timesteps=150000, log_interval=1, reset_num_timesteps=False)
model.save("scenario1/models/tuned/maskablePPOheadwayReward")

e.close()
