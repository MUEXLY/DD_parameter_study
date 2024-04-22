import json, re, os
import subprocess

from dataclasses import dataclass

@dataclass
class structure:
    configFile: dict

    def modifyInitMicrostructure(self):
        modelibPath = self.configFile['mainMoDELibDirectory']
        microStructureToUse = self.configFile['microstructureFileToUse']
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
        microStrucConfigFile = f'{inputFilePath}/initialMicrostructure.txt'
        # open the original data file
        dummyData = []
        pattern = f'#?microstructureFile = .*'
        replace = f'microstructureFile = {microStructureToUse};'
        with open(microStrucConfigFile, 'r') as f:
            for line in f:
                # Strip the line of leading and trailing whitespace
                stripped_line = line.strip()
                # Check if the line is blank
                if not stripped_line:
                    dummyData.append('\n') # add a blank line to the list
                    continue;

                #data = re.sub(pattern, replace, line)
                if microStructureToUse in line:
                    data = line.strip('#')
                else:
                    if '#' in line:
                        data = f'{line}'
                    else:
                        data = f'#{line}'
                # store original data
                dummyData.append(data)
        # overwrite the original data file
        with open(f'{inputFilePath}/initialMicrostructure.txt', 'w') as g:
            for line in dummyData:
                g.write(line)

    def changeMaterial(self):
        modelibPath = self.configFile['mainMoDELibDirectory']
        microStructureToUse = self.configFile['microstructureFileToUse']
        inputFilePath = f'{modelibPath}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/'
        print("Generating polycrystal...")
        materialFile = self.configFile['materialFileToUse']
        dummyData = []
        with open(f'{inputFilePath}/generateInputFiles.py', 'r') as f:
            for line in f:
                # Strip the line of leading and trailing whitespace
                stripped_line = line.strip()
                # Check if the line is blank
                if not stripped_line:
                    dummyData.append('\n') # add a blank line to the list
                    continue;
                if 'MaterialsLibrary' in line:
                    data = f"pf=PolyCrystalFile('../../../MaterialsLibrary/{materialFile}');\n"
                else:
                    data = line
                # store original data
                dummyData.append(data)
        # overwrite the original data file
        with open(f'{inputFilePath}/generateInputFiles.py', 'w') as g:
            for line in dummyData:
                g.write(line)
        # change the current working directory to inputFiles
        #runtimeDir = os.getcwd()
        #os.chdir(f'{inputFilePath}')

        ## using exec() to run another Python script
        #with open(f'{inputFilePath}/generateInputFiles.py', 'r') as file:
        #    exec(file.read())

        ## change the current working directory back to the original
        #os.chdir(runtimeDir)

