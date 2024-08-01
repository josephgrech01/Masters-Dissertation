import gym
from gym.spaces import Discrete, Box
import os
import sys
import numpy as np
import math
import pandas as pd
import random
from datetime import datetime
import matplotlib.pyplot as plt
import pickle

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME")

from sumolib import checkBinary
import traci

# numBuses = 6
numBuses = 18

class SumoEnv(gym.Env):
    # epLen: the number of RL steps before the episode terminates
    # traffic: set to zero for no traffic or else to the lowest traffic speed in km/h
    # bunched: True - buses start already bunched, False - buses start evenly spaced
    # mixedConfigs: Used during training to alternate between already bunched and evenly spaced scenarios
    def __init__(self, gui=False, noWarnings=False, epLen=250, traffic=False, bunched=False, mixedConfigs=False, save=None, continuous=False, headwayReward=True):
        if gui:
            self._sumoBinary = checkBinary('sumo-gui')
        else:
            self._sumoBinary = checkBinary('sumo')

        self.episodeNum = 0

        self.traffic = traffic
        self.mixedConfigs = mixedConfigs
        self.continuous = continuous
        self.headwayReward = headwayReward

        if not self.traffic and not bunched:
            self.config = 'scenario2/sumo/ring.sumocfg'
        elif not self.traffic and bunched:
            self.config = 'scenario2/sumo/ringBunched.sumocfg'
        elif self.traffic and not bunched:
            self.config = 'scenario2/sumo/ringTraffic.sumocfg'

        self.noWarnings = noWarnings
        # self.sumoCmd = [self._sumoBinary, "-c", self.config, "--tripinfo-output", "tripinfo.xml", "--no-internal-links", "false", "--lanechange.overtake-right", "true"]
        self.sumoCmd = [self._sumoBinary, "-c", self.config, "--no-internal-links", "false", "--lanechange.overtake-right", "true"]
        if self.noWarnings:
            self.sumoCmd.append("--no-warnings")

        self.epLen = epLen

        # if self.traffic == -1:
        #     self.lowestTrafficSpeed = random.randint(7,10)
        # else:
        #     self.lowestTrafficSpeed = self.traffic

        self.gymStep = 0
       
        self.stoppedBuses = [[None for _ in range(6)], [None for _ in range(6)], [None for _ in range(6)]]
        
        self.route1Travel = {0:[[]], 1:[[]], 2:[[]], 3:[[]], 4:[[]], 5:[[]]}
        self.route2Travel = {0:[[]], 1:[[]], 2:[[]], 3:[[]], 4:[[]], 5:[[]]}
        self.route3Travel = {0:[[]], 1:[[]], 2:[[]], 3:[[]], 4:[[]], 5:[[]]}

        # Variable which contains the bus which has just reached a stop, the bus stop that it has reached, and the
        # stopping time required given the number of people alighting at this stop and those waiting to board
        self.decisionBus = ["bus.0", "stop1", 0]

        self.save= save

        traci.start(self.sumoCmd)

        self.busStops = list(traci.simulation.getBusStopIDList()) # get the list of bus stops from the simulation
        # self.buses = [bus for bus in traci.vehicle.getIDList() if bus[0:3] == "bus" and bus[3] == '.'] # get the list of buses from the simulation
        # self.busesB = [bus for bus in traci.vehicle.getIDList() if bus[0:3] == "bus" and bus[3] == 'B']
        self.buses = ['bus.0', 'bus.1', 'bus.2', 'bus.3', 'bus.4', 'bus.5'] 
        self.busesB = ['busB.0', 'busB.1', 'busB.2', 'busB.3', 'busB.4', 'busB.5']
        self.busesC = ['busC.0', 'busC.1', 'busC.2', 'busC.3', 'busC.4', 'busC.5']


        self.busCapacity = 85

        # dictionary containing those people who have a destination bus stop assigned
        self.personsWithStop = dict()

        self.stopTime = 0

        # stores the number of people on each bus which will stop at each stop
        self.peopleOnBuses = [[0]*12, [0]*12, [0]*12, [0]*12, [0]*12, [0]*12]
        self.peopleOnBusesB = [[0]*12, [0]*12, [0]*12, [0]*12, [0]*12, [0]*12]
        self.peopleOnBusesC = [[0]*12, [0]*12, [0]*12, [0]*12, [0]*12, [0]*12] 


        self.routes = ['.', 'B', 'C']

        if not self.continuous:
            self.action_space = Discrete(3)
        else:
            self.action_space = Box(low=0, high=1, shape=(1,), dtype=np.float32)

       
        # the observation space:
        # contains the stop which the bus has reached, the forward and backward headways of the bus, the number of persons waiting at each stop, 
        # the stopping time required according to the number of people boarding and alighting at this stop, the current maximum passenger waiting 
        # times at each bus stop, the numnber of passengers on the previous, current, and following buses, and the speed factors of the previous,
        # current and follwing buses
        # if self.traffic != 0:
        #     self.low = np.array([0 for _ in range(len(self.routes))] + [0] + [0 for _ in range(len(self.busStops))] + [0, 0] +  [0 for _ in range(len(self.busStops))] + [0] + [0 for _ in range(len(self.busStops))] + [0, 0, 0] + [0, 0, 0], dtype='float32')
        #     # self.low = np.array([0 for _ in range(len(self.routes))] + [0 for _ in range(len(self.busStops))] + [0, 0] +  [0 for _ in range(len(self.busStops))] + [0] + [0 for _ in range(len(self.busStops))] + [0, 0, 0] + [0, 0, 0], dtype='float32')

        #     self.high = np.array([1 for _ in range(len(self.routes))] + [1] + [1 for _ in range(len(self.busStops))] + [5320, 5320] + [float('inf') for _ in self.busStops] + [float('inf')] + [200000 for _ in self.busStops] + [85, 85, 85] + [1, 1, 1], dtype='float32')
        #     # self.high = np.array([1 for _ in range(len(self.routes))] + [1 for _ in range(len(self.busStops))] + [5320, 5320] + [float('inf') for _ in self.busStops] + [float('inf')] + [200000 for _ in self.busStops] + [85, 85, 85] + [1, 1, 1], dtype='float32')
        # else:
        self.low = np.array([0 for _ in range(len(self.routes))] + [0] + [0 for _ in range(len(self.busStops))] + [0, 0] +  [0 for _ in range(len(self.busStops))] + [0] + [0 for _ in range(len(self.busStops))] + [0, 0, 0], dtype='float32')
        # self.low = np.array([0 for _ in range(len(self.routes))] + [0 for _ in range(len(self.busStops))] + [0, 0] +  [0 for _ in range(len(self.busStops))] + [0] + [0 for _ in range(len(self.busStops))] + [0, 0, 0], dtype='float32')
        self.high = np.array([1 for _ in range(len(self.routes))] + [1] + [1 for _ in range(len(self.busStops))] + [5320, 5320] + [float('inf') for _ in self.busStops] + [float('inf')] + [200000 for _ in self.busStops] + [85, 85, 85], dtype='float32')
        # self.high = np.array([1 for _ in range(len(self.routes))] + [1 for _ in range(len(self.busStops))] + [5320, 5320] + [float('inf') for _ in self.busStops] + [float('inf')] + [200000 for _ in self.busStops] + [85, 85, 85], dtype='float32')

        self.observation_space = Box(self.low, self.high, dtype='float32')

        self.reward_range = (float('-inf'), 0)

        self.sdVal = 0
        
        self.dfLog = pd.DataFrame(columns=['time', 'meanWaitTime', 'action', 'dispersion', 'headwaySD'])

        ##################### MUST ADAPT ###########################################################
        self.inCommon1 = ['bus.1', 'busB.1']
        self.notInCommon1 = ['bus.2', 'busB.2', 'bus.3', 'busB.3', 'bus.4', 'busB.4', 'bus.5', 'busB.5', 'bus.0', 'busB.0']

        self.inCommon2 = ['busB.4', 'busC.4']
        self.notInCommon2 = ['busB.5', 'busC.5', 'busB.0', 'busC.0', 'busB.1', 'busC.1', 'busB.2', 'busC.2', 'busB.3', 'busC.3']
        ##################### MUST ADAPT ###########################################################


    def canSkip(self):
        bus = self.decisionBus[0]
        stop = self.decisionBus[1]
        personsOnBus = traci.vehicle.getPersonIDList(bus)
        for person in personsOnBus:
            if self.personsWithStop[person][0] == stop:
                return False

        return True

    def valid_action_mask(self):
        if self.canSkip():
            return [1,1,1]
        else:
            return [1,0,1]
        

    # step function required by the gym environment
    # each each step signifies an arrival of a bus at a bus stop 
    def step(self, action):

        self.gymStep += 1
        # print("GYM STEP: ", self.gymStep)
        
        self.logValues(action)

        #####################
        #   APPLY ACTION    #
        #####################
        
        if not self.continuous:
            # hold the bus
            if action == 0: 
                stopData = traci.vehicle.getStops(self.decisionBus[0], 1)
                # increase the stopping time of the vehicle by 15 seconds (hence holding the vehicle)
                traci.vehicle.setBusStop(self.decisionBus[0], stopData[0].stoppingPlaceID, duration=(self.decisionBus[2]+15))
                
                # UPDATE PEOPLE ON BUS

                # boarding
                personsOnStop = traci.busstop.getPersonIDs(self.decisionBus[1])
                # All persons of that line on the stop can board the bus
                for person in personsOnStop: 
                    # increment the number of passengers of the decision bus 
                    line = self.personsWithStop[person][2]
                    if traci.vehicle.getLine(self.decisionBus[0]) == 'line1':
                        #####CHECK IF CAN BOARD DEPENDING ON LINE
                        if line == 'line1':
                            self.peopleOnBuses[int(self.decisionBus[0][-1])][int(self.personsWithStop[person][0][-1])-1] += 1 
                            # set the decision bus as the bus which the person boarded 
                            self.personsWithStop[person][1] = self.decisionBus[0]
                    elif traci.vehicle.getLine(self.decisionBus[0]) == 'line2':
                        if line == 'line2':
                            # print(self.decisionBus[0][-1])
                            # print(self.personsWithStop[person])
                            self.peopleOnBusesB[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1
                            # set the decision bus as the bus which the person boarded 
                            self.personsWithStop[person][1] = self.decisionBus[0]
                    elif traci.vehicle.getLine(self.decisionBus[0]) == 'line3':
                        if line == 'line3':
                            # print(self.decisionBus[0][-1])
                            # print(self.personsWithStop[person])
                            self.peopleOnBusesC[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1
                            # set the decision bus as the bus which the person boarded 
                            self.personsWithStop[person][1] = self.decisionBus[0]
                #alighting
                personsOnBus = traci.vehicle.getPersonIDList(self.decisionBus[0])
                # Not everyone on the bus may be alighting at this stop
                for person in personsOnBus:
                    # check if passenger will alight at this stop
                    if self.personsWithStop[person][0] == self.decisionBus[1]:
                        # decrement the number of passengers of the decision bus
                        if traci.vehicle.getLine(self.decisionBus[0]) == 'line1':
                            self.peopleOnBuses[int(self.decisionBus[0][-1])][int(self.personsWithStop[person][0][-1])-1] -= 1
                        elif traci.vehicle.getLine(self.decisionBus[0]) == 'line2':
                            self.peopleOnBusesB[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] -= 1
                        elif traci.vehicle.getLine(self.decisionBus[0]) == 'line3':
                            self.peopleOnBusesC[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] -= 1
            # skip the stop
            elif action == 1: 
                stopData = traci.vehicle.getStops(self.decisionBus[0], 1)
                # set the stopping duration to zero, hence skipping the stop
                traci.vehicle.setBusStop(self.decisionBus[0], stopData[0].stoppingPlaceID, duration=0)

            # else action == 2, no action taken and bus proceeds normally by letting passengers board and alight
            else:
                stopData = traci.vehicle.getStops(self.decisionBus[0], 1)
                # set the stopping time to the time required just to let passengers board and alight
                # notice that we do not increase the stopping duration as we did for the holding action 
                traci.vehicle.setBusStop(self.decisionBus[0], stopData[0].stoppingPlaceID, duration=self.decisionBus[2])

                #UPDATE PEOPLE ON BUS

                #boarding
                personsOnStop = traci.busstop.getPersonIDs(self.decisionBus[1])
                # All persons of that line on the stop can board the bus
                for person in personsOnStop: 
                    # increment the number of passengers of the decision bus
                    line = self.personsWithStop[person][2]
                    if traci.vehicle.getLine(self.decisionBus[0]) == 'line1':
                        if line == 'line1':
                            self.peopleOnBuses[int(self.decisionBus[0][-1])][int(self.personsWithStop[person][0][-1])-1] += 1
                            # set the decision bus as the bus which the person boards
                            self.personsWithStop[person][1] = self.decisionBus[0]
                    elif traci.vehicle.getLine(self.decisionBus[0]) == 'line2':
                        if line == 'line2':
                            self.peopleOnBusesB[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1
                            # set the decision bus as the bus which the person boards
                            self.personsWithStop[person][1] = self.decisionBus[0]
                    elif traci.vehicle.getLine(self.decisionBus[0]) == 'line3':
                        if line == 'line3':
                            self.peopleOnBusesC[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1
                            # set the decision bus as the bus which the person boards
                            self.personsWithStop[person][1] = self.decisionBus[0]
                #alighting
                personsOnBus = traci.vehicle.getPersonIDList(self.decisionBus[0])
                # Not everyone on the bus may be alighting at this stop
                for person in personsOnBus:
                    # check if the passenger will alight at this stop
                    if self.personsWithStop[person][0] == self.decisionBus[1]:
                        # decrement the number of passengers of the decision bus
                        if traci.vehicle.getLine(self.decisionBus[0]) == 'line1':
                            self.peopleOnBuses[int(self.decisionBus[0][-1])][int(self.personsWithStop[person][0][-1])-1] -= 1
                        elif traci.vehicle.getLine(self.decisionBus[0]) == 'line2':
                            self.peopleOnBusesB[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] -= 1
                        elif traci.vehicle.getLine(self.decisionBus[0]) == 'line3':
                            self.peopleOnBusesC[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] -= 1
        else:
            if math.isnan(action):
                action = 0
            holdingTime = math.ceil(action * 9)

            stopData = traci.vehicle.getStops(self.decisionBus[0], 1)
            traci.vehicle.setBusStop(self.decisionBus[0], stopData[0].stoppingPlaceID, duration=(self.decisionBus[2]+holdingTime))

            # UPDATE PEOPLE ON BUS

            # boarding
            personsOnStop = traci.busstop.getPersonIDs(self.decisionBus[1])
            # All persons of that line on the stop can board the bus
            for person in personsOnStop: 
                # increment the number of passengers of the decision bus 
                line = self.personsWithStop[person][2]
                if traci.vehicle.getLine(self.decisionBus[0]) == 'line1':
                    #####CHECK IF CAN BOARD DEPENDING ON LINE
                    if line == 'line1':
                        self.peopleOnBuses[int(self.decisionBus[0][-1])][int(self.personsWithStop[person][0][-1])-1] += 1 
                        # set the decision bus as the bus which the person boarded 
                        self.personsWithStop[person][1] = self.decisionBus[0]
                elif traci.vehicle.getLine(self.decisionBus[0]) == 'line2':
                    if line == 'line2':
                        # print(self.decisionBus[0][-1])
                        # print(self.personsWithStop[person])
                        self.peopleOnBusesB[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1
                        # set the decision bus as the bus which the person boarded 
                        self.personsWithStop[person][1] = self.decisionBus[0]
                elif traci.vehicle.getLine(self.decisionBus[0]) == 'line3':
                    if line == 'line3':
                        # print(self.decisionBus[0][-1])
                        # print(self.personsWithStop[person])
                        self.peopleOnBusesC[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1
                        # set the decision bus as the bus which the person boarded 
                        self.personsWithStop[person][1] = self.decisionBus[0]
            #alighting
            personsOnBus = traci.vehicle.getPersonIDList(self.decisionBus[0])
            # Not everyone on the bus may be alighting at this stop
            for person in personsOnBus:
                # check if passenger will alight at this stop
                if self.personsWithStop[person][0] == self.decisionBus[1]:
                    # decrement the number of passengers of the decision bus
                    if traci.vehicle.getLine(self.decisionBus[0]) == 'line1':
                        self.peopleOnBuses[int(self.decisionBus[0][-1])][int(self.personsWithStop[person][0][-1])-1] -= 1
                    elif traci.vehicle.getLine(self.decisionBus[0]) == 'line2':
                        self.peopleOnBusesB[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] -= 1
                    elif traci.vehicle.getLine(self.decisionBus[0]) == 'line3':
                        self.peopleOnBusesC[int(self.decisionBus[0][-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] -= 1

        ########################################
        #   FAST FORWARD TO NEXT DECISION STEP #
        ########################################

        # run the simulation until a bus has reached a stop.
        # the variable reachedStopBuses contains a list of all buses that have reached a stop at this
        # simulation step, with each element containing the bus and the stop it has reached.
        reachedStopBuses = self.reachedStop()
        while len(reachedStopBuses) < 1: # while no bus has reached a stop
            self.sumoStep()
            reachedStopBuses = self.reachedStop()


        ###### UPDATE DECISION BUS #######
        # we set the first bus in reachedStopBuses as the decision bus
        # calculate the stopping time required
        self.stopTime = self.getStopTime(reachedStopBuses[0][0], reachedStopBuses[0][1])
        # if reachedStopBuses[0][0][3] == 'B':
        #     print('Stop {}, people on bus {}'.format(reachedStopBuses[0][1], self.peopleOnBusesB))
        #     print('Stop time {}'.format(self.stopTime))
        self.decisionBus = [reachedStopBuses[0][0], reachedStopBuses[0][1], self.stopTime]



        ###############################################
        #   GET NEW OBSERVATION AND CALCULATE REWARD  #
        ###############################################

        state = self.computeState()

        if self.headwayReward:
            reward = self.computeReward()
        else:
            reward = self.computeRewardWithTime()
        # 

        # print(self.peopleOnBuses)
        # print(self.decisionBus[0])
        # print(self.decisionBus[1])
        # print(self.stopTime)

        
        # check if episode has terminated
        # if self.gymStep > self.epLen:
        if traci.simulation.getTime() > self.epLen:#3000:
            print("DONE, episode num: ", self.episodeNum)

            done = True

            if self.save is not None:
                self.dfLog.to_csv(self.save + 'log.csv')
                with open(self.save + 'route1.pkl', 'wb') as f:
                    pickle.dump(self.route1Travel, f)
                with open(self.save + 'route2.pkl', 'wb') as f:
                    pickle.dump(self.route2Travel, f)
                with open(self.save + 'route3.pkl', 'wb') as f:
                    pickle.dump(self.route3Travel, f)


            # BUNCHING GRAPH
            # colours = ['red', 'green', 'orange', 'blue', 'purple', 'black']
            # labelled = [False for _ in range(6)]
            # for y in range(0,6):
            #     for z in self.bunchingGraphData[y]:
            #         x_values = []
            #         y_values = []

            #         for i in z:
            #             x_values.append((i[0]*9)/60)
            #             y_values.append(i[1])

            #         if not labelled[y]:
            #             plt.plot(x_values, y_values, color=colours[y], label='bus '+str(y))
            #             labelled[y] = True
            #         else:
            #             plt.plot(x_values, y_values, color=colours[y])
            # plt.yticks(range(1,13))
            # plt.title("PPO with Traffic, Bunched")
            # plt.xlabel('Time (mins)')
            # plt.ylabel('Bus Stop')
            # plt.legend(loc=4)
            # plt.savefig('results/final/bunching/ppo/TrafficBunchedBunching.jpg')
            # plt.show()
            # plt.clf()


            # # PIE CHART showing the actions taken
            # values = []
            # labels = []
            # actions = self.dfLog['action'].tolist()
            # hold = actions.count('Hold') / len(actions)
            # if hold != 0:
            #     values.append(hold)
            #     labels.append("Hold")
            # skip = actions.count('Skip') / len(actions)
            # if skip != 0:
            #     values.append(skip)
            #     labels.append("Skip")
            # noAction = actions.count('No action') / len(actions)
            # if noAction != 0:
            #     values.append(noAction)
            #     labels.append("No action")
    

            # plt.pie(values, labels=labels, autopct='%1.1f%%')
            # plt.title('Actions (PPO, Traffic, Bunched).jpg')
            # # plt.savefig('results/final/actions/ppo/TrafficBunchedActions.jpg')
            # # plt.show()
            # plt.clf()

        else:
            done = False

        info = {}

        return state, reward, done, info


    # reset function required by the gym environment 
    def reset(self):
        self.episodeNum += 1
        traci.close()
        
        if self.mixedConfigs: # choose the initial state of the environment (bunched or unbunched)
            if self.episodeNum % 2 == 0:
                self.config = 'scenario2/sumo/ring.sumocfg'
                print('Not bunched')
            else:
                self.config = 'scenario2/sumo/ringBunched.sumocfg'
                print('Bunched')

        # self.sumoCmd = [self._sumoBinary, "-c", self.config, "--tripinfo-output", "tripinfo.xml", "--no-internal-links", "false", "--lanechange.overtake-right", "true"]
        self.sumoCmd = [self._sumoBinary, "-c", self.config, "--no-internal-links", "false", "--lanechange.overtake-right", "true"]
        if self.noWarnings:
            self.sumoCmd.append("--no-warnings")
        traci.start(self.sumoCmd)
        self.gymStep = 0
        self.stoppedBuses = [[None for _ in range(6)], [None for _ in range(6)], [None for _ in range(6)]] 
        self.decisionBus = ["bus.0", "stop1", 0]
        self.personsWithStop = dict()
        self.peopleOnBuses = [[0]*12, [0]*12, [0]*12, [0]*12, [0]*12, [0]*12]
        self.peopleOnBusesB = [[0]*12, [0]*12, [0]*12, [0]*12, [0]*12, [0]*12]
        self.peopleOnBusesC = [[0]*12, [0]*12, [0]*12, [0]*12, [0]*12, [0]*12]

        self.stopTime = 0

        self.sdVal = 0

        self.route1Travel = {0:[[]], 1:[[]], 2:[[]], 3:[[]], 4:[[]], 5:[[]]}
        self.route2Travel = {0:[[]], 1:[[]], 2:[[]], 3:[[]], 4:[[]], 5:[[]]}
        self.route3Travel = {0:[[]], 1:[[]], 2:[[]], 3:[[]], 4:[[]], 5:[[]]}

        # if self.traffic == -1:
        #     self.lowestTrafficSpeed = random.randint(7,10)
        # else:
        #     self.lowestTrafficSpeed = self.traffic

        ##################### MUST ADAPT ###########################################################
        self.inCommon = ['bus.1', 'busB.1']
        self.notInCommon = ['bus.2', 'busB.2', 'bus.3', 'busB.3', 'bus.4', 'busB.4', 'bus.5', 'busB.5', 'bus.0', 'busB.0']

        self.inCommon2 = ['busB.4', 'busC.4']
        self.notInCommon2 = ['busB.5', 'busC.5', 'busB.0', 'busC.0', 'busB.1', 'busC.1', 'busB.2', 'busC.2', 'busB.3', 'busC.3']
        ##################### MUST ADAPT ###########################################################

        # sumo step until all buses are in the simulation
        while len(traci.vehicle.getIDList()) < numBuses: ##### SHOULD CHECK WHETHER THE VEHICLES ARE BUSES AND NOT CARS???
            self.sumoStep()

        # self.buses = [bus for bus in traci.vehicle.getIDList() if bus[0:3] == "bus" and bus[3] == '.']
        # self.busesB = [bus for bus in traci.vehicle.getIDList() if bus[0:3] == "bus" and bus[3] == 'B']
        self.buses = ['bus.0', 'bus.1', 'bus.2', 'bus.3', 'bus.4', 'bus.5'] 
        self.busesB = ['busB.0', 'busB.1', 'busB.2', 'busB.3', 'busB.4', 'busB.5']
        self.busesC = ['busC.0', 'busC.1', 'busC.2', 'busC.3', 'busC.4', 'busC.5']


        state = self.computeState()
        return state

    def close(self):
        traci.close()

    # function which returns a list of buses that have reached a stop
    def reachedStop(self):
        reached = []

        simTime = traci.simulation.getTime()

        mapping = {'.': 0, 'B': 1, 'C': 2}

        for vehicle in traci.vehicle.getIDList():
            if vehicle[0:3] == "bus":
                for stop in self.busStops:
                    # if the bus is on the same lane as the stop
                    if traci.busstop.getLaneID(stop) == traci.vehicle.getLaneID(vehicle):
                        # check if the bus is within reach of the stop
                        if (traci.vehicle.getLanePosition(vehicle) >= (traci.busstop.getStartPos(stop) - 5)) and (traci.vehicle.getLanePosition(vehicle) <= (traci.busstop.getEndPos(stop) + 1)):
                            # the bus shouls be marked as a newly stopped bus only if it was not already marked as so in 
                            # the previous few time steps
                            if self.stoppedBuses[mapping[vehicle[3]]][int(vehicle[-1])] == None:
                                # get stop id and update stopped bused list
                                self.stoppedBuses[mapping[vehicle[3]]][int(vehicle[-1])] = stop
                                # add the bus to the list of newly stopped buses
                                reached.append([vehicle, stop])

                                # if stop == 'stop9' or stop == 'stop9B':
                                #     self.inCommon.append(vehicle)
                                # elif stop == 'stop1' or stop == 'stop1B':
                                #     self.inCommon.remove(vehicle)

                                

                                # update bunching graph data
                                ##########################
                                # need to update
                                ##########################
                                
                                busNum = int(''.join([char for char in vehicle if char.isdigit()]))

                                s = int(''.join([char for char in stop if char.isdigit()]))

                                # if len(stop) == 5:
                                #     s = int(stop[-1])
                                # else:
                                #     s = int(stop[-2:])
                                if vehicle[3] == '.':
                                    self.route1Travel[busNum][-1].append((simTime, s))
                                elif vehicle[3] == 'B':
                                    self.route2Travel[busNum][-1].append((simTime, s))
                                elif vehicle[3] == 'C':
                                    self.route3Travel[busNum][-1].append((simTime, s))

                                # self.bunchingGraphData[busNum][-1].append((simTime, s))

                        else:
                            # update buses which have left a bus stop such that they are no longer marked as stopped
                            if self.stoppedBuses[mapping[vehicle[3]]][int(vehicle[-1])] != None:
                                self.stoppedBuses[mapping[vehicle[3]]][int(vehicle[-1])] = None
                                
                                # update bunching graoh data
                                ##########################
                                # need to update
                                ##########################
                                busNum = int(''.join([char for char in vehicle if char.isdigit()]))
                    
                                s = int(''.join([char for char in stop if char.isdigit()]))
                                
                                # if len(stop) == 5:
                                #     s = int(stop[-1])
                                # else:
                                #     s = int(stop[-2:])   

                                if vehicle[3] == '.':
                                    self.route1Travel[busNum][-1].append((simTime, s))
                                    if s == 12:
                                        self.route1Travel[busNum].append([])
                                elif vehicle[3] == 'B':
                                    self.route2Travel[busNum][-1].append((simTime, s))
                                    if s == 12:
                                        self.route2Travel[busNum].append([])
                                elif vehicle[3] == 'C':
                                    self.route3Travel[busNum][-1].append((simTime, s))
                                    if s == 12:
                                        self.route3Travel[busNum].append([])
                                # self.bunchingGraphData[busNum][-1].append((simTime, s))

                                #################################################################################
                                # MIGHT NEED TO UPDATE IF A ROUTE HAS A DIFFERENT NUMBER OF STOPS OTHER THAN 12 #
                                #################################################################################
                                # if s == 12:
                                #     self.bunchingGraphData[busNum].append([])
    
        
        # calculate headway standard deviation

        # MUST CHECK LATER ON

        if reached:
            headways = []
            for bus in traci.vehicle.getIDList():
                if bus[0:3] == "bus":
                    # follower, leader = self.getFollowerLeader(bus=[bus])

                    # forwardHeadway = self.getForwardHeadway(leader, bus)

                    # backwardHeadway = self.getForwardHeadway(bus, follower)
                    # headways.append(abs(forwardHeadway - backwardHeadway))

                    if bus not in self.inCommon1 and bus not in self.inCommon2:
                        # print('bus: {}'.format(bus))
                        # print('self.buses: {}'.format(self.buses))
                        # print('self.busesB: {}'.format(self.busesB))
                        h = self.notInCommonHeadways(bus=[bus])
                    else:
                        # print('from sd:')
                        h = self.inCommonHeadways(bus=[bus])
                    
                    headways.append(abs(h[0] - h[1]))

            average = sum(headways)/len(headways)
            deviations = [((headway - average)**2) for headway in headways]
            variance = sum(deviations) / len(headways)
            sd = math.sqrt(variance)

            self.sdVal = sd
        
        return reached

    def updateCommon(self):
        for vehicle in traci.vehicle.getIDList():
            if vehicle[0:3] == "bus":
                lane = traci.vehicle.getLaneID(vehicle)
                if lane == '9_1' and vehicle not in self.inCommon1:
                    self.inCommon1.append(vehicle)
                    self.notInCommon1.remove(vehicle)
                elif (lane == '0_1' or lane == 'E0_1') and vehicle in self.inCommon1:
                    self.inCommon1.remove(vehicle)
                    self.notInCommon1.append(vehicle)

                if lane == 'E3_1' and vehicle not in self.inCommon2:
                    self.inCommon2.append(vehicle)
                    self.notInCommon2.remove(vehicle)
                elif (lane == 'E6_1' or lane == 'C6_1') and vehicle in self.inCommon2:
                    self.inCommon2.remove(vehicle)
                    self.notInCommon2.append(vehicle)

        # print('inCommon: {}'.format(self.inCommon))
        # print('notInCommon: {}'.format(self.notInCommon))



    def sumoStep(self):
        traci.simulationStep() # run the simulation for 1 step
        self.updatePersonStop() # update the stops corresponding to each person 
        self.updateCommon()
        # print('common: {}'.format(self.inCommon))
        # update the passengers on board only if all buses are currently in the simulation
        if len([bus for bus in traci.vehicle.getIDList() if bus[0:3] == "bus"]) == numBuses:
            self.updatePassengersOnBoard()

        simTime = traci.simulation.getTime()

        # if self.traffic != 0:
        #     if simTime % 15 == 0: # add a new car in the simulation
        #         traci.vehicle.add('car'+str(simTime), 'traffic', typeID='traffic')
        #         repeats = random.randint(1,3) # randomly choose the number of times the new car will loop around the bus corridor
        #         # # build the new route of the car according to the number of repeats
        #         newRoute = ['E0']
        #         for _ in range(repeats):
        #             newRoute.extend(['5','6','7','8','9','10','11','0','1','2','3','4'])
        #         newRoute.extend(['5','6','7','8','9','E1'])
        #         traci.vehicle.setRoute('car'+str(simTime), newRoute)

        #         # randomly set the speed of the new car
        #         speeds = [self.lowestTrafficSpeed, 20, 30, 50]
        #         speed = random.randint(0,3)
        #         traci.vehicle.setSpeed('car'+str(simTime), speeds[speed])

        traci.vehicle.highlight('bus.0', color=(255,0,0), size=60)
        traci.vehicle.highlight('bus.1', color=(255,0,0), size=60)
        traci.vehicle.highlight('bus.2', color=(255,0,0), size=60)
        traci.vehicle.highlight('bus.3', color=(255,0,0), size=60)
        traci.vehicle.highlight('bus.4', color=(255,0,0), size=60)
        traci.vehicle.highlight('bus.5', color=(255,0,0), size=60)

        traci.vehicle.highlight('busB.0', color=(255,0,255), size=60)
        traci.vehicle.highlight('busB.1', color=(255,0,255), size=60)
        traci.vehicle.highlight('busB.2', color=(255,0,255), size=60)
        traci.vehicle.highlight('busB.3', color=(255,0,255), size=60)
        traci.vehicle.highlight('busB.4', color=(255,0,255), size=60)
        traci.vehicle.highlight('busB.5', color=(255,0,255), size=60)

        traci.vehicle.highlight('busC.0', color=(0,0,255), size=60)
        traci.vehicle.highlight('busC.1', color=(0,0,255), size=60)
        traci.vehicle.highlight('busC.2', color=(0,0,255), size=60)
        traci.vehicle.highlight('busC.3', color=(0,0,255), size=60)
        traci.vehicle.highlight('busC.4', color=(0,0,255), size=60)
        traci.vehicle.highlight('busC.5', color=(0,0,255), size=60)


    # function which computes the state required by the gym environment
    # The state that is returned contains the stop which the bus has reached, the forward and backward headways, the number of persons waiting at each stop,
    # the stopping time required according to the number of people boarding and alighting at this stop, the current maximum passenger waiting
    # times at each bus stop, and the number of passengers on the previous, current and following buses
    def computeState(self):

        route = self.oneHotEncode(self.routes, self.decisionBus[0][3])

        inCommon = 0
        if self.decisionBus[0] in ['stop10', 'stop11', 'stop12', 'stop4B', 'stop5B', 'stop6B']:
            inCommon = 1

        stop = self.oneHotEncode(self.busStops, self.decisionBus[1])
        # bus = self.oneHotEncode(self.buses, self.decisionBus[0]) would need to update 

        headways = self.getHeadways()
        
        waitingPersons = self.getPersonsOnStops()

        maxWaitTimes = self.getMaxWaitTimeOnStops()

        numPassengers = self.getNumPassengers()

        
        # if self.traffic != 0:
        #     # MUST ADAPT SPEED FACTORS FOR MORE THAN ONE LINE
        #     speedFactors = self.getSpeedFactors()
        #     state = route + [inCommon] + stop + headways + waitingPersons + [self.stopTime] + maxWaitTimes + numPassengers + speedFactors
        #     # state = route + stop + headways + waitingPersons + [self.stopTime] + maxWaitTimes + numPassengers + speedFactors
        # else:
        state = route + [inCommon] + stop + headways + waitingPersons + [self.stopTime] + maxWaitTimes + numPassengers
        # state = route + stop + headways + waitingPersons + [self.stopTime] + maxWaitTimes + numPassengers

        return state

    def oneHotEncode(self, list, item):
        return [1 if i == item else 0 for i in list]

    # function which returns the forward headway of a given bus (follower)
    
    #### MUST CHECK AND ADAPT
    def getForwardHeadway(self, leader, follower):
        # number of edges in the ring network simulation
        numEdges = 12
        leaderRoad = int(''.join([char for char in traci.vehicle.getRoadID(leader) if char.isdigit()]))
        followerRoad = int(''.join([char for char in traci.vehicle.getRoadID(follower) if char.isdigit()]))

        # both buses are on the same edge and the leader is in front of the follower.
        # just return the distance between the position of both buses
        if leaderRoad == followerRoad: 
            if traci.vehicle.getLanePosition(leader) - traci.vehicle.getLanePosition(follower) > 0:
                return traci.vehicle.getLanePosition(leader) - traci.vehicle.getLanePosition(follower)
        

        # otherwise, we must compute the length of all lanes between the two buses.
       
        # first find the remaining distance of the lane on which the follower currently is 
        h = traci.lane.getLength(traci.vehicle.getLaneID(follower)) - traci.vehicle.getLanePosition(follower)

        # calculate the number of edges between the those on which the two buses are
        if leaderRoad == followerRoad:
            repeats = numEdges - 1
        elif leaderRoad > followerRoad:
            repeats = leaderRoad - followerRoad - 1
        else:
            repeats = (numEdges - (abs(leaderRoad - followerRoad))) - 1
        
        # add the length of each edge in between the edges on which the two buses currently are
        line = traci.vehicle.getLine(follower)
        for i in range(repeats):
            lane = followerRoad + i + 1
            if lane >= numEdges:
                lane = lane % numEdges


            if line == 'line1':
                l = str(lane)
            elif line == 'line2':
                if lane not in [9,10,11]:
                    l = 'E'+str(lane)
                else:
                    l = str(lane)
            elif line == 'line3':
                if lane not in [3,4,5]:
                    l = 'C'+str(lane)
                else:
                    l = 'E'+str(lane) 

            h += traci.lane.getLength(l+"_0")

        # finally, add the portion of the leader's lane already driven  
        h += traci.vehicle.getLanePosition(leader)

        return h
            
    # function which returns the id of the leader and follower buses of the decision bus
    def getFollowerLeader(self, bus=[]):
        if bus:
            b = ''.join([char for char in bus[0] if char.isdigit()])
            line = traci.vehicle.getLine(bus[0])
        else:
            b = ''.join([char for char in self.decisionBus[0] if char.isdigit()]) 
            line = traci.vehicle.getLine(self.decisionBus[0])

        # print('b: {}'.format(b))
        # print('line: {}'.format(line))
        
        
        
        if line == 'line1':
            # if the decision bus is the last bus, then the follower is the first bus, hence it is set to zero
            if int(b) + 1 == len(self.buses):
                follower = "bus.0"
            # otherwise just increment the bus number
            else:
                follower = "bus." + str(int(b) + 1)
        
            # if the decision bus is the first bus, then the leader is the last bus, hence set to the number of buses minus 1
            if int(b) == 0:
                leader = "bus." + str(len(self.buses) - 1)
            # otherwise just decrement the bus number
            else:
                leader = "bus." + str(int(b) - 1)

        elif line == 'line2':
            # print('in line 2')
            # if the decision bus is the last bus, then the follower is the first bus, hence it is set to zero
            if int(b) + 1 == len(self.busesB):
                follower = "busB.0"
            # otherwise just increment the bus number
            else:
                follower = "busB." + str(int(b) + 1)

            # print('follower {}'.format(follower))
        
            # if the decision bus is the first bus, then the leader is the last bus, hence set to the number of buses minus 1
            if int(b) == 0:
                leader = "busB." + str(len(self.busesB) - 1)
                # print('b==0')
            # otherwise just decrement the bus number
            else:
                leader = "busB." + str(int(b) - 1)

            # print('leader {}'.format(leader))

        elif line == 'line3':
            # if the decision bus is the last bus, then the follower is the first bus, hence it is set to zero
            if int(b) + 1 == len(self.busesC):
                follower = 'busC.0'
            # otherwise just increment the bus number
            else:
                follower = 'busC.' + str(int(b) + 1)

            # if the decision bus is the first bus, then the leader is the last bus, hence set the number of buses minus 1
            if int(b) == 0:
                leader = 'busC.' + str(len(self.busesC) - 1)
            # otherwise just decrement the bus number
            else:
                leader = 'busC.' + str(int(b) - 1)

        return follower, leader

    def notInCommonHeadways(self, bus=[]):
        if bus:
            b = bus[0]
        else:
            b = self.decisionBus[0]
        # get the follower and leader of the decision bus
        follower, leader = self.getFollowerLeader(bus=[b])
        # print('follower, leader: {} {}'.format(follower, leader))
        
        # get the forward headway of the decision bus
        forwardHeadway = self.getForwardHeadway(leader, b)

        # get the backward headway of the decision bus.
        # in this case, we are in reality finding the forward headway of the follower to the decision bus which
        # is the same as the backward headway of the decision bus to its follower
        backwardHeadway = self.getForwardHeadway(b, follower)


        check = False
        line = b[3]
        if line == '.' or line == 'C':
            for veh in self.notInCommon: ###############################
                if veh[3] == line:
                    if veh == b:
                        check = True
                    
                    break

        # if check and (len(self.inCommon) != 0):
        mapping = {'.': self.inCommon1, 'C': self.inCommon2}
        if check:
            if len(mapping[line]) != 0:
                # if self.inCommon[-1] != leader:
                if mapping[line][-1] != leader:
                    # print(b)
                    # print('diff route leader {}'.format(self.inCommon[-1]))
                    # forwardHeadway = self.getForwardHeadway(self.inCommon[-1], b)
                    forwardHeadway = self.getForwardHeadway(mapping[line][-1], b)

            # else:
            #     print('{} Same route leader {}'.format(b, self.inCommon[-1]))

        check = False
        line = b[3]
        if line == 'B':
            for veh in self.notInCommon1:
                if veh[3] == line:
                    if veh == b:
                        check = True

                    break
            for veh in self.notInCommon2:
                if veh[3] == line:
                    if veh == b:
                        check = True

                    break

        if check:
            road = int(''.join([char for char in traci.vehicle.getRoadID(b) if char.isdigit()]))
            if road in [0,1,2]:
                if len(self.inCommon2) != 0:
                    if self.inCommon2[-1] != leader:
                        forwardHeadway = self.getForwardHeadway(self.inCommon2[-1], b)
            if road in [6,7,8]:
                if len(self.inCommon1) != 0:
                    if self.inCommon1[-1] != leader:
                        forwardHeadway = self.getForwardHeadway(self.inCommon1[-1], b)



        return [forwardHeadway, backwardHeadway]

    def inCommonHeadways(self, bus=[]):
        if bus:
            b = bus[0]
        else:
            b = self.decisionBus[0]
        sameRouteFollower, sameRouteLeader = self.getFollowerLeader(bus=[b])


        road = traci.vehicle.getRoadID(b)
        if road in ['9', '10', '11']:
            index = self.inCommon1.index(b)
            x = 0
        elif road in ['E3', 'E4', 'E5']:
            index = self.inCommon2.index(b)
            x = 1

        inCommon = {0: self.inCommon1, 1: self.inCommon2}
        notInCommon = {0: self.notInCommon1, 1: self.notInCommon2}

        # index = self.inCommon.index(b)

        # print(b)
        if b in self.inCommon1:
            index = self.inCommon1.index(b)
            x = 0
        elif b in self.inCommon2:
            index = self.inCommon2.index(b)
            x = 1
        
        if index == 0:  
            # leader = sameRouteLeader
            line = b[3]

            diffRouteLeader = None

            for veh in reversed(notInCommon[x]):
                if veh[3] != line:
                    diffRouteLeader = veh
                    break
            
            if diffRouteLeader == None: # just in case all other route buses are following in the common corridor
                for veh in reversed(inCommon[x]):
                    if veh[3] != line:
                        diffRouteLeader = veh
                        break

            sameRouteHeadway = self.getForwardHeadway(sameRouteLeader, b)
            diffRouteHeadway = self.getForwardHeadway(diffRouteLeader, b)

            # if sameRouteHeadway < diffRouteHeadway:
            #     print('Same Route Leader')
            # else:
            #     print('Diff route Leader')

            forwardHeadway = sameRouteHeadway if sameRouteHeadway < diffRouteHeadway else diffRouteHeadway

        else:
            # leader = self.inCommon[index - 1]
            leader = inCommon[x][index - 1]
            
            forwardHeadway = self.getForwardHeadway(leader, b)

        if index == len(inCommon[x]) - 1:
            # follower = sameRouteFollower
            line = b[3]

            diffRouteFollower = None

            for veh in notInCommon[x]:
                if veh[3] != line:
                    diffRouteFollower = veh
                    break

            if diffRouteFollower == None: # just in case all other route buses are leading in the common corridor
                for veh in inCommon[x]:
                    if veh[3] != line:
                        diffRouteFollower = veh
                        break

            sameRouteHeadway = self.getForwardHeadway(b, sameRouteFollower)
            diffRouteHeadway = self.getForwardHeadway(b, diffRouteFollower)

            # if sameRouteHeadway < diffRouteHeadway:
            #     print('Same Route Follower')
            # else:
            #     print('Diff Route Follower')

            backwardHeadway = sameRouteHeadway if sameRouteHeadway < diffRouteHeadway else diffRouteHeadway
        
        else:
            # follower = self.inCommon[index + 1]
            follower = inCommon[x][index + 1]

        # print('```````````````````````````')
        # print('bus: {}'.format(b))
        # print('manual follower: {}'.format(follower))
        
        # print('traci follower: {}'.format(traci.vehicle.getFollower(b, dist=443)))

            backwardHeadway = self.getForwardHeadway(b, follower)

        # print('manual headway: {}'.format(backwardHeadway))
        # print('```````````````````````````')

        return [forwardHeadway, backwardHeadway]
        


    # function which returns the forward and backward headways of the decision bus
    def getHeadways(self):
        line = traci.vehicle.getLine(self.decisionBus[0])
        if (line == 'line1' and len(self.buses) > 1) or (line == 'line2' and len(self.busesB) > 1) or (line == 'line3' and len(self.busesC) > 1):
            
            if self.decisionBus[0] not in self.inCommon1 and self.decisionBus[0] not in self.inCommon2:
                return self.notInCommonHeadways()
            else:
                return self.inCommonHeadways()
            
        else:
            return [0, 0]

    # function which returns the number of people waiting on each stop in the network
    def getPersonsOnStops(self):
        persons = [traci.busstop.getPersonCount(stop) for stop in self.busStops]
        return persons

    # function which returns the maximum passenger waiting time of each stop in the network
    def getMaxWaitTimeOnStops(self):
        maxWaitTimes = []
        for stop in self.busStops:
            personsOnStop = traci.busstop.getPersonIDs(stop)
            waitTimes = [traci.person.getWaitingTime(person) for person in personsOnStop]
            # check if there are actually people waiting on the stop
            if len(waitTimes) > 0:
                maxWaitTimes.append(max(waitTimes))
            # if no people are waiting on the stop, then the max wait time of this stop is set to zero
            else:
                maxWaitTimes.append(0)

        return maxWaitTimes

    # function which returns the number of passengers on the leader bus, decision bus, and follower bus
    def getNumPassengers(self):
        sameRouteFollower, sameRouteLeader = self.getFollowerLeader()

        bus = self.decisionBus[0]
        road = traci.vehicle.getRoadID(bus)
        if road in ['9', '10', '11']:
            x = 0
        elif road in ['E3', 'E4', 'E5']:
            x = 1

        if bus in self.inCommon1:
            x = 0
        elif bus in self.inCommon2:
            x = 1

        inCommon = {0: self.inCommon1, 1: self.inCommon2}

        if bus in self.inCommon1 or bus in self.inCommon2:
            index = inCommon[x].index(bus)
            # index = self.inCommon.index(bus)
            if index == 0:
                leader = sameRouteLeader
            else:
                leader = inCommon[x][index - 1]
            if index == len(inCommon[x]) - 1:
                follower = sameRouteFollower
            else:
                follower = inCommon[x][index + 1]
        else:
            leader = sameRouteLeader
            follower = sameRouteFollower


        numPassengers = [traci.vehicle.getPersonNumber(leader), traci.vehicle.getPersonNumber(self.decisionBus[0]), traci.vehicle.getPersonNumber(follower)]
        return numPassengers

    # function which computes the reward required by the gym environment and rl algorithm
    def computeReward(self):

        headways = self.getHeadways()

        forward = headways[0]
        backward = headways[1]

        reward = -abs(forward - backward)

        return reward  

    # function which computes the reward required by the gym environment and rl algorithm
    def computeRewardWithTime(self):

        # headways = self.getHeadways()

        # forward = headways[0]
        # backward = headways[1]

        # dist = -abs(forward - backward)

        # speed = traci.vehicle.getSpeed(self.decisionBus[0])

        # time = dist/speed

        maxWaitTimes = self.getMaxWaitTimeOnStops()

        reward = -sum(maxWaitTimes)

        return reward   


    # function which randomly assigns a destination bus stop to persons yet without a destination
    def updatePersonStop(self):
        persons = traci.person.getIDList()
        # get list of persons curently without destination
        personsWithoutStop = [person for person in persons if person not in self.personsWithStop]
        for person in personsWithoutStop:
            if person[0] == 'p':
                line = 'line1'
                # assign a random bus stop from the following six bus stops as the destination (as is done in the paper by Wang and Sun 2020)
                num = random.randint(1,6)
                edge = traci.person.getRoadID(person)
                newEdge = (int(edge) + num) % 12
                newStop = newEdge + 1
                stop = "stop"+str(newStop)
                traci.person.appendDrivingStage(person, str(newEdge), "line1", stopID=stop) 
                traci.person.appendWalkingStage(person, [str(newEdge)], 250) 
                # add the person to the persons with an assigned stop
                self.personsWithStop[person] = [stop, None, line]
            elif person[0] == 'B':
                line = 'line2'
                num = random.randint(1,6)
                edgeTemp = traci.person.getRoadID(person)

                if not edgeTemp[0].isdigit():
                    edge = edgeTemp[1:]
                else:
                    edge = edgeTemp

                newEdge = (int(edge) + num) % 12
                newStop = newEdge + 1
                stop = "stop"+str(newStop)
                if newStop not in [10, 11, 12]:
                    stop += 'B'
                    e = 'E'+str(newEdge)
                else:
                    e = str(newEdge)
                traci.person.appendDrivingStage(person, e, "line2", stopID=stop) 
                traci.person.appendWalkingStage(person, [e], 250) 
                # add the person to the persons with an assigned stop
                self.personsWithStop[person] = [stop, None, line] 
            elif person[0] == 'C':
                line = 'line3'
                num = random.randint(1,6)
                road = traci.person.getRoadID(person)

                edge = int(''.join([char for char in road if char.isdigit()]))
                newEdge = (int(edge) + num) % 12
                newStop = newEdge + 1
                stop = 'stop' + str(newStop)

                if newStop not in [4, 5, 6]:
                    stop += 'C'
                    e = 'C' + str(newEdge)
                else:
                    stop += 'B'
                    e = 'E' + str(newEdge)

                traci.person.appendDrivingStage(person, e, 'line3', stopID=stop)
                traci.person.appendWalkingStage(person, [e], 250)
                # add the person to ther persons with an assigned stop
                self.personsWithStop[person] = [stop, None, line]
            
            
    # function which determines the dwell time of a bus at a stop based on the number of passengers boarding and alighting, using the boarding and alighting rates
    def getStopTime(self, bus, stop):

        # the number of people on the bus stop waiting to board the bus
        # boarding = traci.busstop.getPersonCount(stop)

        line = traci.vehicle.getLine(bus)
        boarding = 0
        personsOnStop = traci.busstop.getPersonIDs(self.decisionBus[1])
        for person in personsOnStop:
            if self.personsWithStop[person][2] == line:
                boarding += 1
        
        # the number of passengers on this bus that will alight at this stop
        if line == 'line1':
            alighting = self.peopleOnBuses[int(bus[-1])][int(''.join([char for char in stop if char.isdigit()]))-1]
        elif line == 'line2':
            alighting = self.peopleOnBusesB[int(bus[-1])][int(''.join([char for char in stop if char.isdigit()]))-1]
        elif line == 'line3':
            alighting = self.peopleOnBusesC[int(bus[-1])][int(''.join([char for char in stop if char.isdigit()]))-1]

        # calculate dwell time according to the boarding and alighting rates in the paper by Wang and Sun 2020
        time = max(math.ceil(boarding/3), math.ceil(abs(alighting)/1.8)) #abs is there just in case is falls below zero if a person should've left a bus but the simulation did not give them time
        
        return time

    # For any passengers which board the bus during holding time and thus were not know beforehand that they would board
    def updatePassengersOnBoard(self): 
        # for bus in self.buses:
        for bus in traci.vehicle.getIDList():
            if bus[0:3] == "bus":
                for person in traci.vehicle.getPersonIDList(bus):
                    # check if passenger does not yet have a bus assigned to them
                    if self.personsWithStop[person][1] == None:
                        # assign the bus to the passenger
                        self.personsWithStop[person][1] = bus 
                        # increment number of passengers of the particular bus
                        line = self.personsWithStop[person][2]
                        if line == 'line1':
                            self.peopleOnBuses[int(bus[-1])][int(self.personsWithStop[person][0][-1])-1] += 1
                        elif line == 'line2':
                            self.peopleOnBusesB[int(bus[-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1
                        elif line == 'line3':
                            self.peopleOnBusesC[int(bus[-1])][int(''.join([char for char in self.personsWithStop[person][0] if char.isdigit()]))-1] += 1

    # function which returns the speed factor (speed of bus/speed without traffic) of the leader bus, decision bus, and follower bus
    def getSpeedFactors(self):
        follower, leader = self.getFollowerLeader()

        speedFactors = [traci.vehicle.getSpeed(leader)/20, traci.vehicle.getSpeed(self.decisionBus[0])/20, traci.vehicle.getSpeed(follower)/20]
        return speedFactors

    # logging the values in the dataframe
    def logValues(self, action):

        time = traci.simulation.getTime()

        maxWaitTimes = self.getMaxWaitTimeOnStops()    
        mean = sum(maxWaitTimes)/len(maxWaitTimes)
        
        actions = ['Hold', 'Skip', 'No action']

        if not self.continuous:
            a = actions[action]
        else:
            a = action

        occDisp = self.occupancyDispersion()

        self.dfLog = pd.concat([self.dfLog, pd.DataFrame.from_records([{'time': time, 'meanWaitTime':mean, 'action':a, 'dispersion':occDisp, 'headwaySD':self.sdVal}])], ignore_index=True)

    # occupancy dispersion as calculated in Wang and Sun (2020), using a variance to mean ratio
    def occupancyDispersion(self):
        passengers = []
        for bus in self.buses:
            passengers.append(traci.vehicle.getPersonNumber(bus))
        for bus in self.busesB:
            passengers.append(traci.vehicle.getPersonNumber(bus))
        for bus in self.busesC:
            passengers.append(traci.vehicle.getPersonNumber(bus))

        average = sum(passengers)/len(passengers)
        if average == 0:
            return 0

        deviations = [((p - average)**2) for p in passengers]
        variance = sum(deviations) / len(passengers)

        occDisp = variance / average

        return occDisp
