from sb3_contrib.ppo_mask import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from env import SumoEnv

def mask_fn(env):
    return env.valid_action_mask()

actions = ['Hold', 'Skip', 'Proceed']
e = SumoEnv(gui=True, noWarnings=True, epLen=3000, traffic=True, bunched=False, continuous=False, headwayReward=False, save=None)#'scenario2/results/discrete/timeReward/traffic90/')
e = ActionMasker(e, mask_fn)
# no traffic
# model = PPO.load("models/ppoNoTraffic")

# traffic
# model=MaskablePPO.load("scenario1/models/maskablePPOupdatedHeadways200000dur15")
model=MaskablePPO.load("scenario2/models/maskablePPOtimeReward450000")
# model=MaskablePPO.load("scenario1/models/maskablePPOmixedConfigs500000")

obs = e.reset()
while True:
    action, states = model.predict(obs)
    print("action: ", actions[action])
    obs, reward, done, info = e.step(action)
    if done:
        break

e.close()