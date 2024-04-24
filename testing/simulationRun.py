import json, re, os
import subprocess
import itertools
import shutil
import subprocess
from dataclasses import dataclass

@dataclass
class dislocationDynamicsRun:
    structure: object
    testRange: dict

    # change material in polycrystal generation script, also enables partial if enabled
    #def changeMaterial(self):
    #    modelibPath = self.structure.configFile['mainMoDELibDirectory']
    #    microStructureToUse = self.structure.configFile['microstructureFileToUse']
    #    inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
    #    materialFile = self.structure.configFile['materialFileToUse']
    #    dummyData = []
    #    with open(f'{inputFilePath}/generateInputFiles.py', 'r') as f:
    #        for line in f:
    #            # Strip the line of leading and trailing whitespace
    #            stripped_line = line.strip()
    #            # Check if the line is blank
    #            if not stripped_line:
    #                dummyData.append('\n') # add a blank line to the list
    #                continue;
    #            if 'MaterialsLibrary' in line:
    #                data = f"pf=PolyCrystalFile('../../../MaterialsLibrary/{materialFile}');\n"
    #            else:
    #                data = line
    #            # store original data
    #            dummyData.append(data)
    #    # overwrite the original data file
    #    with open(f'{inputFilePath}/generateInputFiles.py', 'w') as g:
    #        for line in dummyData:
    #            g.write(line)
    #    # change the current working directory to inputFiles
    #    #runtimeDir = os.getcwd()
    #    #os.chdir(f'{inputFilePath}')

    #    ## using exec() to run another Python script
    #    #with open(f'{inputFilePath}/generateInputFiles.py', 'r') as file:
    #    #    exec(file.read())

    #    ## change the current working directory back to the original
    #    #os.chdir(runtimeDir)

    def exploreAllParams(self) -> None:
        modelibPath = self.structure.configFile['mainMoDELibDirectory']
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
        outputPath = self.structure.configFile['dataOutPutDirectory']
        #paramList = self.structure.configFile['parametersToExplore']
        paramToCouple = self.structure.configFile['paramtersToCouple']
        timeStep = self.structure.configFile['totalTimeSteps']
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'

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
            self.changeParameters(parameters)
            # set time step
            self.setTimeStep(timeStep)
            # generate microstructure
            self.generateMicrostructure()
            # run simulation
            self.runDislocationDynamics(parameters)
            # detect CRSS
            #self.detectCRSS(parameters)
            # copy the finished data to the output directory
            self.copyDataToOutputDir(parameters, outputPath, workingSimPath)

    def copyDataToOutputDir(self, parameters: dict, outputPath: str, workingSimPath: str) -> None:
        # create directory name based on the parameters
        name = []
        for key, value in parameters.items():
            name.append(f'{key}')
            if type(value) == list:
                for val in value:
                    name.append(f'{val}')
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

    def generateMicrostructure(self) -> None:
        modelibPath = self.structure.configFile['mainMoDELibDirectory']
        binaryFile = f'{modelibPath}/tools/MicrostructureGenerator/build/microstructureGenerator'
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'
        necessaryFolders = ['evl', 'F'];
        for folder in necessaryFolders:
            # Check if the directory does not exist, create it
            if not os.path.exists(f'{workingSimPath}/{folder}'):
                os.makedirs(f'{workingSimPath}/{folder}')

        # get the current working directory
        runtimeDir = os.getcwd()
        # change the current working directory to the simulation working directory
        os.chdir(f'{workingSimPath}')
        # Use subprocess.run to execute the binary
        try:
            result = subprocess.run([binaryFile], check=True, text=True, capture_output=True)
            # enable the print statement below if you need to see the output
            #print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error occurred while executing microstructureGenerator.")
            print("Error Code:", e.returncode)
            print("Error Message:", e.stderr)
            exit(1)
        # change the working directory from the simulation working dir to the original dir
        os.chdir(runtimeDir)

    def runDislocationDynamics(self, parameters: dict) -> None:
        print(f'currently running simulation with parameters... : {parameters}')
        modelibPath = self.structure.configFile['mainMoDELibDirectory']
        binaryFile = f'{modelibPath}/tools/DDomp/build/DDomp'
        workingSimPath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/'
        # get the current working directory
        runtimeDir = os.getcwd()
        # change the current working directory to the simulation working directory
        os.chdir(f'{workingSimPath}')
        # Use subprocess.run to execute the binary
        try:
            result = subprocess.run([binaryFile], check=True, text=True, capture_output=True)
            # enable the print statement below if you need to see the output
            # it dumps the output all at once, so if the simulation is long,
            # it can crash your terminal
            #print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error occurred while executing DDomp.")
            print("Error Code:", e.returncode)
            print("Error Message:", e.stderr)
            exit(1)

        # change the working directory from the simulation working dir to the original dir
        os.chdir(runtimeDir)

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

    def setTimeStep(self, timeStep: int) -> None:
        modelibPath = self.structure.configFile['mainMoDELibDirectory']
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
        ddFile = f'{inputFilePath}/DD.txt'
        pattern = f'Nsteps=.*'
        replace = f'Nsteps={timeStep};'
        dummyData = []
        # open the original data file
        with open(ddFile,'r') as f:
            for line in f:
                # compare the pattern line by line and if the line matches the pattern, replace it
                dat = re.sub(pattern, replace, line)
                # store data
                dummyData.append(dat)
        # overwrite the original data file
        with open(ddFile,'w') as g:
            for line in dummyData:
                g.write(line)

    def modifyTXTfile(self, filePath: str, pattern: str, replace: str) -> None:
        dummyData = []
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

    def modifyGenInputFilePy(self, filePath: str, pattern: str, replace: str, inputFilePath: str) -> None:
        dummyData = []
        with open(filePath, 'r') as f:
            for line in f:
                # Strip the line of leading and trailing whitespace
                stripped_line = line.strip()
                # Check if the line is blank
                if not stripped_line:
                    dummyData.append('\n') # add a blank line to the list
                    continue;
                # compare the pattern line by line and if the line matches the pattern, replace it
                data = re.sub(pattern, replace, line)
                # store original data
                dummyData.append(data)
        # overwrite the original data file
        with open(filePath, 'w') as g:
            for line in dummyData:
                g.write(line)
        # change the current working directory to inputFiles
        runtimeDir = os.getcwd()
        os.chdir(f'{inputFilePath}')
        # using exec() to run another Python script
        with open(f'{inputFilePath}/generateInputFiles.py', 'r') as file:
            exec(file.read())
        # change the current working directory back to the original
        os.chdir(runtimeDir)

    def changeParameters(self, paramDictionary: dict) -> None:
        modelibPath = self.structure.configFile['mainMoDELibDirectory']
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
        microstructureLibaryPath = f'{inputFilePath}/../../MicrostructureLibrary/'
        for key, value in paramDictionary.items():
            match key:
                case 'T':
                    pattern = f'pf.absoluteTemperature.*'
                    replace = f'pf.absoluteTemperature={value};'
                    filePath = f'{inputFilePath}/generateInputFiles.py'
                    self.modifyGenInputFilePy(filePath, pattern, replace, inputFilePath)
                case 'A':
                    pattern = f'pf.absoluteTemperature.*'
                    replace = f'pf.absoluteTemperature={value};'
                    filePath = f'{inputFilePath}/generateInputFiles.py'
                    self.modifyGenInputFilePy(filePath, pattern, replace, inputFilePath)
                case 'LT':
                    pattern = f'alphaLineTension=.*'
                    replace = f'alphaLineTension={value};'
                    filePath = f'{inputFilePath}/DD.txt'
                    self.modifyTXTfile(filePath, pattern, replace)
                case 'BS':
                    pattern = f'pf.boxScaling.*'
                    replace = f'pf.boxScaling=np.array({value});'
                    filePath = f'{inputFilePath}/generateInputFiles.py'
                    self.modifyGenInputFilePy(filePath, pattern, replace, inputFilePath)
                #case 'DC':
                #case 'DD':
                #case 'L':
                #case 'GP':
                #case 'RF':
                #case 'DN':
                #case 'SR':
                #case 'DP':
                #case 'DG':
                #case 'LMAX':
                #case 'IES': 
                #case 'DG':

