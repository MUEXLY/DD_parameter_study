import os
import GeneratePolyCrystalFile as gp

def runMicrostructGen(modelibPath, simPath, dataDict, debugFlag=0):
    if debugFlag:
        print('Running microstructure generator...')
        print('debugFlag = '+str(debugFlag))
        print('ModeLib Folder Path = '+modelibPath)
        print('Simulation Folder Path = '+simPath)
    os.system(modelibPath+'tools/MicrostructureGenerator/build/microstructureGenerator '+simPath)

def runDDomp(modelibPath, simPath, debugFlag):
    if debugFlag:
        print('Running DDomp...')
        print('debugFlag = '+str(debugFlag))
        print('ModeLib Folder Path = '+modelibPath)
        print('Simulation Folder Path = '+simPath)
    os.system(modelibPath+'tools/DDomp/build/DDomp '+simPath)
