from env import sumoMultiLine

for i in range(0,1):
    print('ITERATION: {}'.format(i))
    env = sumoMultiLine(gui=True, traffic=False, saveState=False, epLen=50000, continuous=False, save=None)#'singaporeRing/results/noControl/noTraffic/50000')#'singapore/results/skipping/nc/run'+str(i)+'/')

    obs = env.reset()
    done = False
    step = 0
    while not done:
        action = 2
        obs, reward, done, info = env.step(action)
        step += 1

    env.close()
