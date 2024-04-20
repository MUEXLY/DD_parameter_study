import numpy as np
import os

def recordCRSS(outPath, dataDict):
    parameters = np.array([]);
    headerString = [];
    dataOutName = f'{outPath}/CRSSrecord.txt'
    with open(dataOutName, 'a') as o:
        for key, value in dataDict.items():
            if type(value)==list:
                value = np.array(value)
                value = value[value > 0];
                value = value[0];
            parameters = np.append(parameters, value)
            headerString.append(f'#{key}')

        # write parameters
        numOfSigFig = 5
        np.set_printoptions(linewidth=np.inf)
        if os.path.getsize(dataOutName)==0: 
            head = f'{ " "*(numOfSigFig+4) }'.join(headerString)
            o.write(head+'\n')

        parameters = np.array2string(parameters, formatter={'float':lambda x: f"%.{numOfSigFig}e" % x})
        params = ''.join(str(parameters).strip('[]'))

        o.write(params+'\n')

