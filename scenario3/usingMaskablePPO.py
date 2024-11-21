from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from env import SumoEnv

def mask_fn(env):
    return env.valid_action_mask()

actions = ['Hold', 'Skip', 'Proceed']
e = SumoEnv(gui=True, noWarnings=True, epLen=3000, traffic=True, bunched=False, continuous=False, headwayReward=False, save=None)#'scenario3/results/discrete/timeReward/traffic90/')
e = ActionMasker(e, mask_fn)

model=MaskablePPO.load("scenario3/models/maskablePPOtimeReward450000")

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print("action: ", actions[action])
    obs, reward, done, info = e.step(action)
    if done:
        break

e.close()