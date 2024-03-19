from pettingzoo import AECEnv
import os
import sys
from sumolib import checkBinary
import traci
import random
import pandas as pd
import math
import numpy as np

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit('Please declare environment variable \'SUMO_HOME\'')

trips = {} # dictionary to store the destination bus stop of a passenger
route22 = ['410460005', '410459901', '410459897', '410459904', '410459657', '410459651', '410467153', '410462101', '410462103',
           '410475114', '1531005322', '410483103', '410482520', '410482572', '410482568', '410482491', '410482562', '410482564',
           '410482570', '410482551', '410471081', '410471030', '410480716', '410480722', '410480721', '5701793241', '410480724',
           '410464248', '410465916', '410465917', '410465915', '410462762', '410466111', '410464251']
route43 = ['1847853709', '7314770844', '3865151058', '1849631331', '3737148763', '8926967788', '410474760', '410474348', '1849631269',
           '2429952037', '1849631273', '410462266', '410462293', '410462211', '410462291', '410486991', '410486955', '4430976208',
           '410486969', '1855320978', '410486966', '410486516', '410486293', '410475114', '1531005322', '410483103', '410482520',
           '410482572', '410482568', '410482491', '410482562', '410482564', '410482570', '410482551', '410471081', '410471030',
           '410470959', '410471005', '410464255', '410478275', '-410478274', '-410478273', '-1849457018', '410478271', '410459494',
           '4623289717', '410467553', '410467566', '410467564', '1268343846', '410467574', '410467562', '410467567', '410467571',
           '410461658', '410481810', '410481815', '410481781', '410481783', '410482047', '410482019', '1847713996']
shared = ['410475114', ['410480716', '410470959']]
firstStopsEdges = ['543768663', '631887962#0']
finalStopsEdges = ['245934570#2', '528461109']

w = [0.4, 0.5, 0.1]

