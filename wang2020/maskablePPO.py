from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

from env import SumoEnv

###################################################################
#                                                                 #
#                                                                 #
#                                                                 #
#       MUST READAPT MODEL STATE OBSERVATION HIGH AND LOW         #
#                                                                 #
#                                                                 #
#                                                                 #
###################################################################

def mask_fn(env):
    return env.valid_action_mask()

e = SumoEnv(gui=False, noWarnings=True, epLen=250, traffic=False, mixedConfigs=False, bunched=False, save=None)
e = ActionMasker(e, mask_fn)
# model = MaskablePPO(MaskableActorCriticPolicy, e, verbose=1, learning_rate=0.001, tensorboard_log="wang2020/tensorboard/maskablePPO/MaxTimeReward")
model = MaskablePPO.load('wang2020/models/maskablePPOtimeReward250000', tensorboard_log="wang2020/tensorboard/maskablePPO/MaxTimeReward")
model.set_env(e)
model.learn(total_timesteps=25000, log_interval=1, reset_num_timesteps=False)
model.save("wang2020/models/maskablePPOtimeReward275000")

e.close()


###################################################################
#                                                                 #
#                                                                 #
#                                                                 #
#       MUST READAPT MODEL STATE OBSERVATION HIGH AND LOW         #
#                                                                 #
#                                                                 #
#                                                                 #
###################################################################