#!/bin/python3

import os, re
import time
import numpy as np
import numba as nb

def scanDirs(path: str) -> list:
    dirList = []
    with os.scandir(path) as it:
        for entry in it:
            #if not entry.name.startswith('.') and not entry.is_dir():
            if entry.is_dir() and entry.name != '__pycache__':
                dirList.append(entry.name)
    return dirList;

def loadData(path: str) -> np.ndarray:
    time = 1
    b13 = 5
    tstep = np.loadtxt(f'{path}/F/F_0.txt', usecols=time)
    data = np.loadtxt(f'{path}/F/F_0.txt', usecols=b13)
    return tstep, data;

@nb.njit(cache=True, parallel=True)
def deriTest(tstep: np.ndarray, data: np.ndarray) -> np.ndarray:
    g = np.zeros(len(data))
    # derivative
    for i in range(len(data)-1):
        f1 = data[i]
        f2 = data[i+1]
        h = tstep[i+1] - tstep[i]
        g[i] =+ (f2-f1)/h
    maxG = np.amax(g)
    # normalize the data
    return g/maxG;

#@nb.njit(cache=True, parallel=True)
@nb.njit(cache=True)
def detectCRSS(dat):
    #check 50% of data
    checkPortion = int(0.5*(len(dat)-1))
    # cut the data to 50%
    dat = dat[checkPortion:]
    threshold = 0.01
    # return the data that is larger than the threshold
    datt = dat[dat > threshold]
    # if the 50% of the data is not zero, then I conclude that we found CRSS
    if len(datt) >= len(dat)-1:
        print(f'FUCK YEAH CRSS!!!!!!!!')
        return True;

listDataDir = scanDirs('.')

for direct in listDataDir:
    tstep, data = loadData(f'{direct}')
    g = deriTest(tstep, data)
    print(direct)
    datt = detectCRSS(g)
    if datt:
        exit()
    #print(datt)
    #out = np.vstack((tstep, data, g)).T
    #np.savetxt('testData.txt', out)
    #os.system("gnuplot gpltest.gp")

exit()
#tstep, data = loadData()
#g = deriTest(tstep, data)
#out = np.vstack((tstep, data, g)).T
#np.savetxt('testData.txt', out)
#os.system("gnuplot gpltest.gp")
