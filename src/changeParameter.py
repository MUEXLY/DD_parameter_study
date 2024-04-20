#!/bin/python3

import re 
import os

# take the dictionary list as the function argument
def changeParameter(simFolderPath, dataDict):
    inputFilesPath = simFolderPath+'inputFiles/'
    MicrostructureLibaryPath = simFolderPath+'../../MicrostructureLibrary/'
    for key, value in dataDict.items():
        changingDic = {}
        match key:
            case 'T':
                pattern = 'absoluteTemperature.*'
                replace = 'absoluteTemperature = ' +str(value)+';'
                filePath = inputFilesPath+'polycrystal.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'C':
                pattern = 'materialFile.*'
                replace = 'materialFile=../../../MaterialsLibrary/AlMg'+str(value)+'.txt;'
                filePath = inputFilesPath+'polycrystal.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)
                value2 = 0 
                #filePath2 = inputFilesPath+'uniformExternalLoadController.txt'
                #pattern2 = 'ExternalStress0.*'
                #replace2 = 'ExternalStress0 = 0.0 0.0 '+str(value2)+' 0.0 0.0 0.0 '+str(value2)+' 0.0 0.0;'
                #changingDic[filePath2] = []
                #pair2 = [pattern2, replace2]
                #changingDic[filePath2].append(pair2)

            case 'DC':
                pattern = 'periodicDipoleExitFaceIDs.*'
                replace = 'periodicDipoleExitFaceIDs='+str(value)+';' # 0: screw, 1: edge
                filePath = MicrostructureLibaryPath+'periodicDipole.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'DD':
                pattern = 'periodicDipoleHeights.*'
                replace = 'periodicDipoleHeights='+str(value)+';'
                filePath = MicrostructureLibaryPath+'periodicDipole.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'L':
                pattern = 'use_stochasticForce.*'
                replace = 'use_stochasticForce=' +str(value)+';'
                filePath = inputFilesPath+'DD.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'GP':
                pattern = 'quadPerLength.*'
                replace = 'quadPerLength=' +str(value)+';'
                filePath = inputFilesPath+'DD.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)
            
            case 'RF':
                pattern = 'remeshFrequency.*'
                replace = 'remeshFrequency=' +str(value)+';'
                filePath = inputFilesPath+'DD.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'DN':
                pattern = 'periodicDipoleNodes.*'
                replace = 'periodicDipoleNodes = '+str(value)+';'
                filePath = MicrostructureLibaryPath+'periodicDipole.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'SR':
                pattern = 'ExternalStressRate.*'
                replace = 'ExternalStressRate = '+'0.0 0.0 '+str(value)+' 0.0 0.0 0.0 '+str(value)+' 0.0 0.0;'
                filePath = inputFilesPath+'uniformExternalLoadController.txt' 
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'DP':
                pattern = 'periodicDipolePoints.*'
                replace = 'periodicDipolePoints='+str(value[0])+' '+str(value[1])+' '+str(value[2])+';'
                filePath = MicrostructureLibaryPath+'periodicDipole.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'DG':
                pattern = 'periodicDipoleGlideSteps.*'
                replace = f'periodicDipoleGlideSteps={value};'
                filePath = MicrostructureLibaryPath+'periodicDipole.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'LMAX':
                pattern = 'Lmax.*'
                replace = 'Lmax=' +str(value)+';'
                filePath = inputFilesPath+'DD.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'IES': 
                # initial external stress
                pattern = 'ExternalStress0.*'
                replace = 'ExternalStress0='+str(value[0])+' '+str(value[1])+' '+str(value[2])+' '+str(value[3])+' '+str(value[4])+' '+str(value[5])+' '+str(value[6])+' '+str(value[7])+' '+str(value[8])+';'
                filePath = inputFilesPath+'uniformExternalLoadController.txt' 
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

            case 'DG':
                pattern = 'periodicDipoleNodes.*'
                replace = f'periodicDipoleNodes={value};'
                filePath = MicrostructureLibaryPath+'periodicDipole.txt'
                changingDic[filePath] = []
                pair = [pattern, replace]
                changingDic[filePath].append(pair)

        for key, value in changingDic.items():
            dummyData = []
            filePath = key
            pattern = value[0][0]
            replace = value[0][1]
            # open the original data file
            with open(filePath,'r') as f:
                for line in f:
                    # compare the pattern line by line and if the line matches the pattern, replace it
                    dat = re.sub(pattern, replace, line)
                    # store data
                    dummyData.append(dat)
            # overwrite the original data file
            with open(filePath,'w') as g:
                for line in dummyData:
                    g.write(line)


