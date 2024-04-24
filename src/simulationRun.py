import json, re, os
import subprocess
import itertools
import shutil
import subprocess
import numpy as np
from dataclasses import dataclass

@dataclass
class dislocationDynamicsRun:
    structure: object
    testRange: dict

    def exploreAllParams(self) -> None:
        modelibPath = self.structure.configFile['mainMoDELibDirectory']
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
        forceFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/F/'
        outputPath = self.structure.configFile['dataOutPutDirectory']
        #paramList = self.structure.configFile['parametersToExplore']
        paramToCouple = self.structure.configFile['paramtersToCouple']
        timeStep = self.structure.configFile['totalTimeSteps']
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'
        microStructLibPath = f'{modelibPath}/tutorials/DislocationDynamics/MicrostructureLibrary'
        materialLibPath = f'{modelibPath}/tutorials/DislocationDynamics/MaterialsLibrary'
        externalLoadMode = self.structure.configFile['loadType']
        slipSystemType = self.structure.configFile['slipSystemType']

        # remove the dictionary emlements that are empty
        keysToRemove = [key for key,values in self.testRange.items() if not values] # keys to remove
        for key in keysToRemove: # remove the keys that has empty values
            del self.testRange[key]

        tempKeys = []
        tempArray = []
        # get the keys and values from the testRange dictionary
        for key, value in self.testRange.items():
            tempKeys.append(key)
            tempArray.append(value)

        # create a list of dictionaries for each simulation run
        paramDictList = []
        combinations = list(itertools.product(*tempArray))
        for comb in combinations:
            templateRunDict = {}
            for i, element in enumerate(comb):
                templateRunDict[tempKeys[i]] = element
            paramDictList.append(templateRunDict)

        # if there are parameters that need to be changed together, remove the list that doesn't fit the criteria
        #if paramToCouple:
        #    for run in runList:

        # copy reference input Files to the simulation working directory
        self.copyReferenceInputFiles(inputFilePath)

        # clean up the old data
        if os.path.exists(f'{workingSimPath}/F'):
            os.system(f'rm -rf {workingSimPath}/F')
        if os.path.exists(f'{workingSimPath}/evl'):
            os.system(f'rm -rf {workingSimPath}/evl')
        
        # run simulations with the parameters saved on each list
        # (?) do I need to clean up the old data automatically?
        for parameters in paramDictList:
            # change parameters
            self.changeParameters(parameters, modelibPath, inputFilePath, microStructLibPath)
            # if partial is enabled, make the change on the material file
            self.setSlipSystemType(parameters, materialLibPath, slipSystemType)
            exit()
            # set time step
            self.setTimeStep(timeStep, modelibPath, inputFilePath)
            # test various stress/stressRate/strain/strainRate
            CRSS = False
            sigma = 2e-05 # initial stress
            while not CRSS:
                # read the uniformExternalLoadController.txt file
                with open(f'{inputFilePath}/uniformExternalLoadController.txt', 'r') as file:
                    text = file.read()
                match externalLoadMode:
                    case 'ExternalStress0':
                        pattern = r'ExternalStress0.=((?:.|\s)*?);'
                        replace = f'ExternalStress0 = 0.0 0.0 {sigma}\n0.0 0.0 0.0\n{sigma} 0.0 0.0;'
                        # replace the pattern with the new value
                        text = re.sub(pattern, replace, text)
                    case 'ExternalStressRate':
                        pattern = r'ExternalStressRate.=((?:.|\s)*?);'
                        replace = f'ExternalStressRate = 0.0 0.0 {sigma}\n0.0 0.0 0.0\n{sigma} 0.0 0.0;'
                        # replace the pattern with the new value
                        text = re.sub(pattern, replace, text)
                    case 'ExternalStrain0':
                        pattern = r'ExternalStrain0.=((?:.|\s)*?);'
                        replace = f'ExternalStrain0 = 0.0 0.0 {sigma}\n0.0 0.0 0.0\n{sigma} 0.0 0.0;'
                        # replace the pattern with the new value
                        text = re.sub(pattern, replace, text)
                    case 'ExternalStrainRate':
                        pattern = r'ExternalStrainRate.=((?:.|\s)*?);'
                        replace = f'ExternalStrainRate = 0.0 0.0 {sigma}\n0.0 0.0 0.0\n{sigma} 0.0 0.0;'
                        # replace the pattern with the new value
                        text = re.sub(pattern, replace, text)
                # overwrite the uniformExternalLoadController.txt file with the new stress
                with open(f'{inputFilePath}/uniformExternalLoadController.txt', 'w') as file:
                    file.write(text)
                # generate microstructure
                self.generateMicrostructure(modelibPath)
                # run simulation
                self.runDislocationDynamics(parameters, modelibPath, externalLoadMode)
                # check if CRSS is reached
                if self.detectPermaDislocGlide(forceFilePath):
                    CRSS = True
                    break;
                # increase the stress
                else:
                    sigma = sigma*2
                    # remove the data
                    if os.path.exists(f'{workingSimPath}/F'):
                        os.system(f'rm -rf {workingSimPath}/F')
                    if os.path.exists(f'{workingSimPath}/evl'):
                        os.system(f'rm -rf {workingSimPath}/evl')
            # copy the finished data to the output directory
            self.copyDataToOutputDir(parameters, outputPath, workingSimPath)

    def copyDataToOutputDir(self, parameters: dict, outputPath: str, workingSimPath: str) -> None:
        # create directory name based on the parameters
        name = []
        for key, value in parameters.items():
            match key:
                case 'temperature':
                    acronym = 'T'
                case 'alloy':
                    acronym = 'A'
                case 'lineTension':
                    acronym = 'LT'
                case 'boxSize':
                    acronym = 'BS'
                #case 'periodicDipoleSlipSystemIDs':
                #    acronym = 'PDSS'
                #case 'periodicDipoleExitFaceIDs':
                case 'periodicDipoleNodes':
                    acronym = 'N'
                case 'periodicDipolePoints':
                    acronym = 'P'
            name.append(f'{acronym}')
            if type(value) == list:
                for val in value:
                    name.append(f'{val.strip()}')
            else:
                name.append(f'{value}')
        folderName = ''.join(name)

        # copy the data to the output directory
        # Copy the entire folder
        folderToCopy = ['evl', 'F', 'inputFiles']
        for folder in folderToCopy:
            shutil.copytree(f'{workingSimPath}/{folder}', f'{outputPath}/{folderName}/{folder}', dirs_exist_ok=True)
        # clean up the data in the working directory
        if os.path.exists(f'{workingSimPath}/F'):
            os.system(f'rm -rf {workingSimPath}/F')
        if os.path.exists(f'{workingSimPath}/evl'):
            os.system(f'rm -rf {workingSimPath}/evl')

    def generateMicrostructure(self, modelibPath: str) -> None:
        #modelibPath = self.structure.configFile['mainMoDELibDirectory']
        binaryFile = f'{modelibPath}/tools/MicrostructureGenerator/build/microstructureGenerator'
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'
        necessaryFolders = ['evl', 'F'];
        for folder in necessaryFolders:
            # Check if the directory does not exist, create it
            if not os.path.exists(f'{workingSimPath}/{folder}'):
                os.makedirs(f'{workingSimPath}/{folder}')
        os.system(f'{binaryFile} {workingSimPath}')

    def runDislocationDynamics(self, parameters: dict, modelibPath: str, externalLoadMode: str) -> None:
        print(f'currently running simulation with parameters... : {parameters}')
        #modelibPath = self.structure.configFile['mainMoDELibDirectory']
        binaryFile = f'{modelibPath}/tools/DDomp/build/DDomp'
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'

        # execute the DDomp binary
        os.system(f'{binaryFile} {workingSimPath}')

    def detectPermaDislocGlide(self, forceFilePath: str) -> bool:
        time = 1
        s13bPIndex = 5
        tstep = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=time)
        data = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=s13bPIndex)
        # calculate the first derivative of time-strain graph
        firstDiff = np.zeros(len(data))
        # derivative
        for i in range(len(data)-1):
            f1 = data[i]
            f2 = data[i+1]
            h = tstep[i+1] - tstep[i]
            firstDiff[i] =+ (f2-f1)/h
            maxFirstDiff = np.amax(firstDiff)
        # normalize the data
        firstDiff = firstDiff/maxFirstDiff;
        #check 50% of data
        checkPortion = int(0.5*(len(firstDiff)-1))
        # remove the first 50% of the data
        firstDiff = firstDiff[checkPortion:]
        threshold = 0.01
        # return the data that is larger than the threshold
        thresData = data[data > threshold]
        # if the 50% of the data is not zero, then I conclude that we found CRSS
        if len(thresData) >= len(firstDiff)-1:
            # found CRSS
            return True;
        else:
            # continue the simulation
            return False;

    def copyReferenceInputFiles(self, inputFilePath: str) -> None:
        # Define the source and destination directories
        source_dir = f'./ReferenceInputFiles/'
        dest_dir = f'{inputFilePath}/test/'
        # Check if the destination directory does not exist, create it
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        # Iterate over all files in the source directory
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            # Check if it is a file and not a directory
            if os.path.isfile(file_path):
                shutil.copy(file_path, dest_dir)  # Copy each file to the destination directory

    def setTimeStep(self, timeStep: int, modelibPath: str, inputFilePath: str) -> None:
        ddFile = f'{inputFilePath}/DD.txt'
        pattern = f'Nsteps=.*'
        replace = f'Nsteps={timeStep};'
        with open(ddFile, 'r') as file:
            text = file.read()
        # replace the pattern with the new value
        text = re.sub(pattern, replace, text)
        # overwrite the original data file
        with open(ddFile, 'w') as file:
            file.write(text)

    def modifyTXTfile(self, filePath: str, pattern: str, replace: str) -> None:
        with open(filePath, 'r') as file:
            text = file.read()
        # replace the pattern with the new value
        text = re.sub(pattern, replace, text)
        # overwrite the original data file
        with open(filePath, 'w') as file:
            file.write(text)

    def modifyGenInputFilePy(self, filePath: str, pattern: str, replace: str, inputFilePath: str) -> None:
        with open(filePath, 'r') as file:
            text = file.read()
        # replace the pattern with the new value
        text = re.sub(pattern, replace, text)
        # overwrite the original data file
        with open(filePath, 'w') as file:
            file.write(text)
        # change the current working directory to inputFiles
        runtimeDir = os.getcwd()
        os.chdir(f'{inputFilePath}')
        # using exec() to run another Python script
        with open(f'{inputFilePath}/generateInputFiles.py', 'r') as file:
            exec(file.read())
        # change the current working directory back to the original
        os.chdir(runtimeDir)

    def setSlipSystemType(self, paramDictionary: dict, materialLibPath: str, slipSystemType: str) -> None:
        for key, value in paramDictionary.items():
            match key:
                case 'alloy':
                    pattern = f'enabledSlipSystems.*'
                    replace = f'enabledSlipSystems={slipSystemType};'
                    filePath = f'{materialLibPath}/{value}.txt'
        with open(filePath, 'r') as file:
            text = file.read()
        # replace the pattern with the new value
        if re.search(pattern, text):
            text = re.sub(pattern, replace, text)
            # overwrite the original data file
            with open(filePath, 'w') as file:
                file.write(text)
        # if there is no enabledSlipSystem declaration, add it to the file
        else:
            with open(filePath, 'w') as file:
                file.write(text)
                file.write(f'{replace}')

    def changeParameters(self, paramDictionary: dict, modelibPath: str, inputFilePath: str, microStructLibPath: str) -> None:
        for key, value in paramDictionary.items():
            match key:
                case 'temperature':
                    pattern = f'pf.absoluteTemperature.*'
                    replace = f'pf.absoluteTemperature={value};'
                    filePath = f'{inputFilePath}/generateInputFiles.py'
                    self.modifyGenInputFilePy(filePath, pattern, replace, inputFilePath)
                case 'alloy':
                    pattern = f'pf=PolyCrystalFile.*'
                    replace = f'pf=PolyCrystalFile("../../../MaterialsLibrary/{value}.txt");'
                    filePath = f'{inputFilePath}/generateInputFiles.py'
                    self.modifyGenInputFilePy(filePath, pattern, replace, inputFilePath)
                case 'lineTension':
                    pattern = f'alphaLineTension=.*'
                    replace = f'alphaLineTension={value};'
                    filePath = f'{inputFilePath}/DD.txt'
                    self.modifyTXTfile(filePath, pattern, replace)
                case 'boxSize':
                    pattern = f'pf.boxScaling.*'
                    replace = f'pf.boxScaling=np.array({value});'
                    filePath = f'{inputFilePath}/generateInputFiles.py'
                    self.modifyGenInputFilePy(filePath, pattern, replace, inputFilePath)
                case 'periodicDipoleSlipSystemIDs':
                    pattern = f'periodicDipoleSlipSystemIDs.*'
                    replace = f'periodicDipoleSlipSystemIDs={value};'
                    filePath = f'{microStructLibPath}/periodicDipole.txt'
                    self.modifyTXTfile(filePath, pattern, replace)
                case 'periodicDipoleExitFaceIDs':
                    pattern = f'periodicDipoleExitFaceIDs.*'
                    replace = f'periodicDipoleExitFaceIDs={value};'
                    filePath = f'{microStructLibPath}/periodicDipole.txt'
                    self.modifyTXTfile(filePath, pattern, replace)
                case 'periodicDipoleNodes':
                    pattern = f'periodicDipoleNodes.*'
                    replace = f'periodicDipoleNodes={value};'
                    filePath = f'{microStructLibPath}/periodicDipole.txt'
                    self.modifyTXTfile(filePath, pattern, replace)
                case 'periodicDipolePoints':
                    pattern = r'periodicDipolePoints=((?:.|\s)*?);'
                    replace = f'periodicDipolePoints={value};'
                    filePath = f'{microStructLibPath}/periodicDipole.txt'
                    self.modifyTXTfile(filePath, pattern, replace)
                case 'periodicDipoleHeights':
                    pattern = f'periodicDipoleHeights.*'
                    replace = f'periodicDipoleHeights={value};'
                    filePath = f'{microStructLibPath}/periodicDipole.txt'
                    self.modifyTXTfile(filePath, pattern, replace)
                case 'periodicDipoleGlideSteps':
                    pattern = f'periodicDipoleGlideSteps.*'
                    replace = f'periodicDipoleGlideSteps={value};'
                    filePath = f'{microStructLibPath}/periodicDipole.txt'
                    self.modifyTXTfile(filePath, pattern, replace)