class sumoMultiLine(AECEnv):
    def __init__(self, gui=False):
        super().__init__()
        self.agents = []
        self.agent_states =  {} # dictionary to store the state of each agent
        self.actionBuses = []
        self.total22 = 0
        self.total43 = 0

        self.reachedSharedCorridor = [] # buses that have reached the first stop of the shared corridor, will remain in list until end of journey

        if gui:
            self.sumoBinary = checkBinary('sumo-gui')
        else:
            self.sumoBinary = checkBinary('sumo')

        self.sumoCmd = [self.sumoBinary, '-c', 'singapore/singapore.sumo.cfg', '--tripinfo-output', 'tripinfo.xml', '--no-internal-links', 'true']#, '--lanechange.overtake-right', 'true']

        traci.start(self.sumoCmd)

        # self.envStep = 0
        self.currentVehicles = []
        self.hour = 6
        
        self.df22 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route22.csv'))
        self.df43 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route43.csv'))
        self.addPassengers()#self.df22, self.df43, self.hour)


    def step(self, actions):
        for bus in self.actionBuses:
            self.executeAction(bus, actions[bus])

        ######################################
        ### SET ACTION BUSES TO EMPTY LIST ###
        ######################################
        self.actionBuses = []

        done = self.sumoStep()

        observations = {agent: self.observe(agent) for agent in self.actionBuses}
        rewards = {agent: self.calculateReward(agent, actions[agent]) for agent in self.actionBuses}
        # dones = {}
        # done = False
        # if len(self.agents) < 1:
        #     done = True
        # print('ACTION BUSES SHOULD NOT BE EMPTY: {}'.format(self.actionBuses))

        return observations, rewards, done, {} #, dones, {}


    def addAgent(self, agent):
        self.agents.append(agent)
        self.agent_states[agent] = {'journeySection': -1, 'route': agent.split(':')[0][-2]}
        

    def removeAgent(self, agent):
        if agent in self.agents:
            self.agents.remove(agent)
            del self.agent_states[agent]

    def observe(self, agent):
        state = []

        # encode bus route
        if self.agent_states[agent]['route'] == '22':
            state += [0, 1]
        else:
            state += [1, 0]

        # headways with same route
        bh, fh = self.getHeadways(agent, sameRoute=True)
        state += [fh, bh]

        # encode total on board passengers and total persons waiting at stop 
        onBoardTotal = traci.vehicle.getPersonNumber(agent)
        atStopTotal = traci.busstop.getPersonCount(self.agent_states[agent['stop']])
        busCapacity = traci.vehicle.getPersonCapacity(agent)
        state += [onBoardTotal/busCapacity, atStopTotal/busCapacity]

        # if bus is in shared corridor, include headways with other route
        if self.agent_states[agent]['journeySection'] == 0:
            bh_other, fh_other = self.getHeadways(agent, sameRoute=False)
            state += [fh_other, bh_other]
        else: # bus is not in shared corridor
            state += [0, 0]

        return state

    def calculateReward(self, agent, action):
        r1 = self.getCVsquared(self.agent_states[agent]['route'])
        if self.agent_states[agent]['journeySection'] == 0:
            other_bh, other_fh = self.getHeadways(agent, sameRoute=False)
            r3 = np.exp(-abs(other_fh - other_bh))

            reward = - w[0] * r1 - w[1] * action + w[2] * r3
        else:
            reward = - w[0] * r1 - (w[1] + w[2]) * action

        return reward

    def getCVsquared(self, route):
        forwardHeadways = []
        for agent in reversed(self.agents):
            if self.agent_states[agent]['route'] == route:
                _, fh = self.getHeadways(agent, sameRoute = True)
                forwardHeadways.append(fh)
        variance = np.var(forwardHeadways)
        mean = np.mean(forwardHeadways)

        cvSquared = variance / mean / mean

        return cvSquared
    
    def reset(self):
        self.close()

        self.agents = []
        self.agent_states =  {} # dictionary to store the state of each agent
        self.actionBuses = []

        traci.start(self.sumoCmd)

        # self.envStep = 0
        self.currentVehicles = []
        self.hour = 6
        
        self.df22 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route22.csv'))
        self.df43 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route43.csv'))
        self.addPassengers()#self.df22, self.df43, self.hour)

        return {agent: self.observe(agent) for agent in self.actionBuses}

    def close(self):
        traci.close()
        ##############################################
        ### NOT SURE IF SHOULD ADDED ANYTHING ELSE ###
        ##############################################

    # executes the given action to the agent
    def executeAction(self, agent, action):
        # get number of alighting and boarding passengers at this stop
        alight = self.agent_states[agent]['alight_board'][0]
        board = self.agent_states[agent]['alight_board'][1]
        # calculate dwell time required according to boarding and alighting rates in the paper by Wang and Sun 2020
        time = max(math.ceil(board / 3), math.ceil(alight / 1.8))

        # caluclate holding time according to the action given
        holdingTime = math.ceil(action * 90)

        stopData = traci.vehicle.getStops(agent, 1)
        # set the stopping duration by adding the calculated holding time to the already required time 
        traci.vehicle.setBusStop(agent, stopData[0].stoppingPlaceID, duration=(time + holdingTime))

    def sumoStep(self):
        while len(self.actionBuses) == 0:
            traci.simulationStep()
            time = traci.simulation.getTime()

            # start of a new hour
            if self.getHour(time) != self.hour:
                self.hour = self.getHour(time)
                # load the demand data for the current hour
                self.df22 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route22.csv'))
                self.df43 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route43.csv'))
                # add the passengers for the coming hour
                self.addPassengers()#self.df22, self.df43, self.hour)
            
            # keep track of vehicles active in the simulation
            newV = traci.simulation.getDepartedIDList()
            newVehicles = []
            for v in newV:
                traci.vehicle.subscribe(v, [traci.constants.VAR_NEXT_STOPS])
                newVehicles.append([v, None, -1]) # [bus id, current stop, journey section] , journey section -> -1: before shared corridor, 0: in shared corridor, 1: after shared corridor
                self.addAgent(v)
                print("New Vehicle, Agent Added: {}".format(v))
                if traci.vehicle.getLine(v) == '22':
                    self.total22 += 1
                    # print('total22: {}'.format(self.total22))
                else:
                    self.total43 += 1
                    # print('total43: {}'.format(self.total43))
            self.currentVehicles.extend(newVehicles)
            print('Current Vehicles: {}'.format(self.currentVehicles))
            #########################################################################
            ###################### ADD AGENTS #######################################
            #########################################################################
            # create the trip for the newly departed passengers
            newPersons = traci.simulation.getDepartedPersonIDList()
            self.setStop(newPersons)#, self.df22, self.df43)
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
                    removeVehicles.append(v[0])
                else:
                    stopId = next_stop[0][2] # the bus stop ID is the third element in the tuple returned

                    if traci.busstop.getLaneID(stopId) == traci.vehicle.getLaneID(v[0]): # bus is on same lane as its upcoming stop
                        if traci.vehicle.getLanePosition(v[0]) >= (traci.busstop.getStartPos(stopId) - 1): # bus is approaching the stop
                            if not traci.vehicle.isStopped(v[0]): # bus is not yet stopped
                                if v[1] != stopId: # set the vehicle's current stop to the stop ID 
                                    v[1] = stopId
                                    self.agent_states[v[0]]['stop'] = stopId
                                    if stopId == shared[0]: # update journey section to 'reached shared corridor'
                                        v[2] = 0
                                        self.agent_states[v[0]]['journeySection'] = 0
                                        self.reachedSharedCorridor.append(v[0])
                                    elif stopId in shared[1]: # update journey section to 'after shared corridor'
                                        v[2] = 1 
                                        self.agent_states[v[0]]['journeySection'] = 1

                                    # check if the bus should stop
                                    # if not self.shouldStop(v[0], stopId):
                                    persons = self.shouldStop(v[0], stopId)
                                    if persons is None:
                                        traci.vehicle.setBusStop(v[0], stopId, duration=0) # stopping duration set to zero
                                    # else add bus to actionBuses only if the stop is not the final one in the route (since it should always stop at the final stop)
                                    elif stopId not in finalStopsEdges:
                                        # an action should be taken for this bus
                                        self.actionBuses.append(v[0])
                                        self.agent_states['alight_board'] = persons # keep track of number of people that want to alight and board                                    

            ############################################################################################################
            ###################### UPDATE GLOBAL LIST OF WHICH BUSES SHOULD STOP #######################################
            ############################################################################################################
            
            # removing the vehicles that have ended their journey
            for v in removeVehicles:
                for x in self.currentVehicles:
                    if v == x[0]:
                        self.reachedSharedCorridor.remove(v)
                        self.currentVehicles.remove(x)
                        self.removeAgent(v)

            #########################################################################
            ###################### REMOVE AGENTS ####################################
            #########################################################################

            if len(self.agents) < 1:
                return True
        #########################################################################
        ###################### RETURN TRUE IF NO MORE BUSES ####################
        #########################################################################
        # if len(self.agents) < 1:
        #     return True
        return False
    
    # function that adds the passengers into the simulation for the coming hour
    def addPassengers(self): #df22, df43, hour):
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
        totalTime = 3600
        if self.hour == 6:
            totalTime = 1800 # from 6.30 to 7 am, simulation starts at 6.30 and not 6.00
        departures = []
        currentTime = 0

        # keem adding passengers until the last departure that does not exceed an hour 
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

            traci.person.appendDrivingStage(person, alightEdge, line, stopID=alightingStop)

            # update the trips dictionary with the new passenger and alighting stop
            trips[person] = alightingStop

    # determines whether a bus should stop given the passengers on board and those waiting at the stop 
    def shouldStop(self, bus, stop):
        alight = 0
        board = 0
        # check if any of the passengers on the bus want to alight at the stop
        for p in traci.vehicle.getPersonIDList(bus):
            if trips[p] == stop:
                # return True
                alight += 1
        # check if any of the persons waiting at the stop want to board this bus line
        busLine = traci.vehicle.getLine(bus)
        for p in traci.busstop.getPersonIDs(stop):
            passengerLine = p.split('.')[1]
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
            trips.pop(p) # remove finished trip from dictionary

    # function that returns the forward and backward headways of the provided bus
    def getHeadways(self, bus, sameRoute=True):
        follower = self.getFollower(bus, sameRoute=sameRoute)
        leader = self.getLeader(bus, sameRoute=sameRoute)

        #################################################################
        ###### CHECK FOR NONE HEADWAYS ##################################
        #################################################################

        backwardHeadway = self.getForwardHeadway(follower, bus)
        forwardHeadway = self.getForwardHeadway(bus, leader)

        return backwardHeadway, forwardHeadway

    # function that determines the follower bus of the provided bus
    def getFollower(self, bus, sameRoute=True):
        # follower bus with same route
        if sameRoute: 
            buses = [v[0] for v in self.currentVehicles if v[0].split(':')[0][-2] == traci.vehicle.getLine(bus)]
            i = buses.index(bus) # index of bus in currentVehicles
            if i + 1 == len(buses): # bus is the current last of the route, therefore it has no follower
                return None
            else: # follower is the next element of list since all buses keep their order as no overtaking is possible
                return buses[i + 1]
        # follower bus with different route
        else: 
            i = self.reachedSharedCorridor.index(bus) # reachedSharedCorridor is in order of travelling, thus use it instead of currentVehicles
            for b in self.reachedSharedCorridor[i:]:
                if b.split(':')[0][-2] != traci.vehicle.getLine(bus): # follower is most next element of the other route
                    return b
            # check if follower may have not yet reached the shared corridor (by checking journey section)
            buses = [v[0] for v in self.currentVehicles if v[0].split(':')[0][-2] != traci.vehicle.getLine(bus) and v[2] == -1]
            if len(buses) != 0: # follower is the first element
                return buses[0]
            # there is no follower
            return None
            
    # function that determines the leader bus of the provided bus
    def getLeader(self, bus, sameRoute=True):
        # leader bus with same route
        if sameRoute: 
            # get all active buses of route
            buses = [v[0] for v in self.currentVehicles if v[0].split(':')[0][-2] == traci.vehicle.getLine(bus)]
            i = buses.index(bus) # index of bus in currentVehicles
            if i == 0: # bus is the leader of the route, therefore it has no leader
                return None
            else: # leader is the previous element of list since all buses keep their order as no overtaking is possible 
                return buses[i - 1]
        # leader bus with different route
        else: 
            i = self.reachedSharedCorridor.index(bus) # reachedSharedCorridor is in order of travelling, thus use it instead of currentVehicles
            for b in reversed(self.reachedSharedCorridor[:i]):
                if b.split(':')[0][-2] != traci.vehicle.getLine(bus): # leader is the most previous element of the other route
                    return b 
            return None # there is no active leader from the other route

    def getForwardHeadway(self, follower, leader, sameRoute=True):
        ##### CHECK #####################################################################
        ##### IF BUS IS ARRIVING AT TERMINAL, IT WILL NOT HAVE A FORWARD HEADWAY ########
        ##### IF BUS IS LEAVING FROM TERMINAL, IT WILL NOT HAVE A BACKWARD HEADWAY ######
        #################################################################################

        if follower is None:
            if leader == 'bus_22:3.6' or leader == 'bus_43:3.7': # last bus of service, therefore return zero
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

            route = traci.simulation.findRoute(startTerminus, leaderEdge, vType='bus')
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

            route = traci.simulation.findRoute(followerEdge, finalTerminus, vType='bus')
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

        route = traci.simulation.findRoute(followerEdge, leaderEdge, vType='bus')
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