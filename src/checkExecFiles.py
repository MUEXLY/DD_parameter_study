#!/bin/python3

import os

def checkExecFiles(DDompPath, microGenPath):
    if not os.path.isfile(microGenPath + "/build/microstructureGenerator"):
        exit("There is no MicrostructureGenerator executable file")
    if not os.path.isfile(DDompPath + "/build/DDomp"):
        exit("There is no DDomp executable file")
