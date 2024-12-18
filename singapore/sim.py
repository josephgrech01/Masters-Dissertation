import os
import sys
import optparse

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary
import traci
import random
import pandas as pd

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                        default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

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

print('Len route 22: {}'.format(len(route22)))
print('Len route 43: {}'.format(len(route43)))

def run():
    step = 0
    currentVehicles = []
    hour = 6
    
    df22 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(hour),'route22.csv'))
    df43 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(hour),'route43.csv'))
    addPassengers(df22, df43, hour)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print('Step: {}'.format(step), end="\r")
        time = traci.simulation.getTime()

        if getHour(time) != hour:
            hour = getHour(time)
            # load the demand data for the current hour
            df22 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(hour),'route22.csv'))
            df43 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(hour),'route43.csv'))
            # add the passengers for the coming hour
            addPassengers(df22, df43, hour)

        # keep track of vehicles active in the simulation
        newV = traci.simulation.getDepartedIDList()
        newVehicles = []
        for v in newV:
            traci.vehicle.subscribe(v, [traci.constants.VAR_NEXT_STOPS])
            newVehicles.append([v, None])
            print("New Vehicle: {}".format(v))
        currentVehicles.extend(newVehicles)
        
        # create the trip for the newly departed passengers
        newPersons = traci.simulation.getDepartedPersonIDList()
        setStop(newPersons, df22, df43)
        # remove the persons that have arrived from the dictionary
        arrived = traci.simulation.getArrivedPersonIDList()
        updateTrips(arrived)

        removeVehicles = []
        # checking which buses have arrived at a stop 
        for v in currentVehicles:
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
                                # check if the bus should stop
                                if not shouldStop(v[0], stopId):
                                    traci.vehicle.setBusStop(v[0], stopId, duration=0) # stopping duration set to zero
                                # else stop normally
        
        # removing the vehicles that have ended their journey
        for v in removeVehicles:
            for x in currentVehicles:
                if v == x[0]:
                    currentVehicles.remove(x)

        if step % 1000 == 0 and step != 0:
            if len(currentVehicles) > 1:
                print('curreVehicles: {}'.format(currentVehicles))
                veh1 = currentVehicles[1][0]
                lane1 = traci.vehicle.getLaneID(veh1)
                edge1 = traci.lane.getEdgeID(lane1)
                lanePos1 = traci.vehicle.getLanePosition(veh1)
                
                veh2 = currentVehicles[0][0]
                lane2 = traci.vehicle.getLaneID(veh2)
                edge2 = traci.lane.getEdgeID(lane2)
                len2 = traci.lane.getLength(lane2)
                lanePos2 = traci.vehicle.getLanePosition(veh2)

                headway = traci.simulation.getDistanceRoad(edge1, lanePos1, edge2, lanePos2, isDriving=True)
                
                print('veh1: {}'.format(veh1))
                print('edge1: {}'.format(edge1))
                print('veh2: {}'.format(veh2))
                print('edge2: {}'.format(edge2))
                print('HEADWAY: {}'.format(headway))

                route = traci.simulation.findRoute(edge1, edge2, vType='bus')
                actual = route.length - lanePos1 - (len2 - lanePos2)

                print('LENGTH: {}'.format(route.length))

                print("speed 1: {}".format(traci.vehicle.getSpeed(veh1)))
                print("speed 2: {}".format(traci.vehicle.getSpeed(veh2)))
                print('ACTUAL LENGTH: {}'.format(actual))

                print('USING FUNCTION: {}'.format(getForwardHeadway(veh1, veh2)))
            else:
                print("CURRENTLY ONLY 1 VEHICLES IN SIM")

        step += 1

    traci.close()

# function that adds the passengers into the simulation for the coming hour
def addPassengers(df22, df43, hour):
    routes = [route22, route43]
    currTime = traci.simulation.getTime()
    for index, route in enumerate(routes):
        if index == 0:
            df = df22
            line = '22'
        else:
            df = df43
            line = '43'

        # iterate over each route's bus stop
        for stop in route: 
            temp = df[df['Boarding Stop'] == int(stop)]
            if len(temp.index) != 0:
                total = temp['Total'].sum() # total number of persons that arrive at this stop in the hour
                departures = getDepartures(total, hour)

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
def getDepartures(rate, hour):
    lambdaVvalue = rate / 3600 # per second
    totalTime = 3600
    if hour == 6:
        totalTime = 1800 # from 6.30 to 7 am, simulation starts at 6.30 and not 6.00
    departures = []
    currentTime = 0

    # keep adding passengers until the last departure that does not exceed an hour 
    while currentTime < totalTime:
        interval = random.expovariate(lambdaVvalue) # Poisson distribution
        currentTime += interval

        if currentTime < totalTime:
            departures.append(str(int(currentTime)))

    return departures # return as a list of strings, as required by the 'addPassengers' function

# function that creates the trip for the newly departed passengers
# person ids must be in the form 'BOARDINGSTOP.BUSLINE.TIMESTEP'
# df22 and df43 contains the probabilities of the alighting bus stops 
def setStop(persons, df22, df43):
    for person in persons:
        # extract boarding stop and line from passenger id
        boardingStop = person.split('.')[0] 
        line = person.split('.')[1]

        if line == '22':
            df = df22
        else:
            df = df43

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
def shouldStop(bus, stop):
    # check if any of the passengers on the bus want to alight at the stop
    for p in traci.vehicle.getPersonIDList(bus):
        if trips[p] == stop:
            return True
    # check if any of the persons waiting at the stop want to board this bus line
    busLine = traci.vehicle.getLine(bus)
    for p in traci.busstop.getPersonIDs(stop):
        passengerLine = p.split('.')[1]
        if passengerLine == busLine:
            return True
    # bus does not need to stop
    return False

def updateTrips(arrived):
    for p in arrived:
        trips.pop(p) # remove finished trip from dictionary

def getForwardHeadway(follower, leader):
    followerLane = traci.vehicle.getLaneID(follower)
    followerPosition = traci.vehicle.getLanePosition(follower)
    followerEdge = traci.lane.getEdgeID(followerLane)
    
    leaderLane = traci.vehicle.getLaneID(leader)
    leaderPosition = traci.vehicle.getLanePosition(leader)
    leaderLaneLength = traci.lane.getLength(leaderLane)
    leaderEdge = traci.lane.getEdgeID(leaderLane)

    route = traci.simulation.findRoute(followerEdge, leaderEdge, vType='bus')
    headway = route.length - followerPosition - (leaderLaneLength - leaderPosition)

    return headway

def getHour(time):
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



if __name__ == "__main__":
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    traci.start([sumoBinary, "-c", "singapore/singapore.sumo.cfg"])
    run()
