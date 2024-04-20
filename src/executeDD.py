#!/bin/python3

import os
import itertools
import numpy as np
import dataHandler as dh
import GeneratePolyCrystalFile as gp
import changeParameter as cp
import detectCRSS as tc
import runEXEs as re
import testRange as tr
import recordCRSS as rc

def ifResetBlackList(previousC, currentC, blackList):
    #reset seed blacklist
    if previousC != currentC:
        # reset blacklist
        blackList = []
    return blackList;

def returnConcent(previousC, dataDict):
    for key, value in dataDict.items():
        # changes the current concentration on each loop
        if key=='C':
            currentC = value
            break;
    return currentC;

def ignoreCRSSpivot(blackList, dataDict, Pivot):
    # find the current pivot in the loop
    for key, value in dataDict.items():
        if key == Pivot:
            currentPivot = value
            break;

    # if the value is in the list, return true
    if currentPivot in blackList:
        return True;

def executeDD(modelibPath, outPath, simPath, microstructLibPath, studyRange, datAcronym, polyCrystalSetup, CRSSdetectSetup, pairRun=0):
    if pairRun:
        combinations = []
        for i in range(len(studyRange[0])):
            tupleList = (studyRange[0][i], studyRange[1][i])
            combinations.append(tupleList)
    else:
        combinations = list(itertools.product(*studyRange))

    blackList = []
    previousC = None
    for inputValue in combinations:

        # zip the acronyms and variable values as a dictionary
        dataDict = {k:v for k,v in zip(datAcronym, inputValue)}

        # Check if there is a change in concentration, if there is, reset the seed blacklist
        currentC = returnConcent(previousC, dataDict)
        if previousC != None:
            blackList = ifResetBlackList(previousC, currentC, blackList)
        previousC = currentC

        # blacklist the seed number that already showed CRSS
        # meaning, just continue to the next seed
        if ignoreCRSSpivot(blackList, dataDict, CRSSdetectSetup['pivot']):
            continue;

        # Generate folder names based on the parameter values, this is purely for generating folder names
        dataOutputName = []
        for k, v in zip(datAcronym, inputValue):
            # If there is more than one value from the passed list of parameters, then just use the first value for the folder name
            if type(v)==list:
                #v = v[0]
                v = [str(x) for x in v]
                v = '_'.join(v)
            dataOutputName.append(k+str(v))
        dataOutputName = ''.join(dataOutputName)

        # Create F and evl folders 
        dh.createEvlandFfolder(simPath)

        #just regenerate both inputfiles and polycrystalfile for every loop (temp solution)
        Crystal = gp.PolyCrystalFile(polyOutPath=simPath, modelibPath=modelibPath, dataDict=dataDict)
        Crystal.generate(lattice=polyCrystalSetup['lattice'], partialMode=polyCrystalSetup['partial'])

        # change parameter
        cp.changeParameter(simPath, dataDict)

        # Run microstructure Generator
        re.runMicrostructGen(modelibPath, simPath, dataDict, debugFlag=0)

        # Run simulation
        re.runDDomp(modelibPath, simPath, debugFlag=0)

        # Kill this automation script if the simulation wasn't completed
        #kill

        # Make the full directory path as a variable
        dataFullNamePath = outPath+dataOutputName

        # Generate the data directory
        if not os.path.exists(dataFullNamePath):
            os.system(f'mkdir -p {dataFullNamePath}')

        # Copy the simulation data to the data directory
        #os.system('cp -r '+simPath+'F '+dataFullNamePath)
        #os.system('cp -r '+simPath+'evl '+dataFullNamePath)
        os.system(f'cp -r {simPath}F {dataFullNamePath}')
        os.system(f'cp -r {simPath}evl {dataFullNamePath}')

        # Copy modified inputFiles to the data directory
        os.system(f'cp -r {simPath}inputFiles {dataFullNamePath}')
        os.system(f'cp {microstructLibPath}periodicDipole.txt {dataFullNamePath}')

        # check if CRSS is reached (if this option is enabled)
        if CRSSdetectSetup['on']:
            timeColIndex = 1
            match CRSSdetectSetup['extStress']:
                case 's11':
                    bPIndex = 3
                case 's12':
                    bPIndex = 4
                case 's13':
                    bPIndex = 5
                case 's21':
                    bPIndex = 6
                case 's22':
                    bPIndex = 7
                case 's23':
                    bPIndex = 8
                case 's31':
                    bPIndex = 9
                case 's32':
                    bPIndex = 10
                case 's33':
                    bPIndex = 11
            # load F data to compare
            times, y_data = tc.loadData(f'{simPath}', bPIndex)
            # calculate the first derivative
            firstDiff = tc.calc1stDiff(times, y_data)
            # judge if CRSS is reached or not
            CRSSswitch = tc.detectCRSS(firstDiff)
            if CRSSswitch:
                # find what is seed number in inputValue
                pivotVal = dataDict[CRSSdetectSetup['pivot']] #convert list to just a integer
                # add the seed number on the blacklist to skip the simulation
                blackList.append(pivotVal)
                # record CRSS as a separate text data
                rc.recordCRSS(outPath, dataDict)

        # Remove the simulation data at the end of each loop
        os.system(f'rm -r {simPath}F')
        os.system(f'rm -r {simPath}evl')
