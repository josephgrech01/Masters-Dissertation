from env import sumoMultiLine

for i in range(0,1):
    print('ITERATION: {}'.format(i))
    env = sumoMultiLine(gui=True, traffic=False, save=None)#'singapore/results/'+str(i)+'/')

    obs = env.reset()
    done = False
    step = 0
    while not done:
        action = 0
        obs, reward, done, info = env.step(action)
        step += 1
    env.close()