from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from envRemote import sumoMultiLine

def mask_fn(env):
    # print('masking')
    return env.valid_action_mask()

actions = ['Hold', 'Skip', 'Proceed']
e = sumoMultiLine(gui=False, noWarnings=True, epLen=50000, traffic=False, bunched=False, headwayReward=False, continuous=False, saveState=False, save='singaporeRing/results/newTests/discrete/timeReward/')
e = ActionMasker(e, mask_fn)
# no traffic
# model = PPO.load("models/ppoNoTraffic")

# traffic
model=MaskablePPO.load("singaporeRing/models/discrete/timeReward1500000")
# model=MaskablePPO.load("singaporeRing/models/discrete/epLen50000headwayReward150000")


obs = e.reset()
while True:
    action, states = model.predict(obs)#, action_masks=mask_fn(e))
    print("action: ", actions[action])
    obs, reward, done, info = e.step(action)
    if done:
        break

e.close()