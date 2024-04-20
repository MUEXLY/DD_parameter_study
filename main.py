#!/bin/python3

# Automation Script (hyunsol@g.clemson.edu)

import sys, string, os, json
import numpy as np
import itertools

# add lib directory path
sys.path.insert(1,'./src')
import handleUserInput as ui
import initStudyParameters as ip
import checkExecFiles as ce
#import dataHandler as dh
import dirPathInit as di
import executeDD as exe
import initDataAcronyms as ia

#import initSimulation as IS

def main():
    ## Directory Paths
    # **************** YOU ALWAYS HAVE TO ADD "/" AT THE END OF EACH PATH **********************
    #modelibPath ='/home/anon/Documents/Research/Github/MoDELib2_Final/MoDELib2/'
    # read the config file
    with open('config.json') as f:
        data = json.load(f)
        for key, value in data.items():
            if key=='mainMoDELibDirectory':
                modelibPath = value
            elif key=='dataOutPutDirectory':
                outputPath = value
            elif key=='totalTimeSteps':
                totalTsteps = value
            elif key=='parametersToExplore':
                paramList = value.split()
            elif key=='paramtersToCouple':
                paramToCouple = value.split()
            else:
                continue;

    print(f'modelibPath: {modelibPath}')
    print(f'outputPath: {outputPath}')
    print(f'paramToCouple: {paramToCouple}')
    print(f'paramList: {paramList}')
    print(f'totalTsteps: {totalTsteps}')
    # Declare data output location
    #outPath = f'{modelibPath}tutorials/DislocationDynamics/{outFolderName}/'
    outPath = outputPath

    # select variables to study
    #userInput = ui.selectVariables();

    # Create a class object containing the list of the parameters to study, based on the user inputs
    studyRange = ip.setTestRange(paramList)

    print(f'studyRange: {studyRange}')
    exit()
    # Run simulations
    # initialize all necessary directory paths
    simPath, refinputPath, microstructLibPath, DDompPath, microGenPath = di.dirPathInit(modelibPath)

    changeParameters

    # Check if there are the compiled executable files of microstructureGenerator and DDomp
    ce.checkExecFiles(DDompPath, microGenPath)

    # delete old reference input files if there is any
    if os.path.exists(refinputPath):
        os.system('rm -r {refinputPath}')

    # Generate the reference input files
    # This is implemented so that the initial config of the inputfiles can be preserved
    #dh.genReferenceFiles(refinputPath, simPath)
    os.system(f'mkdir -p {refinputPath}')
    os.system(f'cp -r {simPath}inputFiles/* {refinputPath}')

    # copy reference input files to input files folder
    #os.system('cp -r '+refinputPath+'* '+simPath+'inputFiles/')
    os.system(f'cp -r {refinputPath}* {simPath}inputFiles/')

    # Delete the old simulation results if there is any
    #dh.delOldEvlandF(simPath)
    if os.path.exists(f'{simPath}F'):
        os.system(f'rm -rf {simPath}F')
    if os.path.exists(f'{simPath}evl'):
        os.system('rm -rf {simPath}evl')
    
    # initialize the selected study parameters as a list of acronyms
    datAcronym = ia.initDataAcronyms(userInput)

    # delete old/failed simulation files
    if os.path.exists(outPath):
        os.system(f'rm -r {outPath}')

    # write acronym information in the output path
    ui.writeAcronymInfo(outPath)

    # save the test range file in the data output directory
    os.system(f"cp ./src/testRange.py {outPath}")


    # Run simulations for every possible combinations
    polyCrystalSetup = {'lattice': 'fcc', 'partial': 1}
    # pivot variable used as blacklist variable
    CRSSdetectSetup = {'on': True, 'pivot': 'IES', 'extStress': 's13'}
    exe.executeDD(modelibPath, outPath, simPath, microstructLibPath, studyRange, datAcronym, polyCrystalSetup, CRSSdetectSetup, pairRun=0)

if __name__=='__main__':
    main()
