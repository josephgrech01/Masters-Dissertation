#!/usr/bin/env python

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

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                        default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

trips = {} # dictionary to store the destination bus stop of a passenger
lines = {}
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
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(step)

        newV = traci.simulation.getDepartedIDList()
        newVehicles = []
        for v in newV:
            traci.vehicle.subscribe(v, [traci.constants.VAR_NEXT_STOPS])
            newVehicles.append([v, None])
            print("New Vehicle: {}".format(v))
        currentVehicles.extend(newVehicles)
        

        # create the trip for the newly departed passengers
        newPersons = traci.simulation.getDepartedPersonIDList()
        setStop(newPersons, {}) ####################### PROVIDE ACTUAL DF #################
        # remove the persons that have arrived from the dictionary
        arrived = traci.simulation.getArrivedPersonIDList()
        updateTrips(arrived)

        #### SET STOP DURATION IN ROUTE FILE TO 1 SECOND AT EACH STOP  ################################


        step += 1

    traci.close()

# function that creates the trip for the newly departed passengers
# person ids must be in the form 'BOARDINGSTOP.BUSLINE.TIMESTEP'
# df contains the probabilities of the alighting bus stops 
def setStop(persons, df):
    # route22 = [] ##################### NEED TO MOVE THESE OUT FROM THE FUNCTION
    # route43 = [] ##################### NEED TO MOVE THESE OUT FROM THE FUNCTION
    for person in persons:
        # extract boarding stop and line from passenger id
        boardingStop = person.split('.')[0] 
        line = person.split('.')[1]

        # extract all records relating to the boarding stop
        temp = df[df['Boarding Stop'] == boardingStop]
        possibleStops = temp['Alighting Stop'].tolist()
        stopWeights = temp['Total'].tolist()
        # give some small weight to the unmentioned stops
        possibleStops.append('other')
        stopWeights.append('0.1')
        
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

def updateTrips(arrived):
    for p in arrived:
        trips.pop(p)



if __name__ == "__main__":
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    traci.start([sumoBinary, "-c", "singapore/singapore.sumo.cfg"])
    run()
