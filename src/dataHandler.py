import os

def delOldEvlandF(simPath):
    if os.path.exists(simPath+'F'):
        os.system('rm -rf '+simPath+'F')
    if os.path.exists(simPath+'evl'):
        os.system('rm -rf '+simPath+'evl')

def createEvlandFfolder(simPath):
    if not os.path.exists(simPath+'F'):
        os.system('mkdir -p '+simPath+'F')
    if not os.path.exists(simPath+'evl'):
        os.system('mkdir -p '+simPath+'evl')

def delOldReferenceFiles(refinputPath):
    if os.path.exists(refinputPath):
        os.system('rm -r '+refinputPath)

def genReferenceFiles(refinputPath, simPath):
    os.system('mkdir -p '+refinputPath)
    os.system('cp -r '+simPath+'inputFiles/* ' +refinputPath)
