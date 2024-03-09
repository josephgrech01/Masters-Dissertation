from pettingzoo import AECEnv
import os
import sys
from sumolib import checkBinary
import traci
import random
import pandas as pd


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

class sumoMultiLine(AECEnv):
    def __init__(self, gui=False):
        super().__init__()
        self.agents = []
        self.agent_states =  {} # dictionary to store the state of each agent
        # self.envStep = 0
        self.currentVehicles = []
        self.hour = 6
        
        self.df22 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route22.csv'))
        self.df43 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route43.csv'))
        self.addPassengers(self.df22, self.df43, self.hour)

        if gui:
            self.sumoBinary = checkBinary('sumo-gui')
        else:
            self.sumoBinary = checkBinary('sumo')

        self.sumoCmd = [self.sumoBinary, '-c', 'singapore/singapore.sumo.cfg', '--tripinfo-output', 'tripinfo.xml', '--no-internal-links', 'false', '--lanechange.overtake-right', 'true']

        traci.start(self.sumoCmd)


    def step(self, actions):
        for agent in self.agents:
            pass
            # IMPLEMENT APPLICATION OF ACTION




    def sumoStep(self):
        traci.simulationStep()
        time = traci.simulation.getTime()

        if self.getHour(time) != self.hour:
            self.hour = self.getHour(time)
            # load the demand data for the current hour
            self.df22 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route22.csv'))
            self.df43 = pd.read_csv(os.path.join('singapore','demand','byHour','hour'+str(self.hour),'route43.csv'))
            # add the passengers for the coming hour
            self.addPassengers(self.df22, self.df43, self.hour)
        
        # keep track of vehicles active in the simulation
        newV = traci.simulation.getDepartedIDList()
        newVehicles = []
        for v in newV:
            traci.vehicle.subscribe(v, [traci.constants.VAR_NEXT_STOPS])
            newVehicles.append([v, None])
            print("New Vehicle: {}".format(v))
        self.currentVehicles.extend(newVehicles)
        #########################################################################
        ###################### ADD AGENTS #######################################
        #########################################################################
        # create the trip for the newly departed passengers
        newPersons = traci.simulation.getDepartedPersonIDList()
        self.setStop(newPersons, self.df22, self.df43)
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
                                # check if the bus should stop
                                if not self.shouldStop(v[0], stopId):
                                    traci.vehicle.setBusStop(v[0], stopId, duration=0) # stopping duration set to zero
                                # else stop normally

        ############################################################################################################
        ###################### UPDATE GLOBAL LIST OF WHICH BUSES SHOULD STOP #######################################
        ############################################################################################################
        
        # removing the vehicles that have ended their journey
        for v in removeVehicles:
            for x in self.currentVehicles:
                if v == x[0]:
                    self.currentVehicles.remove(x)

        #########################################################################
        ###################### REMOVE AGENTS #######################################
        #########################################################################


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