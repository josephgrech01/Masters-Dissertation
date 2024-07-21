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

e = SumoEnv(gui=False, noWarnings=True, epLen=3000, traffic=False, mixedConfigs=False, bunched=False, save=None, continuous=False, headwayReward=False)
e = ActionMasker(e, mask_fn)

# model = MaskablePPO(MaskableActorCriticPolicy, e, verbose=1, learning_rate=0.001, tensorboard_log="scenario2/tensorboard/maskablePPO/timeReward")

model = MaskablePPO.load('scenario2/models/maskablePPOtimeReward350000', tensorboard_log="scenario2/tensorboard/maskablePPO/timeReward")
model.set_env(e)

model.learn(total_timesteps=100000, log_interval=1, reset_num_timesteps=False)
model.save("scenario2/models/maskablePPOtimeReward450000")

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