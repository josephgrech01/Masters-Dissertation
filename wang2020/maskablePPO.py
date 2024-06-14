from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

from env import SumoEnv

def mask_fn(env):
    return env.valid_action_mask()

e = SumoEnv(gui=False, noWarnings=True, epLen=250, traffic=0, mixedConfigs=False, bunched=False)
e = ActionMasker(e, mask_fn)
model = MaskablePPO(MaskableActorCriticPolicy, e, verbose=1, learning_rate=0.001, tensorboard_log="wang2020/tensorboard/maskablePPO")

model.learn(total_timesteps=250000, log_interval=1)
model.save("wang2020/models/maskablePPO")

e.close()