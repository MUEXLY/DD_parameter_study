#!/bin/python3

import numpy as np
import re, sys, os, itertools
import GeneratePolyCrystalFile as GPC
import changeParameter as CP
import testRange as TR
from dataclasses import dataclass


def runSimulations(modelibPath, outPath, userInput, inputRange):
    # initialize all necessary directory paths
    simPath, refinputPath, microstructLibPath, DDompPath, microGenPath = dirPathInit(modelibPath)
    
    # Check if there are the compiled executable files of microstructureGenerator and DDomp
    checkExecFiles(DDompPath, microGenPath)

    # delete old reference input files if there is any
    delOldReferenceFiles(refinputPath)

    # Generate the reference input files
    # This is implemented so that the initial config of the inputfiles can be preserved
    genReferenceFiles(refinputPath, simPath)

    # copy reference input files to input files folder
    os.system('cp -r '+refinputPath+'* '+simPath+'inputFiles/')

    # Delete the old simulation results if there is any
    delOldEvlandF(simPath)
    
    # initialize the selected study parameters as a list of acronyms
    datAcronym = initDataAcronyms(userInput, inputRange)

    # Run simulations for every possible combinations
    executeDD(modelibPath, outPath, simPath, microstructLibPath, inputRange, datAcronym)
