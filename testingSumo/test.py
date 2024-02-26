import os
import sys
import optparse
from sumolib import checkBinary
import traci
import random

stopEdge = [3, 4, 5, 6, 7]
stops = [[1,3,4], [3,4], [3], [4]] #stops accessible from that stop
trips = {} #dictionary to store the destination bus stop of a passenger
lines = [[0,4], [2,3], [0,1,3,4]]

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare enviornment variable 'SUMO_HOME'")

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                        default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

def run():
    step = 0
    currentVehicles = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        new = traci.simulation.getDepartedIDList()
        newVehicles = []
        for v in new:
            traci.vehicle.subscribe(v, [traci.constants.VAR_NEXT_STOPS])
            newVehicles.append([v, None])
        currentVehicles.extend(newVehicles)

        # create the trip for the newly departed passengers
        newPersons = traci.simulation.getDepartedPersonIDList()
        setStop(newPersons)
        # remove the passengers that have arrived from the dictionary
        arrived = traci.simulation.getArrivedPersonIDList()
        updateTrips(arrived)

        removeVehicles = []
        for v in currentVehicles:
            results = traci.vehicle.getSubscriptionResults(v[0])
            next_stop = results.get(traci.constants.VAR_NEXT_STOPS, None)
            print("Results:\n", results)
            print("Next_stop:\n", next_stop)
            # bus has no more stops left and should be removed
            if len(next_stop) == 0:
                removeVehicles.append(v[0])
            else:
                stop = next_stop[0][2]
                # print("v[1]: ", v[1], " stop: ", stop)
                
                if traci.busstop.getLaneID(stop) == traci.vehicle.getLaneID(v[0]):
                    if traci.vehicle.getLanePosition(v[0]) >= (traci.busstop.getStartPos(stop) - 1):
                        if not traci.vehicle.isStopped(v[0]):
                            print("bus " + v[0] + " stop " + stop)
                            if v[1] != stop:
                                v[1] = stop
                                # check if the bus should stop
                                if not shouldStop(v[0], stop): 
                                    traci.vehicle.setBusStop(v[0], stop, duration=0)
                                    print("Not stopping!")
                                else:
                                    print("Stopping!")
                                    # if traci.vehicle.getPersonNumber(v[0]) != 0:
                                    #     traci.vehicle.setStopParameter(v[0], 0, "line", "9")
                                    #     print("CHANGING LINE: ", traci.vehicle.getLine(v[0]))
                                    # for p in traci.busstop.getPersonIDs(stop):
                                    #     traci.vehicle.refuseBoarding(p)
                                    #     print("refusing boarding")
                                    
            # print(next_stop)
        for v in removeVehicles:
            for x in currentVehicles:
                if v == x[0]:
                    currentVehicles.remove(x)
        # print("Current Vehicles: ", currentVehicles)

        
        step += 1

    traci.close()
    sys.stdout.flush()

def setStop(persons):
    for person in persons:
        stop = int(traci.person.getRoadID(person)[1:]) - 3
        r = random.randint(0, len(stops[stop]) - 1)
        s = stops[stop][r]

        # num = random.randint(1,4)
        newEdge = "E" + str(stopEdge[s])
        newStop = "bs_" + str(s)
        traci.person.appendDrivingStage(person, newEdge, "ANY", stopID=newStop)
        traci.person.appendWalkingStage(person, [newEdge], 25)

        # trips[person] = newEdge
        trips[person] = newStop

def updateTrips(arrived):
    for p in arrived:
        trips.pop(p)

def shouldStop(bus, stop):
    for p in traci.vehicle.getPersonIDList(bus):
        if trips[p] == stop:
            return True
    for p in traci.busstop.getPersonIDs(stop):
        destination = trips[p]
        line = int(traci.vehicle.getLine(bus))
        # print("destination[3:]: "+destination[3:])
        # print("line: "+str(line))
        # print("lines[line]: ")
        # print(lines[line])
        if int(destination[3:]) in lines[line]:
            # print("about to return true")
            return True
    # print("about to return false")
    return False



if __name__ == "__main__":
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    
    traci.start([sumoBinary, "-c", "testingSumo/test.sumocfg", "--tripinfo-output", "testTripInfo.xml"])
    run()

