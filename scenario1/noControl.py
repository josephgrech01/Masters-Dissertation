from env import SumoEnv

env = SumoEnv(gui=True, noWarnings=True, epLen=750, traffic=True, bunched=False, save=None)#'scenario1/results/noControl/traffic90')

episodes = 1
for episode in range(1, episodes + 1):

    state = env.reset()

    done = False

    while not done:
        state, reward, done, info = env.step(2) # bus proceeds normally, hence action == 2

env.close()