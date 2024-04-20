import os, re
import numpy as np
import numba as nb

def loadData(path: str, bPIndex: int) -> np.ndarray:
    time = 1
    tstep = np.loadtxt(f'{path}/F/F_0.txt', usecols=time)
    data = np.loadtxt(f'{path}/F/F_0.txt', usecols=bPIndex)
    # dump duplicate data
    tstep = np.unique(tstep)
    data = data[:len(tstep)]
    return tstep, data;

# calculate the first derivative of time-strain graph
@nb.njit(cache=True, parallel=True)
def calc1stDiff(tstep: np.ndarray, data: np.ndarray) -> np.ndarray:
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

@nb.njit(cache=True)
def detectCRSS(data):
    #check 50% of data
    checkPortion = int(0.5*(len(data)-1))
    # cut the data to 50%
    data = data[checkPortion:]
    threshold = 0.01
    # return the data that is larger than the threshold
    thresData = data[data > threshold]
    # if the 50% of the data is not zero, then I conclude that we found CRSS
    if len(thresData) >= len(data)-1:
        # found CRSS
        return True;
    else:
        return False;
