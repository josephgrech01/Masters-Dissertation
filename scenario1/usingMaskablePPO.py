from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from env import SumoEnv

def mask_fn(env):
    print('MASK_FN')
    return env.valid_action_mask()

actions = ['Hold', 'Skip', 'Proceed']
e = SumoEnv(gui=True, noWarnings=True, epLen=750, traffic=True, bunched=False, save=None)#'scenario1/results/maskablePPO/timeReward/traffic90/')
e = ActionMasker(e, mask_fn)


# traffic
# model=MaskablePPO.load("scenario1/models/discrete/headwayReward")
model=MaskablePPO.load("scenario1/models/discrete/timeReward")


obs = e.reset()
while True:
    action, states = model.predict(obs)
    print("action: ", actions[action])
    obs, reward, done, info = e.step(action)
    if done:
        break

e.close()