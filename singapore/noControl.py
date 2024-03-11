from env import sumoMultiLine

env = sumoMultiLine(gui=True)

obs = env.reset()
done = False

while not done:
    actions = {agent: 0 for agent in env.agents if agent in env.actionBuses}
    obs, rewards, done = env.step(actions)
    print('STEP')
    #############################
    # TEST IF ACTION IS APPLIED #
    #############################
print('DONE')
env.close()
