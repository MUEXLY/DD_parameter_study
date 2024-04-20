import numpy as np

def areaSwept(filePath, file):
    timeStep = int(file.split('_')[1].split('.')[0])
    #labels = 
    slipPlaneDat = []
    loopLength = []
    outDat = {}
    # Extract slip plane information
    with open(filePath+file, 'r') as o:
        for line in o:
            # split the line with delimiter \t
            line = line.split('\t')
            linedat = []
            # split the line with delimiter ' ', additional algo is added to keep the list as 1 dimension 
            for i in range(len(line)):
                dummy = line[i].split(' ')
                if len(dummy) > 1:
                    for j in range(len(dummy)):
                        if dummy[j]:
                            linedat.append(dummy[j])
                else:
                    linedat.append(dummy[0])
            # if there are 16 elements in the list (slip plane), save the data
            if len(linedat)==16:
                slipPlaneDat.append(linedat)
#    print(slipPlaneDat)
    Aindex = 15
    for j in range(len(slipPlaneDat)):
        #loopLength.append(float(slipPlaneDat[j][15]))
        loopLength.append(float(slipPlaneDat[j][Aindex]))
    loopLength = np.array(loopLength)
    # returns all slip planes
    outDat[timeStep] = loopLength
    return outDat;
