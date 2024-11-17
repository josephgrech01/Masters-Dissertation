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

e = SumoEnv(gui=False, noWarnings=True, epLen=250, traffic=False, mixedConfigs=False, bunched=False, save=None, continuous=False)
e = ActionMasker(e, mask_fn)
# model = MaskablePPO(MaskableActorCriticPolicy, e, verbose=1, n_steps=2778, gamma=0.93011, learning_rate=0.000012779, tensorboard_log="wang2020/tensorboard/maskablePPO/tuned/headwayReward")

model = MaskablePPO(MaskableActorCriticPolicy, e, verbose=1, learning_rate=0.001, tensorboard_log="wang2020/tensorboard/maskablePPO/tuned/headwayReward2")


# model = MaskablePPO.load('wang2020/models/maskablePPOtimeReward250000', tensorboard_log="wang2020/tensorboard/maskablePPO/MaxTimeReward")
# model.set_env(e)
model.learn(total_timesteps=150000, log_interval=1, reset_num_timesteps=False)
model.save("wang2020/models/tuned/maskablePPOheadwayReward")

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