from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from env import SumoEnv

def mask_fn(env):
    return env.valid_action_mask()

actions = ['Hold', 'Skip', 'Proceed']
e = SumoEnv(gui=True, noWarnings=True, epLen=750, traffic=False, bunched=True, save='wang2020/results/maskablePPO/updatedHeadwaysDur15/bunched/2')
e = ActionMasker(e, mask_fn)
# no traffic
# model = PPO.load("models/ppoNoTraffic")

# traffic
model=MaskablePPO.load("wang2020/models/maskablePPOupdatedHeadways200000dur15")
# model=MaskablePPO.load("wang2020/models/maskablePPOmixedConfigs500000")

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print("action: ", actions[action])
    obs, reward, done, info = e.step(action)
    if done:
        break

e.close()