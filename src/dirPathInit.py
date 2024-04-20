#!/bin/python3

import sys, string, os
import numpy as np
import itertools

def dirPathInit(modelibPath):
    simPath = modelibPath + 'tutorials/DislocationDynamics/periodicDomains/uniformLoadController' + '/'
    refinputPath = simPath + 'referenceInputFiles' + '/'
    microstructLibPath = modelibPath + 'tutorials/DislocationDynamics/MicrostructureLibrary' + '/'
    #outPath = modelibPath +'tutorials/DislocationDynamics/AutoProducedData/' # Data output location
    DDompPath = modelibPath + 'tools/DDomp' + '/'
    microGenPath = modelibPath + 'tools/MicrostructureGenerator' + '/'

    return simPath, refinputPath, microstructLibPath, DDompPath, microGenPath;
