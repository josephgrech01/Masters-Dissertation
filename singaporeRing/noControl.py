from env import sumoMultiLine

for i in range(0,1):
    print('ITERATION: {}'.format(i))
    env = sumoMultiLine(gui=True, traffic=False, saveState=False, epLen=50000, continuous=False, save=None)#'singaporeRing/results/noControl/noTraffic/50000')#'singapore/results/skipping/nc/run'+str(i)+'/')

    obs = env.reset()
    done = False
    step = 0
    while not done:
        # actions = {agent: 0 for agent in env.agents if agent in env.action Buses}
        action = 2
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
