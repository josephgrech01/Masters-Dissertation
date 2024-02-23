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
        setStop(newPersons)
        # remove the persons that have arrived from the dictionary
        arrived = traci.simulation.getArrivedPersonIDList()
        updateTrips(arrived)



        step += 1

    traci.close()

# function that creates the trip for the newly departed passengers
# person ids must be in the form 'BOARDINGSTOP.BUSLINE.TIMESTEP'
# df contains the probabilities of the alighting bus stops 
def setStop(persons, df):
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
        
        # randomly choose alighting bus stop according to the weights
        alightingStop = random.choices(possibleStops, weights=stopWeights)
        
        if alightingStop != 'other':
            # set the passenger's alighting stop
            alightLane = traci.busstop.getLaneID(alightingStop)
            alightEdge = traci.lane.getEdgeID(alightLane)

            traci.person.appendDrivingStage(person, alightEdge, line, stopID=alightingStop)
        else:
            # IMPLEMENT CASE WHERE ALIGHTINGSTOP = 'OTHER'
            pass

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
