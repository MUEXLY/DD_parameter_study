#!/bin/python3

import sys, os, json
# add lib directory path
sys.path.insert(1,'./src')
import initStructure as init
import simulationRun as sim
from testRange import *
#from src import initStructure


def main():
    # parse config file
    configFile = "config.json"
    with open(configFile) as f:
        config = json.load(f)
    modelibPath = config['mainMoDELibDirectory']
    outputPath = config['dataOutPutDirectory']
    totalTsteps = config['totalTimeSteps']
    paramToCouple = config['paramtersToCouple']
    microStructure = config['microstructureFileToUse']
    partial = config['enablePartial']
    #paramList = config['parametersToExplore']
    #materialFile = config['materialFileToUse']

    structure = init.structure(config)
    structure.modifyInitMicrostructure()
    #structure.changeMaterial()

    #initConfig = initializeConfig()
    ddRun = sim.dislocationDynamicsRun(structure, testRange)
    #ddRun.checkExecutables()
    ddRun.exploreAllParams()

    # To do
    # 1. remove the manual stress range setting, just implement an algo that test small and jump to big, and step back to small

    #analyzer = resultsAnalyzer()
    #analyzer.plotCRSS()

    return 0;

if __name__ == "__main__":
    main()
