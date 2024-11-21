# import gymnasium as gym
import gym
import os
import sys
from sumolib import checkBinary
import traci
import random
import pandas as pd
import math
import numpy as np
from gym.spaces import Box, Discrete
import statistics
import pickle

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit('Please declare environment variable \'SUMO_HOME\'')

numBuses = 33

uniqueStops = ['410460005', '410459901', '410459897', '410459904', '410459657', '410459651', '410467153', '410462101', '410462103',
           '410475114', '1531005322', '410483103', '410482520', '410482572', '410482568', '410482491', '410482562', '410482564',
           '410482570', '410482551', '410471081', '410471030', '410480716', '410480722', '410480721', '5701793241', '410480724',
           '410464248', '410465916', '410465917', '410465915', '410462762', '410466111', '410464251', '1847853709', '7314770844',
           '3865151058', '1849631331', '3737148763', '8926967788', '410474760', '410474348', '1849631269', '2429952037', '1849631273',
           '410462266', '410462293', '410462211', '410462291', '410486991', '410486955', '4430976208', '410486969', '1855320978',
           '410486966', '410486516', '410486293', '410470959', '410471005', '410464255', '410478275', '-410478274', '-410478273',
           '-1849457018', '410478271', '410459494', '4623289717', '410467553', '410467566', '410467564', '1268343846', '410467574',
           '410467562', '410467567', '410467571', '410461658', '410481810', '410481815', '410481781', '410481783', '410482047',
           '410482019', '1847713996']

trips = {} # dictionary to store the destination bus stop of a passenger
route22 = ['410460005', '410459901', '410459897', '410459904', '410459657', '410459651', '410467153', '410462101', '410462103',
           '410475114', '1531005322', '410483103', '410482520', '410482572', '410482568', '410482491', '410482562', '410482564',
           '410482570', '410482551', '410471081', '410471030', '410480716', '410480722', '410480721', '5701793241', '410480724',
           '410464248', '410465916', '410465917', '410465915', '410462762', '410466111', '410464251'] #34 stops
route43 = ['1847853709', '7314770844', '3865151058', '1849631331', '3737148763', '8926967788', '410474760', '410474348', '1849631269',
           '2429952037', '1849631273', '410462266', '410462293', '410462211', '410462291', '410486991', '410486955', '4430976208',
           '410486969', '1855320978', '410486966', '410486516', '410486293', '410475114', '1531005322', '410483103', '410482520',
           '410482572', '410482568', '410482491', '410482562', '410482564', '410482570', '410482551', '410471081', '410471030',
           '410470959', '410471005', '410464255', '410478275', '-410478274', '-410478273', '-1849457018', '410478271', '410459494',
           '4623289717', '410467553', '410467566', '410467564', '1268343846', '410467574', '410467562', '410467567', '410467571',
           '410461658', '410481810', '410481815', '410481781', '410481783', '410482047', '410482019', '1847713996'] #62 stops
shared = ['410475114', ['410480716', '410470959']]
sharedStops = ['410475114', '1531005322', '410483103', '410482520', '410482572', '410482568', '410482491', '410482562', '410482564',
               '410482570', '410482551', '410471081', '410471030']
firstStopsEdges = ['543768663', '631887962#0']
finalStopsEdges = ['245934570#2', '528461109']

w = [0.4, 0.5, 0.1]
 
