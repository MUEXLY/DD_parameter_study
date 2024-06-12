import re, os
import subprocess
import itertools
import shutil
import numpy as np
from dataclasses import dataclass
from typing import Any

@dataclass
class dislocationDynamicsRun:
    structure: object
    testRange: dict

    def exploreAllParams(self) -> None:
        modelibPath = self.structure.configFile['mainMoDELibDirectory'];
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
        forceFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/F/'
        outputPath = self.structure.configFile['dataOutPutDirectory']
        paramToCouple = self.structure.configFile['paramtersToCouple']
        timeStep = self.structure.configFile['totalTimeSteps']
        microStruct = self.structure.configFile['microstructureFileToUse']
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'
        microStructLibPath = f'{modelibPath}/tutorials/DislocationDynamics/MicrostructureLibrary'
        materialLibPath = f'{modelibPath}/tutorials/DislocationDynamics/MaterialsLibrary'
        noiseLibPath = f'{modelibPath}/tutorials/DislocationDynamics/NoiseLibrary'
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

        # copy reference input Files to the simulation working directory
        #self.copyReferenceInputFiles(microStructLibPath, materialLibPath, noiseLibPath, inputFilePath)

        # clean up the old data
        if os.path.exists(f'{workingSimPath}/F'):
            os.system(f'rm -rf {workingSimPath}/F')
        if os.path.exists(f'{workingSimPath}/evl'):
            os.system(f'rm -rf {workingSimPath}/evl')

        # run simulations with the parameters saved on each list
        for parameters in paramDictList:
            # extract material info
            b_SI = self.readValFromMaterialFile('b_SI', materialLibPath, parameters)
            mu0_SI = self.readValFromMaterialFile('mu0_SI', materialLibPath, parameters)
            rho_SI = self.readValFromMaterialFile('rho_SI', materialLibPath, parameters)
            cs = np.sqrt(mu0_SI/rho_SI) #shear wave speed
            convertTimeUnit = b_SI/cs # [sec]

            # change parameters
            _ = self.changeParameters(parameters, modelibPath, inputFilePath, microStructLibPath)
            # if partial is enabled, make the change on the material file
            _ = self.setSlipSystemType(parameters, materialLibPath, slipSystemType)
            # set time step
            _ = self.setTimeStep(timeStep, modelibPath, inputFilePath)


            #######################################
            # bisection 'like' algorithm
            ##############################################
            convertMPaToMu = 1/(mu0_SI*10**(-6)) # conversion factor
            initialStressMPa = 1 # initial stress guess in MPa
            #tol=10
            maxIter = 20 # set the max num of search
            numericalZero = 10
            tooHighDotMu = 10000
            stressStepInMPa = 20
            initialCRSSguessMPa = 1500  # assume that the CRSS is in between 1MPa and 1500MPa
            # interval for bisection method
            A, B = initialStressMPa, initialCRSSguessMPa
            # applied stress value in DD, convert MPa to [mu]
            sigma = initialStressMPa*convertMPaToMu
            # start searching
            for iterationNumber in range(1, maxIter+1):
                print(f'iteration = {iterationNumber}, sigma = {sigma/convertMPaToMu} MPa')
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
                _ = self.generateMicrostructure(modelibPath)

                # run simulation for the number of steps in config.json file
                _ = self.runDislocationDynamics(parameters, modelibPath, externalLoadMode)

                # calculate the mean dot betaP
                muDotBetaP = self.calcMeanOfDotBetaP(forceFilePath, convertTimeUnit)
                print(f'muDotBetaP = {muDotBetaP}')
                # it's CRSS!
                if numericalZero <= muDotBetaP <= tooHighDotMu:
                    # increase timestep
                    #steps = 1000000
                    steps = 20000
                    print(f'Running more simulation until step: {steps}, muDotBetaP = {muDotBetaP}')
                    # increase the timestep number so that it can run simulation more
                    _ = self.setTimeStep(steps, modelibPath, inputFilePath)
                    # restart simulation
                    _ = self.runDislocationDynamics(parameters, modelibPath, externalLoadMode)
                    # save the data
                    _ = self.copyDataToOutputDir(parameters, outputPath, workingSimPath, microStructLibPath, microStruct, sigma/convertMPaToMu)
                    # save the result in a separate file with CRSS and configuration info
                    _ = self.saveData(parameters, outputPath, sigma/convertMPaToMu)
                    # break the search loop
                    break
                # stress is too high
                elif muDotBetaP >= tooHighDotMu:
                    # update the upper boundary of the interval
                    B = (A+B)/2
                    # next guess
                    sigma = (A+B)/2 * convertMPaToMu
                # dislocation is not moving, stress is too low
                elif muDotBetaP <= tooHighDotMu:
                    # set the stress to the upper bound and run it
                    sigma = B * convertMPaToMu
                else:
                    exit("something is wrong, mean dotBetaP calculation is erroneous")

                # dislocation is not moving
                #if muDotBetaP < numericalZero:
                #    print(f'muDotBetaP = {muDotBetaP}')
                #    _ = self.copyDataToOutputDir(parameters, outputPath, workingSimPath, microStructLibPath, microStruct, sigma/convertMPaToMu)
                #    if os.path.exists(f'{workingSimPath}/F'):
                #        os.system(f'rm -rf {workingSimPath}/F')
                #    if os.path.exists(f'{workingSimPath}/evl'):
                #        os.system(f'rm -rf {workingSimPath}/evl')
                #    # increase the applied stress by the step size
                #    sigma += stressStepInMPa*convertMPaToMu
                #    continue
                ## CRSS is found
                #elif numericalZero < muDotBetaP < tooHighDotMu:
                #    # increase timestep
                #    #steps = 1000000
                #    steps = 20000
                #    print(f'Running more simulation until step: {steps}, muDotBetaP = {muDotBetaP}')
                #    # increase the timestep number so that it can run simulation more
                #    _ = self.setTimeStep(steps, modelibPath, inputFilePath)
                #    # restart simulation
                #    _ = self.runDislocationDynamics(parameters, modelibPath, externalLoadMode)
                #    # save the data
                #    _ = self.copyDataToOutputDir(parameters, outputPath, workingSimPath, microStructLibPath, microStruct, sigma/convertMPaToMu)
                #    # save the result as a CSV file with CRSS
                #    _ = self.saveDataInCSV(parameters, outputPath, sigma/convertMPaToMu)
                #    break
                ## stress is too high
                #else:
                #    print(f'muDotBetaP = {muDotBetaP}')
                #    _ = self.copyDataToOutputDir(parameters, outputPath, workingSimPath, microStructLibPath, microStruct, sigma/convertMPaToMu)
                #    if os.path.exists(f'{workingSimPath}/F'):
                #        os.system(f'rm -rf {workingSimPath}/F')
                #    if os.path.exists(f'{workingSimPath}/evl'):
                #        os.system(f'rm -rf {workingSimPath}/evl')
                #    # reduce the stress step size by half
                #    stressStepInMPa = stressStepInMPa/2
                #    # reduce the applied stress by the step size
                #    sigma -= stressStepInMPa*convertMPaToMu
                #    continue

    def saveData(self, parameters: dict, outputPath: str, sigmaMPa: float) -> None:
        dataOutputName = 'CRSStestResult.txt'
        # remove old data
        #if os.path.exists(f'{outputPath}/{dataOutputName}'):
        #    os.system(f'rm {outputPath}/{dataOutputName}')
        header, data = [], []
        for key, value in parameters.items():
            # if the value is string with ' ' delimiter, split with delim, then strip newline (\n) if there is any
            value = [ x.strip('\n') for x in value.split(' ') ] if type(value)==str else value
            # if the value is list, join the string with ',' delimiter
            value = ','.join([str(x) for x in value]) if type(value)==list else value
            match key:
                case 'temperature':
                    header.append(f'Temp')
                    data.append(f'{value}')
                case 'alloy':
                    header.append(f'Alloy')
                    data.append(f'{value}')
                case 'boxSize':
                    header.append(f'BoxSize')
                    data.append(f'{value}')
                case 'lineTension':
                    header.append(f'LineTension')
                    data.append(f'{value}')
                case 'periodicDipoleSlipSystemIDs':
                    header.append(f'sIDs')
                    data.append(f'{value}')
                case 'periodicDipoleExitFaceIDs':
                    header.append(f'exIDs')
                    data.append(f'{value}')
                case 'periodicDipoleNodes':
                    header.append(f'NodeNum')
                    data.append(f'{value}')
                case 'periodicDipolePoints':
                    header.append(f'dipolePoints')
                    data.append(f'{value}')
                case 'periodicDipoleHeights':
                    header.append(f'dipoleHeights')
                    data.append(f'{value}')
                case 'periodicDipoleGlideSteps':
                    header.append(f'dipoleGSteps')
                    data.append(f'{value}')
        # add CRSS header
        header.append(f'CRSS')
        # add CRSS
        data.append(f'{sigmaMPa}')

        # join the list of strings as a single string
        header = ' '.join(header)
        data = ' '.join(data)
        # if file does not exsit, write header
        if not os.path.exists(f'{outputPath}/{dataOutputName}'):
            with open(f'{outputPath}/{dataOutputName}', 'w') as output:
                output.write(f'{header}\n')
                output.write(data)
        else:
            with open(f'{outputPath}/{dataOutputName}', 'a') as output:
                output.write(data)

    def readValFromMaterialFile(self, parameter: str, libPath: str, parameters: dict) -> float:
        with open(f'{libPath}/{parameters['alloy']}.txt', 'r') as mFile:
            for line in mFile:
                # strip down comments from the data
                line = line.split(';')[0]
                if line.startswith(f'{parameter}'):
                    # Split the line by '=' and take the second part, then remove leading/trailing whitespace
                    value = float(line.split('=')[1].strip())
                    break
        return value;

    def copyDataToOutputDir(self, parameters: dict, outputPath: str, workingSimPath: str, microStructLibPath: str,  microStructFile: str, sigmaMPa: float) -> None:
        if not os.path.exists(f'{outputPath}'):
            shutil.os.makedirs(f'{outputPath}')

        # create directory name based on the parameters
        name = []
        name.append(f'Str{int(sigmaMPa)}')
        for key, value in parameters.items():
            # if the value is string with ' ' delimiter, split with delim, then strip newline (\n) if there is any
            value = [ x.strip('\n') for x in value.split(' ') ] if type(value)==str else value
            # if the value is list, join the string with '-' delimiter
            value = '-'.join([str(x) for x in value]) if type(value)==list else value
            match key:
                case 'temperature':
                    name.append(f'T{value}')
                case 'alloy':
                    name.append(f'{value}')
                case 'boxSize':
                    name.append(f'BS{value}')
                case 'lineTension':
                    name.append(f'LT{value}')
                case 'periodicDipoleSlipSystemIDs':
                    name.append(f'sID{value}')
                case 'periodicDipoleExitFaceIDs':
                    name.append(f'exID{value}')
                case 'periodicDipoleNodes':
                    name.append(f'N{value}')
                case 'periodicDipolePoints':
                    name.append(f'DP{value}')
                case 'periodicDipoleHeights':
                    name.append(f'DH{value}')
                case 'periodicDipoleGlideSteps':
                    name.append(f'DGS{value}')
        # join the list of strings as a single string
        folderName = ''.join(name)

        # Remove the old generated data if there is previously generated data
        if os.path.exists(f'{outputPath}/{folderName}'):
            os.system(f'rm -rf {outputPath}/{folderName}')

        # copy the data to the output directory
        shutil.copytree(f'{workingSimPath}/', f'{outputPath}/{folderName}', dirs_exist_ok=True)
        # copy microStructureFile
        shutil.copy(f'{microStructLibPath}/{microStructFile}', f'{outputPath}/{folderName}')

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
        # catch the binary runtime error
        try:
            # Execute the binary
            result = subprocess.run(
                [f'{binaryFile}', f'{workingSimPath}'],
                check=True,                          # Raises a CalledProcessError on non-zero exit status
                stdout=subprocess.PIPE,              # Capture standard output
                stderr=subprocess.PIPE               # Capture standard error
            )
            #output = result.stdout.decode('utf-8')
            error = result.stderr.decode('utf-8')
            #print("Output:", output)
            #print("Error:", error)
        except subprocess.CalledProcessError as e:
            exit(e.stderr.decode('utf-8'))

    def runDislocationDynamics(self, parameters: dict, modelibPath: str, externalLoadMode: str) -> None:
        print(f'currently running simulation with parameters... : {parameters}')
        binaryFile = f'{modelibPath}/tools/DDomp/build/DDomp'
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'

        max_attempts = 3  # Maximum number of attempts to restart the binary
        attempt = 1
        while attempt <= max_attempts:
            try:
                # Execute the binary
                result = subprocess.run(
                    [f'{binaryFile}', f'{workingSimPath}'],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                error = result.stderr.decode('utf-8')
                break  # Exit the loop if the execution is successful
            except subprocess.CalledProcessError as e:
                error = e.stderr.decode('utf-8')
                print(f"Attempt {attempt} failed. Error: {error}")
                attempt += 1

        if attempt > max_attempts:
            print(f"Execution failed after {max_attempts} attempts.")
            exit(error)

    #def nonZeroBetaP(self, forceFilePath: str, convertTimeUnit: float) -> bool:
    #    # read the data
    #    time = 1
    #    s13bPIndex = 5
    #    tstep = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=time)
    #    data = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=s13bPIndex)

    #    # Calculate the index to start from (20% of the array length)
    #    startIndex = int(len(data)*0.2)

    #    # Slice the array to get the remaining 80%
    #    trimmedData = data[startIndex:]
    #    trimmedTstep = tstep[startIndex:]

    #    # calculate the first derivative of the remaining 80% of the time-plasticStrain graph
    #    diff = np.gradient(trimmedData, trimmedTstep*convertTimeUnit) # rate [1/s]
    #    muDiff = np.mean(diff) # mean of the plastic strain rate [1/s]

    #    tolerance = 10 # arbitrary value, if the mean of plastic strain is larger than 1000 [1/s], we found it
    #    # return the data that is larger than the tolerance
    #    if muDiff>tolerance:
    #        return True;
    #    else:
    #        return False;

    def calcMeanOfDotBetaP(self, forceFilePath: str, convertTimeUnit: float) -> float:
        # read the data
        time = 1
        s13bPIndex = 5
        tstep = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=time)
        data = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=s13bPIndex)

        # Calculate the index to start from (20% of the array length)
        startIndex = int(len(data)*0.2)

        # Slice the array to get the remaining 80%
        trimmedData = data[startIndex:]
        trimmedTstep = tstep[startIndex:]

        # calculate the first derivative of the remaining 80% of the time-plasticStrain graph
        diff = np.gradient(trimmedData, trimmedTstep*convertTimeUnit) # rate [1/s]
        muDiff = np.mean(diff) # mean of the plastic strain rate [1/s]
        return muDiff

    #def detectPermaDislocGlide(self, forceFilePath: str) -> bool:
    #    # calculate the sim time unit
    #    b_SI=0.286e-9 # burgers vector
    #    mu0_SI=28.595428e+9 # [Pa] shear modulus
    #    rho_SI=2700.0 # [kg/m^3] density
    #    cs = np.sqrt(mu0_SI/rho_SI) #shear wave speed
    #    convertTimeUnit = b_SI/cs # [sec]

    #    # read the data
    #    time = 1
    #    s13bPIndex = 5
    #    tstep = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=time)
    #    data = np.loadtxt(f'{forceFilePath}/F_0.txt', usecols=s13bPIndex)
    #    # calculate the first derivative of time-strain graph
    #    #print(firstDiff)

    #    # Calculate the index to start from (20% of the array length)
    #    startIndex = int(len(data)*0.2)

    #    # Slice the array to get the remaining 80%
    #    trimmedData = data[startIndex:]
    #    trimmedTstep = tstep[startIndex:]

    #    # calculate the first derivative of the remaining 80% of the time-plasticStrain graph
    #    diff = np.gradient(trimmedData, trimmedTstep*convertTimeUnit) # rate [1/s]
    #    muDiff = np.mean(diff) # mean of the plastic strain rate [1/s]

    #    print(f'data: {data}')
    #    print(f'diff: {diff}')
    #    exit()
    #    tolerance = 1000 # arbitrary value, if the mean of plastic strain is larger than 1000 [1/s], we found it
    #    # return the data that is larger than the tolerance
    #    if muDiff>tolerance:
    #        # found CRSS
    #        print(f'Found CRSS at muDiff = {muDiff}')
    #        return True;
    #    else:
    #        # continue the simulation
    #        return False;

    def copyReferenceInputFiles(self, modelibPath: str) -> None:
        # Define the source and destination directories
        sourceDir = f'./ReferenceInputFiles/'
        # Copy a directory and its contents, overwriting the destination if it already exists
        shutil.copytree(f'{sourceDir}', f'{modelibPath}/tutorials/DislocationDynamics/', dirs_exist_ok=True)

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
        with open(f'./generateInputFiles.py', 'r') as file:
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


