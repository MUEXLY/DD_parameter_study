#!/bin/python3

import numpy as np
import re, sys, os, itertools
import GeneratePolyCrystalFile as GPC
import changeParameter as CP
import testRange as TR
from dataclasses import dataclass

@dataclass
class initSim:
    # class object args
    lattice : str
    extStress : str  
    partial : int = 0
    pairRun : int = 0
    detectCRSS : int = 0
    
    #(***************** runSImlulation commands go to main file
    def runSimulations(self, modelibPath, outPath, userInput, inputRange):
        # initialize all necessary directory paths
        simPath, refinputPath, microstructLibPath, DDompPath, microGenPath = self.dirPathInit(modelibPath)
        
        # Check if there are the compiled executable files of microstructureGenerator and DDomp
        self.checkExecFiles(DDompPath, microGenPath)

        # delete old reference input files if there is any
        self.delOldReferenceFiles(refinputPath)

        # Generate the reference input files
        # This is implemented so that the initial config of the inputfiles can be preserved
        self.genReferenceFiles(refinputPath, simPath)

        # copy reference input files to input files folder
        os.system('cp -r '+refinputPath+'* '+simPath+'inputFiles/')

        # Delete the old simulation results if there is any
        self.delOldEvlandF(simPath)
        
        # initialize the selected study parameters as a list of acronyms
        datAcronym = self.initDataAcronyms(userInput, inputRange)

        # Run simulations for every possible combinations
        self.executeDD(modelibPath, outPath, simPath, microstructLibPath, inputRange, datAcronym)

    def executeDD(self, modelibPath, outPath, simPath, microstructLibPath, inputRange, datAcronym):
        if self.pairRun:
            combinations = []
            for i in range(len(inputRange[0])):
                tupleList = (inputRange[0][i], inputRange[1][i])
                combinations.append(tupleList)
        else:
            combinations = list(itertools.product(*inputRange))

        for inputValue in combinations:
            # zip the acronyms and variable values as a dictionary
            dataDict = {k:v for k,v in zip(datAcronym, inputValue)}

            # Generate folder names based on the parameter values, this is purely for generating folder names
            dataOutputName = []
            for k, v in zip(datAcronym, inputValue):
                # If there is more than one value from the passed list of parameters, then just use the first value for the folder name
                if type(v)==list:
                    #v = v[0]
                    v = [str(x) for x in v]
                    v = '_'.join(v)
                dataOutputName.append(k+str(v))
            #dataOutputName = [k+str(v) for k,v in zip(datAcronym, inputValue)]
            dataOutputName = ''.join(dataOutputName)

            # Create F and evl folders 
            self.createEvlandFfolder(simPath)

            #just regenerate both inputfiles and polycrystalfile for every loop (temp solution)
            Crystal = GPC.PolyCrystalFile(polyOutPath=simPath, modelibPath=modelibPath, dataDict=dataDict)
            Crystal.generate(self.lattice, self.partial)

            # change parameter
            CP.changeParameter(simPath, dataDict)

            # Run microstructure Generator
            self.runMicrostructureGen(modelibPath, simPath, debugFlag=0)

            # Run simulation
            self.runDDomp(modelibPath, simPath, debugFlag=0)
                
            # Make the full directory path as a variable
            dataFullNamePath = outPath+dataOutputName

            # Generate the data directory if it doest exist
            if not os.path.exists(dataFullNamePath):
                os.makedirs(dataFullNamePath)

            # Copy the simulation data to the data directory
            os.system('cp -r '+simPath+'F '+dataFullNamePath)
            os.system('cp -r '+simPath+'evl '+dataFullNamePath)

            # Copy modified inputFiles to the data directory
            os.system('cp -r '+simPath+'inputFiles '+dataFullNamePath)
            os.system('cp '+microstructLibPath+'periodicDipole.txt '+dataFullNamePath)

            # check if CRSS is reached (if this option is enabled)
            if self.detectCRSS:
                timeColIndex = 1
                match self.extStress:
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
                #x_data = np.loadtxt(f'{simPath}/F/F_0.txt', usecols=timeColIndex)
                y_data = np.loadtxt(f'{simPath}/F/F_0.txt', usecols=bPIndex)
                maxIndex = len(y_data)-1
                thresholdIndex = int(maxIndex*0.8)
                slope = (y_data[maxIndex] - y_data[thresholdIndex])
                # remove the seed number once it reached CRSS
                if slope > 1e-05:
                    # find what is seed number in inputValue
                    seedNum = [ x for x in inputValue if x in TR.seeds ][0] #convert list to just a integer
                    # remove the testlists that contains the seed number from the list of "combinations" (since it reached CRSS)
                    combinations = [ x for x in combinations if not seedNum in x ] 
                    continue;

            # Remove the simulation data at the end of each loop
            os.system('rm -r '+simPath+'F')
            os.system('rm -r '+simPath+'evl')

    def delOldEvlandF(self, simPath):
        if os.path.exists(simPath+'F'):
            os.system('rm -rf '+simPath+'F')
        if os.path.exists(simPath+'evl'):
            os.system('rm -rf '+simPath+'evl')

    def createEvlandFfolder(self, simPath):
        if not os.path.exists(simPath+'F'):
            os.system('mkdir -p '+simPath+'F')
        if not os.path.exists(simPath+'evl'):
            os.system('mkdir -p '+simPath+'evl')

    def delOldReferenceFiles(self, refinputPath):
        if os.path.exists(refinputPath):
            os.system('rm -r '+refinputPath)

    def genReferenceFiles(self, refinputPath, simPath):
        os.system('mkdir -p '+refinputPath)
        os.system('cp -r '+simPath+'inputFiles/* ' +refinputPath)

    def runDDomp(self, modelibPath, simPath, debugFlag):
        if debugFlag:
            print('Running DDomp...')
            print('debugFlag = '+str(debugFlag))
            print('ModeLib Folder Path = '+modelibPath)
            print('Simulation Folder Path = '+simPath)
        os.system(modelibPath+'tools/DDomp/build/DDomp '+simPath)

    def runMicrostructureGen(self, modelibPath, simPath, debugFlag=0):
        if debugFlag:
            print('Running microstructure generator...')
            print('debugFlag = '+str(debugFlag))
            print('ModeLib Folder Path = '+modelibPath)
            print('Simulation Folder Path = '+simPath)
        os.system(modelibPath+'tools/MicrostructureGenerator/build/microstructureGenerator '+simPath)

    def dirPathInit(self, modelibPath):
        simPath = modelibPath + 'tutorials/DislocationDynamics/periodicDomains/uniformLoadController' + '/'
        refinputPath = simPath + 'referenceInputFiles' + '/'
        microstructLibPath = modelibPath + 'tutorials/DislocationDynamics/MicrostructureLibrary' + '/'
        #outPath = modelibPath +'tutorials/DislocationDynamics/AutoProducedData/' # Data output location
        DDompPath = modelibPath + 'tools/DDomp' + '/'
        microGenPath = modelibPath + 'tools/MicrostructureGenerator' + '/'
        return simPath, refinputPath, microstructLibPath, DDompPath, microGenPath;

    def checkExecFiles(self, DDompPath, microGenPath):
        if not os.path.isfile(microGenPath + "/build/microstructureGenerator"):
            exit("There is no MicrostructureGenerator executable file")
        if not os.path.isfile(DDompPath + "/build/DDomp"):
            exit("There is no DDomp executable file")

    def initDataAcronyms(self, userInput, inputRange):
        datAcronym = []
        for i in range(len(userInput)):
            match userInput[i]:
                case '1':
                    acronym = 'T'
                case '2':
                    acronym = 'DL'
                case '3':
                    acronym = 'DD'
                case '4':
                    acronym = 'C'
                case '5':
                    acronym = 'DC'
                case '6':
                    acronym = 'L'
                case '7':
                    acronym = 'GP'
                case '8':
                    acronym = 'RF'
                case '9':
                    acronym = 'DCT'
                case '10':
                    acronym = 'SR'
                case '11':
                    acronym = 'S'
                case '12':
                    acronym = 'DP'
                case '13':
                    acronym = 'DG'
                case '14':
                    acronym = 'LMAX'
                case '15':
                    acronym = 'IES'
                case '16':
                    acronym = 'SS'
                case '17':
                    acronym = 'SF'
                case '18':
                    acronym = 'GS'
                case _:
                    print('Something is wrong')
                    exit()
            datAcronym.append(acronym)
        return datAcronym;