class sumoMultiLine(gym.Env):

    metadata = {}

    def __init__(self, gui=False, traffic=False, bunched=False, headwayReward=True, save=None, noWarnings=True, saveState=None, continuous=False, epLen=52000):

        self.epLen = epLen
        self.continuous = continuous
        self.saveState = saveState
        self.save = str(save)
        self.episodeNum = 0
        self.trips = {}
        self.bus_states =  {} # dictionary to store the state of each bus
        self.actionBuses = []
        self.total22 = 0
        self.total43 = 0

        self.travelTimes22 = {}
        self.travelTimes43 = {}

        self.bunchingGraphData = {}

        self.df = pd.DataFrame(columns=['time', 'meanWaitTime', 'meanLow', 'action', 'dispersion', 'headwaySD'])
        self.rates = pd.DataFrame(columns=['rate'])       
        
        self.bunchingGraphData = {}
        self.reachedSharedCorridor = [] # buses that have reached the first stop of the shared corridor, will remain in list until end of journey
        
        if gui:
            self.sumoBinary = checkBinary('sumo-gui')
        else:
            self.sumoBinary = checkBinary('sumo')

        self.traffic = traffic
        self.bunched = bunched
        self.headwayReward = headwayReward
        self.noWarnings = noWarnings

        if not self.traffic and not self.bunched:
            self.config = 'singaporeRing/sumo/singapore.sumo.cfg'
        elif not self.traffic and self.bunched:
            pass
        elif self.traffic and not self.bunched:
            pass
        
        if self.saveState is None or self.saveState is False:
            self.sumoCmd = [self.sumoBinary, '-c', self.config, '--tripinfo-output', 'tripinfo.xml', '--no-internal-links', 'true', '--time-to-teleport', '550']#, '--save-state.times', '1500', '--save-state.files', 'test.xml', '--save-state.transportables']#, '--lanechange.overtake-right', 'true']
        else:
            self.sumoCmd = [self.sumoBinary, '-c', self.config, '--tripinfo-output', 'tripinfo.xml', '--no-internal-links', 'true', '--time-to-teleport', '550', '--save-state.times', str(self.saveState), '--save-state.files', 'singaporeRing/sumo/state.xml', '--save-state.transportables']
        
        if self.noWarnings:
            self.sumoCmd.append("--no-warnings")

        self.stoppedBuses = [[None for _ in range(12)], [None for _ in range(21)]]
        self.route22Travel = {i:[[]] for i in range(12)}
        self.route43Travel = {i:[[]] for i in range(21)}

        self.buses = ['bus.'+str(i) for i in range(12)]
        self.busesB = ['busB.'+str(i) for i in range(21)]

        self.currentVehicles = []
        self.hour = 6

        self.sdVal = 0        

        self.routes = ['.', 'B']

        self.inCommon = []
        self.notInCommon = ['bus.'+str(i) for i in range(12)]
        self.notInCommon.extend(['busB.'+str(i) for i in range(21)])

        self.decisionBus = ["bus.0", "410460005", 0]
        traci.start(self.sumoCmd)
        if self.saveState == False:
            traci.simulation.loadState('singaporeRing/sumo/state.xml')
            self.loadValues()
            for v in self.currentVehicles:
                traci.vehicle.subscribe(v[0], [traci.constants.VAR_NEXT_STOPS])

        self.busStops = list(traci.simulation.getBusStopIDList())
        
        self.df22 = pd.read_csv(os.path.join('singaporeRing','demand','byHour','hour'+str(self.hour),'route22.csv'))
        self.df43 = pd.read_csv(os.path.join('singaporeRing','demand','byHour','hour'+str(self.hour),'route43.csv'))
        self.addPassengers()

        if not self.continuous:
            self.action_space = Discrete(3)
        else:
            self.action_space = Box(low=0, high=1, shape=(1,), dtype=np.float32)
        
        self.low = np.array([0 for _ in range(2)] + [0] + [0 for _ in range(83)] + [0, 0] + [0 for _ in range(83)] + [0] + [0 for _ in range(83)] + [0,0,0], dtype='float32')
        self.high = np.array([1 for _ in range(2)] + [1] + [1 for _ in range(83)] + [float('inf'), float('inf')] + [float('inf') for _ in range(83)] + [float('inf')] + [float('inf') for _ in range(83)] + [85, 85, 85], dtype='float32')

        self.observation_space = Box(self.low, self.high, dtype='float32')

        self.reward_range = (float('-inf'), 0)

        self.episodes = 0

    def canSkip(self):
        
        bus = self.actionBuses[0]
        stop = self.bus_states[bus]['stop']
        personsOnBus = traci.vehicle.getPersonIDList(bus)
        for person in personsOnBus:
            if self.trips[person] == stop:
                return False
        return True
    
    def valid_action_mask(self):
        if self.canSkip():
            return [1,1,1]
        else:
            return [1,0,1]
            

    def step(self, action):
        self.executeAction(self.actionBuses[0], action)

        ######################################
        ### SET ACTION BUSES TO EMPTY LIST ###
        ######################################
        self.actionBuses = []

        done = self.sumoStep()

        if len(self.actionBuses) > 0:
            observation = self.observe(self.actionBuses[0])
            
            if self.headwayReward:
                reward = self.calculateReward(self.actionBuses[0])
            else:
                reward = self.calculateRewardWithTime()
            
        else: # when last bus exits in the final step
            observation = []
            reward = 0
        
        self.logValues(action)

        if done:
            if self.save != None:
                self.df.to_csv(self.save + 'log.csv')
                with open(self.save + 'bunchingGraph.pkl', 'wb') as f:
                    pickle.dump(self.bunchingGraphData, f)

        return observation, reward, done, {} #, dones, {}

    def oneHotEncode(self, list, item):
        return [1 if i == item else 0 for i in list]

    def getPersonsOnStop(self):
        persons = [traci.busstop.getPersonCount(stop) for stop in uniqueStops]
        return persons

    def getNumPassengers(self, bus):
        follower = self.getFollower(bus)
        leader = self.getLeader(bus)

        numPassengers = [traci.vehicle.getPersonNumber(leader), traci.vehicle.getPersonNumber(bus), traci.vehicle.getPersonNumber(follower)]

        return numPassengers


    def observe(self, bus):

        route = [0,1] if traci.vehicle.getLine(bus) == '22' else [1,0]

        inCommon = 1 if self.bus_states[bus]['journeySection'] == 0 else 0

        stop = self.oneHotEncode(uniqueStops, self.bus_states[bus]['stop'])

        headways = self.getHeadways(bus) if inCommon == 0 else self.getHeadways(bus, sameRoute=False)

        waitingPersons = self.getPersonsOnStop()

        maxWaitTimes = self.getMaxWaitTimeOnStops()

        numPassengers = self.getNumPassengers(bus)

        alight_board = self.bus_states[bus]['alight_board']
        stopTime = max(math.ceil(alight_board[1] * 3), math.ceil(alight_board[0] * 1.8))

        observation = route + [inCommon] + stop + [headways[1], headways[0]] + waitingPersons + [stopTime] + maxWaitTimes + numPassengers
        
        return observation

    def calculateReward(self, bus):

        same_bh, same_fh = self.getHeadways(bus)
        bh = same_bh
        fh = same_fh
        if self.bus_states[bus]['journeySection'] == 0:
            other_bh, other_fh = self.getHeadways(bus, sameRoute=False)

            if other_bh < same_bh:
                bh = other_bh
            if other_fh < other_fh:
                fh = other_fh

        reward = -abs(fh - bh)

        return reward
    

    def calculateRewardWithTime(self):

        maxWaitTimes = self.getMaxWaitTimeOnStops()

        reward = -sum(maxWaitTimes)

        return reward
    
    def reset(self):
        self.close()

        self.trips = {}
        self.bus_states =  {} # dictionary to store the state of each bus
        self.actionBuses = []

        self.currentVehicles = []
        self.hour = 6

        self.sdVal = 0

        self.bunchingGraphData = {}
        self.reachedSharedCorridor = []

        traci.start(self.sumoCmd)
        if self.saveState == False:
            traci.simulation.loadState('singaporeRing/sumo/state.xml')
            self.loadValues()
            for v in self.currentVehicles:
                traci.vehicle.subscribe(v[0], [traci.constants.VAR_NEXT_STOPS])

        self.df = pd.DataFrame(columns=['time', 'meanWaitTime', 'meanLow', 'action', 'dispersion', 'headwaySD'])
        self.df22 = pd.read_csv(os.path.join('singaporeRing','demand','byHour','hour'+str(self.hour),'route22.csv'))
        self.df43 = pd.read_csv(os.path.join('singaporeRing','demand','byHour','hour'+str(self.hour),'route43.csv'))
        self.addPassengers()
        
        self.episodes += 1

        print("EPISODEEEEEE: {}".format(self.episodes))

        self.route22Travel = {i:[[]] for i in range(12)}
        self.route43Travel = {i:[[]] for i in range(21)}

        self.sumoStep()
        
        observation = self.observe(self.actionBuses[0])
        return observation

    def close(self):
        traci.close()

    # executes the given action to the bus
    def executeAction(self, bus, action):
        alight = self.bus_states[bus]['alight_board'][0]
        board = self.bus_states[bus]['alight_board'][1]

        time = max(math.ceil(board * 3), math.ceil(alight * 1.8))
        if not self.continuous:
            # hold the bus
            if action == 0:
                stopData = traci.vehicle.getStops(bus, 1)
                traci.vehicle.setBusStop(bus, stopData[0].stoppingPlaceID, duration=(time + 60))#120))

                simTime = traci.simulation.getTime()
                if bus[4:6] == '22':
                    stopIndex = route22.index(stopData[0].stoppingPlaceID)
                else:
                    stopIndex = route43.index(stopData[0].stoppingPlaceID)

                self.bunchingGraphData[bus][-1] = (simTime + 60, stopIndex)
            # skip the stop
            elif action == 1:
                stopData = traci.vehicle.getStops(bus, 1)
                traci.vehicle.setBusStop(bus, stopData[0].stoppingPlaceID, duration=0)
            # proceed normally
            else:
                stopData = traci.vehicle.getStops(bus, 1)
                traci.vehicle.setBusStop(bus, stopData[0].stoppingPlaceID, duration=time)
                
                simTime = traci.simulation.getTime()
                if bus[4:6] == '22':
                    stopIndex = route22.index(stopData[0].stoppingPlaceID)
                else:
                    stopIndex = route43.index(stopData[0].stoppingPlaceID)

                self.bunchingGraphData[bus][-1] = (simTime + time, stopIndex)

        else:
            if math.isnan(action):
                action = 0
            holdingTime = math.ceil(action * 60)#120)

            stopData = traci.vehicle.getStops(bus, 1)
            traci.vehicle.setBusStop(bus, stopData[0].stoppingPlaceID, duration=(time + holdingTime))

            simTime = traci.simulation.getTime()
            if bus[4:6] == '22':
                stopIndex = route22.index(stopData[0].stoppingPlaceID)
            else:
                stopIndex = route43.index(stopData[0].stoppingPlaceID)


            self.bunchingGraphData[bus][-1] = (simTime + holdingTime, stopIndex)
        
    def sumoStep(self):
        while len(self.actionBuses) == 0:
            traci.simulationStep()
            time = traci.simulation.getTime()
            if time % 1000 == 0:
                print('time: {}'.format(time))

            # start of a new hour
            if self.getHour(time) != self.hour:
                self.hour = self.getHour(time)
                # load the demand data for the current hour
                self.df22 = pd.read_csv(os.path.join('singaporeRing','demand','byHour','hour'+str(self.hour),'route22.csv'))
                self.df43 = pd.read_csv(os.path.join('singaporeRing','demand','byHour','hour'+str(self.hour),'route43.csv'))
                # add the passengers for the coming hour
                if self.saveState == False and self.hour != 11:
                    self.addPassengers()
                else:
                    self.addPassengers()
            
            # keep track of vehicles (buses) active in the simulation
            newV = traci.simulation.getDepartedIDList()
            newVehicles = []
            for v in newV:
                if v[:3] == 'bus':
                    traci.vehicle.subscribe(v, [traci.constants.VAR_NEXT_STOPS])
                    newVehicles.append([v, None, -1]) # [bus id, current stop, journey section] , journey section -> -1: before shared corridor, 0: in shared corridor, 1: after shared corridor
                    self.bus_states[v] = {'journeySection': -1, 'route': v.split(':')[0][-2:]}
                    
                    self.bunchingGraphData[v] = []

                    if traci.vehicle.getLine(v) == '22':
                        self.total22 += 1
                    else:
                        self.total43 += 1

            self.currentVehicles.extend(newVehicles)
            # create the trip for the newly departed passengers
            newPersons = traci.simulation.getDepartedPersonIDList()
            self.setStop(newPersons)
            # remove the persons that have arrived from the dictionary
            arrived = traci.simulation.getArrivedPersonIDList()
            self.updateTrips(arrived)

            removeVehicles = []
            # checking which buses have arrived at a stop 
            for v in self.currentVehicles:
                results = traci.vehicle.getSubscriptionResults(v[0])
                next_stop = results.get(traci.constants.VAR_NEXT_STOPS, None)
                
                if len(next_stop) == 0:
                    # remove bus since it does not have any more stops
                    # removeVehicles.append(v[0])
                    pass
                else:
                    stopId = next_stop[0][2] # the bus stop ID is the third element in the tuple returned

                    if traci.busstop.getLaneID(stopId) == traci.vehicle.getLaneID(v[0]): # bus is on same lane as its upcoming stop
                        if traci.vehicle.getLanePosition(v[0]) >= (traci.busstop.getStartPos(stopId) - 1): # bus is approaching the stop
                            if not traci.vehicle.isStopped(v[0]): # bus is not yet stopped
                                if v[1] != stopId: # set the vehicle's current stop to the stop ID 
                                    v[1] = stopId
                                    self.bus_states[v[0]]['stop'] = stopId
                                    if stopId == shared[0]: # update journey section to 'reached shared corridor'
                                        v[2] = 0
                                        self.bus_states[v[0]]['journeySection'] = 0
                                        self.reachedSharedCorridor.append(v[0])
                                    elif stopId in shared[1]: # update journey section to 'after shared corridor'
                                        v[2] = 1 
                                        self.bus_states[v[0]]['journeySection'] = -1
                                        self.reachedSharedCorridor.remove(v[0])
                                    elif stopId in [route22[0], route43[0]]:
                                        v[2] = -1

                                    # check if the bus should stop
                                    persons = self.shouldStop(v[0], stopId)
                                    if persons is None:
                                        traci.vehicle.setBusStop(v[0], stopId, duration=0) # stopping duration set to zero
                                        if v[0][4:6] == '22':
                                            stopIndex = route22.index(stopId)
                                        else: 
                                            stopIndex = route43.index(stopId)
                                        self.bunchingGraphData[v[0]].append((time, stopIndex))
                                        if v[0][4] == '2':
                                            self.route22Travel[int(v[0].split('.')[1])][-1].append((time, stopIndex))
                                        else:
                                            self.route43Travel[int(v[0].split('.')[1])][-1].append((time, stopIndex))
                                    # else add bus to actionBuses only if the stop is not the final one in the route (since it should always stop at the final stop)
                                    else:
                                        # if stopId not in finalStopsEdges:
                                        if stopId not in ['410464251', '1847713996']:
                                            # an action should be taken for this bus
                                            self.actionBuses.append(v[0])
                                            self.bus_states[v[0]]['alight_board'] = persons # keep track of number of people that want to alight and board                                    
                                        alight = persons[0]
                                        board = persons[1]

                                        if v[0][4:6] == '22':
                                            stopIndex = route22.index(stopId)
                                        else: 
                                            stopIndex = route43.index(stopId)
                                        self.bunchingGraphData[v[0]].append((time, stopIndex))


                                        seconds = max(math.ceil(board * 3), math.ceil(alight * 1.8))
                                        self.bunchingGraphData[v[0]].append((time + seconds, stopIndex))

            if len(self.actionBuses) > 0:
                headways = []
                for bus in self.currentVehicles:
                    bh, fh = self.getHeadways(bus[0])
                    if self.bus_states[bus[0]]['journeySection'] == 0:
                        other_bh, other_fh = self.getHeadways(bus[0], sameRoute=False)
                        if other_bh < bh:
                            bh = other_bh
                        if other_fh < fh:
                            fh = other_fh

                    headways.append(abs(fh - bh))

                self.sdVal = self.sd(headways)
            
            ### SAVING THE STATE ONCE ALL BUSES HAVE ENTERED THE NETWORK ###
            if self.saveState is not None and self.saveState is not False:
                if time == self.saveState:
                    with open('singaporeRing/sumo/state/trips.pkl', 'wb') as f:
                        pickle.dump(self.trips, f)
                    with open('singaporeRing/sumo/state/bus_states.pkl', 'wb') as f:
                        pickle.dump(self.bus_states, f)
                    with open('singaporeRing/sumo/state/actionBuses.pkl', 'wb') as f:
                        pickle.dump(self.actionBuses, f)
                    with open('singaporeRing/sumo/state/bunchingGraphData.pkl', 'wb') as f:
                        pickle.dump(self.bunchingGraphData, f)
                    with open('singaporeRing/sumo/state/reachedSharedCorridor.pkl', 'wb') as f:
                        pickle.dump(self.reachedSharedCorridor, f)
                    with open('singaporeRing/sumo/state/currentVehicles.pkl', 'wb') as f:
                        pickle.dump(self.currentVehicles, f)
                    with open('singaporeRing/sumo/state/hour.pkl', 'wb') as f:
                        pickle.dump(self.hour, f)

                if time == self.saveState + 1:
                    self.close()
            if self.saveState is not None and self.saveState is not False:
                if time == self.saveState + 1:
                    traci.simulation.saveState('singaporeRing/sumo/evenlySpacedtest.xml', saveTransportables=True)
                    self.close()
            
            if len(self.currentVehicles) < 1:
                return True

            if time == self.epLen:
                return True
        #########################################################################
        ###################### RETURN TRUE IF EPISODE HAS ENDED ####################
        #########################################################################
       
        return False
    
    # function that adds the passengers into the simulation for the coming hour
    def addPassengers(self): 
        routes = [route22, route43]
        currTime = traci.simulation.getTime()
        for index, route in enumerate(routes):
            if index == 0:
                df = self.df22
                line = '22'
            else:
                df = self.df43
                line = '43'

            # iterate over each route's bus stop
            for stop in route: 
                temp = df[df['Boarding Stop'] == int(stop)]
                if len(temp.index) != 0:
                    total = temp['Total'].sum() # total number of persons that arrive at this stop in the hour
                    departures = self.getDepartures(total)

                    # checking for passengers that enter the simulation at the same time, since persons cannot have the same ID in SUMO
                    duplicates = {x:departures.count(x) for x in departures if departures.count(x) > 1}
                    for key in duplicates.keys():
                        i = departures.index(key)
                        for z in range(duplicates[key]):
                            departures[i+z] = departures[i+z] + '.' + str(z) # add an index at the end to avoid having the same ID

                    for d in departures:
                        temp = d.split('.')
                        if len(temp) > 1:
                            dep = int(currTime + int(temp[0])) # calculate the time step when the passenger will depart
                            personId = stop + '.' + line + '.' + str(dep) + '.' +  temp[1] # create the passenger ID
                        else:
                            dep = int(currTime + int(d)) # calculate the time step when the passenger will depart
                            personId = stop + '.' + line + '.' + str(dep) # create the passenger ID

                        stopLane = traci.busstop.getLaneID(stop)
                        stopEdge = traci.lane.getEdgeID(stopLane)
                        stopPos = traci.busstop.getStartPos(stop)

                        # add the person on the edge of the stop, departing at the calculated time
                        traci.person.add(personId, stopEdge, stopPos - 1, depart=dep)
                        # walk to the bus stop
                        traci.person.appendWalkingStage(personId, [stopEdge], stopPos, stopID=stop)

    # function that returns the upcoming passenger departure time, according to the given rate, and governed by a Poisson distribution
    # rate is per hour
    # hour of the simulation
    def getDepartures(self, rate):

        lambdaValue = rate / 3600 # per second

        self.rates = pd.concat([self.rates, pd.DataFrame.from_records([{'rate':rate}])])

        totalTime = 3600
        if self.hour == 6:
            totalTime = 1800 # from 6.30 to 7 am, simulation starts at 6.30 and not 6.00
        departures = []
        currentTime = 0

        # keep adding passengers until the last departure that does not exceed an hour 
        while currentTime < totalTime:
            interval = random.expovariate(lambdaValue) # Poisson distribution
            currentTime += interval

            if currentTime < totalTime:
                departures.append(str(int(currentTime)))

        return departures # return as a list of strings, as required by the 'addPassengers' function

    # function that creates the trip for the newly departed passengers
    # person ids must be in the form 'BOARDINGSTOP.BUSLINE.TIMESTEP'
    # df22 and df43 contains the probabilities of the alighting bus stops 
    def setStop(self, persons): #, df22, df43):
        for person in persons:
            # extract boarding stop and line from passenger id
            boardingStop = person.split('.')[0] 
            line = person.split('.')[1]

            if line == '22':
                df = self.df22
            else:
                df = self.df43

            # extract all records relating to the boarding stop
            temp = df[df['Boarding Stop'] == boardingStop]
            possibleStops = temp['Alighting Stop'].astype(str).tolist() # traci functions require strings for ids
            stopWeights = temp['Total'].tolist()
            # give some small weight to the unmentioned stops
            possibleStops.append('other')
            stopWeights.append(0.1)
            
            # randomly select alighting bus stop according to the weights
            alightingStop = random.choices(possibleStops, weights=stopWeights)[0] # returns a list, so need to select the element
            
            # randomly select a different bus stop that is further downstream the route
            if alightingStop == 'other':
                if line == '22':
                    boardingIndex = route22.index(boardingStop)
                    alightingStop = random.choice(route22[boardingIndex + 1:]) # stop must be further downstream
                else:
                    boardingIndex = route43.index(boardingStop)
                    alightingStop = random.choice(route43[boardingIndex + 1:]) # stop must be further downstream
            
            # set the passenger's alighting stop
            alightLane = traci.busstop.getLaneID(alightingStop)
            alightEdge = traci.lane.getEdgeID(alightLane)

            traci.person.appendDrivingStage(person, alightEdge, "ANY", stopID=alightingStop)

            # update the trips dictionary with the new passenger and alighting stop
            self.trips[person] = alightingStop

    # determines whether a bus should stop given the passengers on board and those waiting at the stop 
    def shouldStop(self, bus, stop):
        alight = 0
        board = 0
        # check if any of the passengers on the bus want to alight at the stop
        for p in traci.vehicle.getPersonIDList(bus):
            if self.trips[p] == stop:
                # return True
                alight += 1
        # check if any of the persons waiting at the stop want to board this bus line
        busLine = traci.vehicle.getLine(bus)
        # print('busLine: {}'.format(busLine))
        for p in traci.busstop.getPersonIDs(stop):
            passengerLine = p.split('.')[1]
            # print('passengerLine: {}'.format(passengerLine))
            if passengerLine == busLine:
                # return True
                board += 1
        # bus does not need to stop
        # return False
        if alight == 0 and board == 0:
            return None
        
        return [alight, board]

    def updateTrips(self, arrived):
        for p in arrived:
            self.trips.pop(p) # remove finished trip from dictionary

    # function that returns the forward and backward headways of the provided bus
    def getHeadways(self, bus, sameRoute=True):
        follower = self.getFollower(bus, sameRoute=sameRoute)
        leader = self.getLeader(bus, sameRoute=sameRoute)

        backwardHeadway = self.getForwardHeadway(follower, bus)
        forwardHeadway = self.getForwardHeadway(bus, leader)

        return backwardHeadway, forwardHeadway

    # function that determines the follower bus of the provided bus
    def getFollower(self, bus, sameRoute=True):
        # follower bus with same route
        if sameRoute: 
            buses = [v[0] for v in self.currentVehicles if v[0].split(':')[0][-2:] == traci.vehicle.getLine(bus)]
            i = buses.index(bus) # index of bus in currentVehicles
            if i + 1 == len(buses): # bus is the current last of the route, therefore it has no follower
                return buses[0] 
            else: # follower is the next element of list since all buses keep their order as no overtaking is possible
                return buses[i + 1]
        # follower bus with different route
        else: 
            i = self.reachedSharedCorridor.index(bus) # reachedSharedCorridor is in order of travelling, thus use it instead of currentVehicles
            for b in self.reachedSharedCorridor[i:]:
                if b.split(':')[0][-2:] != traci.vehicle.getLine(bus): # follower is most next element of the other route
                    return b
            # check if follower may have not yet reached the shared corridor (by checking journey section)
            buses = [v[0] for v in self.currentVehicles if v[0].split(':')[0][-2:] != traci.vehicle.getLine(bus) and v[2] == -1]
            if len(buses) != 0: # follower is the first element
                return buses[0]
            # there is no follower
            return None
            
    # function that determines the leader bus of the provided bus
    def getLeader(self, bus, sameRoute=True):
        # leader bus with same route
        if sameRoute: 
            # get all active buses of route
            buses = [v[0] for v in self.currentVehicles if v[0].split(':')[0][-2:] == traci.vehicle.getLine(bus)]
            i = buses.index(bus) # index of bus in currentVehicles
            if i == 0: # bus is the leader of the route, therefore it has no leader
                return buses[-1]
            else: # leader is the previous element of list since all buses keep their order as no overtaking is possible 
                return buses[i - 1]
        # leader bus with different route
        else: 
            i = self.reachedSharedCorridor.index(bus) # reachedSharedCorridor is in order of travelling, thus use it instead of currentVehicles
            for b in reversed(self.reachedSharedCorridor[:i]):
                if b.split(':')[0][-2:] != traci.vehicle.getLine(bus): # leader is the most previous element of the other route
                    return b 
            return None # there is no active leader from the other route

    def getForwardHeadway(self, follower, leader, sameRoute=True):
        if follower is None:
            if leader == 'bus_22:3.7' or leader == 'bus_43:3.7': # last bus of service, therefore return zero
                return 0

            # else, following bus has not yet left initial terminus
            # calculate distance along route that the leader has travelled
            line = traci.vehicle.getLine(leader)
            # get the first bus stop, depending on whether sameRoute is True or False
            if sameRoute:
                startTerminus = firstStopsEdges[0]
                if line == '43':
                    startTerminus = firstStopsEdges[1]
            else:
                startTerminus = firstStopsEdges[1]
                if line == '43':
                    startTerminus = firstStopsEdges[0]

            # get Leader lane, edge and position
            leaderLane = traci.vehicle.getLaneID(leader)
            leaderPosition = traci.vehicle.getLanePosition(leader)
            leaderLaneLength = traci.lane.getLength(leaderLane)
            leaderEdge = traci.lane.getEdgeID(leaderLane)

            route = traci.simulation.findRoute(startTerminus, leaderEdge, vType='bus22')
            # headway is distance from first bus stop to leader position
            headway = route.length - (leaderLaneLength - leaderPosition)

            return headway            
        
        if leader is None:
            if follower == 'bus22:0.0' or follower == 'bus_43:0.0': # first bus of service, therefore return 0
                return 0
            # else, leader bus has already arrived at final terminus
            # calculate distance remaining along route
            line = traci.vehicle.getLine(follower)
            # get final bus stop, depending on whether sameRoute is True or False
            if sameRoute:
                finalTerminus = finalStopsEdges[0]
                if line == '43':
                    finalTerminus = finalStopsEdges[1]
            else:
                finalTerminus = finalStopsEdges[1]
                if line == '43':
                    finalTerminus = finalStopsEdges[0]

            # get follower lane, edge and position
            followerLane = traci.vehicle.getLaneID(follower)
            followerPosition = traci.vehicle.getLanePosition(follower)
            followerEdge = traci.lane.getEdgeID(followerLane)

            route = traci.simulation.findRoute(followerEdge, finalTerminus, vType='bus22')
            # headway is distance from follower position to last bus stop
            headway = route.length - followerPosition

            return headway

        # get follower and leader lane, edge and position
        followerLane = traci.vehicle.getLaneID(follower)
        followerPosition = traci.vehicle.getLanePosition(follower)
        followerEdge = traci.lane.getEdgeID(followerLane)
        
        leaderLane = traci.vehicle.getLaneID(leader)
        leaderPosition = traci.vehicle.getLanePosition(leader)
        leaderLaneLength = traci.lane.getLength(leaderLane)
        leaderEdge = traci.lane.getEdgeID(leaderLane)

        route = traci.simulation.findRoute(followerEdge, leaderEdge, vType='bus22')
        # headway is distance from position of follower to position of leader
        headway = route.length - followerPosition - (leaderLaneLength - leaderPosition)

        return headway

    def getHour(self, time):
        # simulation starts at 6.30am. Last demand file is at 8pm.
        if time < 1800:
            return 6
        elif time < 5400:
            return 7
        elif time < 9000:
            return 8
        elif time < 12600:
            return 9
        elif time < 16200:
            return 10
        elif time < 19800:
            return 11
        elif time < 23400:
            return 12
        elif time < 27000:
            return 13
        elif time < 30600:
            return 14
        elif time < 34200:
            return 15
        elif time < 37800:
            return 16
        elif time < 41400:
            return 17
        elif time < 45000:
            return 18
        elif time < 48600:
            return 19
        else:
            return 20

    def sd(self, l):
        average = sum(l)/len(l)
        deviations = [((x - average)**2) for x in l]
        variance = sum(deviations)/len(l)
        sd = math.sqrt(variance)
        return sd

    def occupancyDispersion(self):
        passengers = []

        for bus in self.currentVehicles:
            passengers.append(traci.vehicle.getPersonNumber(bus[0]))

        average = sum(passengers)/len(passengers)
        if average == 0:
            return 0

        deviations = [((p - average)**2) for p in passengers]
        variance = sum(deviations) / len(passengers)

        occDisp = variance / average

        return occDisp        

    def logValues(self, action):
        time = traci.simulation.getTime()
        
        actions = ['Hold', 'Skip', 'No action']
        if not self.continuous:
            a = actions[action]
        else:
            a = action

        occDisp = self.occupancyDispersion()

        maxWaitTimes = self.getMaxWaitTimeOnStops()

        w = [x for x in maxWaitTimes if x != 0]
        mean = sum(w)/len(w)

        meanLow = sum(maxWaitTimes)/len(maxWaitTimes)
        
        self.df = pd.concat([self.df, pd.DataFrame.from_records([{'time':time, 'meanWaitTime':mean, 'meanLow':meanLow, 'action':a, 'dispersion':occDisp, 'headwaySD':self.sdVal}])])#, ignore_index=True)

    def getMaxWaitTimeOnStops(self):
        maxWaitTimes = []

        for stop in uniqueStops:
            personsOnStop = traci.busstop.getPersonIDs(stop)
            waitTimes = [traci.person.getWaitingTime(person) for person in personsOnStop]
            if len(waitTimes) > 0:
                maxWaitTimes.append(max(waitTimes))
            # in order for the obsevation space to correspond
            # since when stops do not have any passengers these would otherwise not get included in the observation
            else:
                maxWaitTimes.append(0)
        
        if len(maxWaitTimes) != 0:
            return maxWaitTimes
        else:
            return None 

    def loadValues(self):
        with open('singaporeRing/sumo/state/trips.pkl', 'rb') as f:
            self.trips = pickle.load(f)
        with open('singaporeRing/sumo/state/bus_states.pkl', 'rb') as f:
            self.bus_states = pickle.load(f)
        with open('singaporeRing/sumo/state/actionBuses.pkl', 'rb') as f:
            self.actionBuses = pickle.load(f)
        with open('singaporeRing/sumo/state/bunchingGraphData.pkl', 'rb') as f:
            self.bunchingGraphData = pickle.load(f)
        with open('singaporeRing/sumo/state/reachedSharedCorridor.pkl', 'rb') as f:
            self.reachedSharedCorridor = pickle.load(f)
        with open('singaporeRing/sumo/state/currentVehicles.pkl', 'rb') as f:
            self.currentVehicles = pickle.load(f)
        with open('singaporeRing/sumo/state/hour.pkl', 'rb') as f:
            self.hour = pickle.load(f)