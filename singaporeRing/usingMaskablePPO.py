from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from env import sumoMultiLine

def mask_fn(env):
    return env.valid_action_mask()

actions = ['Hold', 'Skip', 'Proceed']
e = sumoMultiLine(gui=True, noWarnings=True, epLen=52000, traffic=False, bunched=False, headwayReward=True, continuous=False, saveState=False, save='singaporeRing/results/discrete/headwayReward/noTraffic/1minHolding/shortEpLen')
e = ActionMasker(e, mask_fn)
# no traffic
# model = PPO.load("models/ppoNoTraffic")

# traffic
model=MaskablePPO.load("singaporeRing/models/discrete/headwayReward150000")
# model=MaskablePPO.load("singaporeRing/models/discrete/epLen50000headwayReward150000")


obs = e.reset()
while True:
    action, states = model.predict(obs)
    print("action: ", actions[action])
    obs, reward, done, info = e.step(action)
    if done:
        break

e.close()