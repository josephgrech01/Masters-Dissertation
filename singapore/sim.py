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

def setStop(person):
    pass

def updateTrips(arrived):
    pass



if __name__ == "__main__":
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo')#-gui')

    traci.start([sumoBinary, "-c", "singapore/singapore.sumo.cfg"])
    run()
