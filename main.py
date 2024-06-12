#!/bin/python3

import sys, json
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

    structure = init.structure(config)
    _ = structure.modifyInitMicrostructure()

    #initConfig = initializeConfig()
    ddRun = sim.dislocationDynamicsRun(structure, testRange)
    #ddRun.checkExecutables()
    _ = ddRun.exploreAllParams()

    return 0;

if __name__ == "__main__":
    _ = main()
