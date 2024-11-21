from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from env import sumoMultiLine

def mask_fn(env):
    return env.valid_action_mask()

actions = ['Hold', 'Skip', 'Proceed']
e = sumoMultiLine(gui=True, noWarnings=True, epLen=50000, traffic=False, bunched=False, headwayReward=False, continuous=False, saveState=False, save='singaporeRing/results/discrete/timeReward/noTraffic/50000Mask')
e = ActionMasker(e, mask_fn)

model=MaskablePPO.load("singaporeRing/models/discrete/timeReward1400000")

obs = e.reset()
while True:
    action, states = model.predict(obs, action_masks=mask_fn(e))
    print("action: ", actions[action])
    obs, reward, done, info = e.step(action)
    if done:
        break

e.close()