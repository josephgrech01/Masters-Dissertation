from env import sumoMultiLine

for i in range(0,1):
    print('ITERATION: {}'.format(i))
    env = sumoMultiLine(gui=True, save='singapore/results/sidewalks/test/increasedDemand/3by8nc.csv')

    obs = env.reset()
    done = False
    step = 0
    while not done:
        # actions = {agent: 0 for agent in env.agents if agent in env.actionBuses}
        action = 0
        obs, reward, done, info = env.step(action)
        step += 1
        # print('STEP')
        #############################
        # TEST IF ACTION IS APPLIED #
        #############################
    print('DONE')
    print('total22: {}'.format(env.total22)) 
    print('total43: {}'.format(env.total43))
    env.close()
    print(step)
