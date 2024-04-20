#!/bin/python3

import numpy as np
import taichi as ti
import sys
ti.init(arch=ti.vulkan)

if len(sys.argv) != 4:
    exitString = "you need to provide 3 arguments\nex)./code.py startStress[mu] endStress[mu] numSteps"
    exit(exitString)

almg5S_Pa = 28.595 * 10**9 # [Pa]
almg10S_Pa = 26.784 * 10**9 # [Pa]
almg15S_Pa = 24.972 * 10**9 # [Pa]

# user input
startStress=float(sys.argv[1])
endStress=float(sys.argv[2])
numSteps=int(sys.argv[3])

testRange = np.linspace(startStress, endStress, numSteps) # [mu]

# initialize the memory
almg5s = ti.field(dtype=ti.f64, shape=numSteps)
almg10s = ti.field(dtype=ti.f64, shape=numSteps)
almg15s = ti.field(dtype=ti.f64, shape=numSteps)

@ti.kernel
def convertMutoMPa(numSteps: ti.i32, stressRange: ti.types.ndarray()):
    for i in range(numSteps):
        almg5s[i] = stressRange[i]*almg5S_Pa*10**(-6) #[GPa/mu]*[mu]*[MPa/Pa]
        almg10s[i] = stressRange[i]*almg10S_Pa*10**(-6) #[GPa/mu]*[mu]*[MPa/Pa]
        almg15s[i] = stressRange[i]*almg15S_Pa*10**(-6) #[GPa/mu]*[mu]*[MPa/Pa]

# run the stress conversion
convertMutoMPa(numSteps, testRange)

# print the converted stress for visual confirmation
for i in range(numSteps):
    print(f'stress = {testRange[i]} [mu], AlMg5 = {almg5s[i]} [MPa], AlMg10 = {almg10s[i]} [MPa], AlMg15 = {almg15s[i]} [MPa]')

# write separate text files
f = open('stressRange_mu.txt', 'w')
g = open('stressRange_MPa.txt', 'w')
for j in range(numSteps):
    f.write(f'[0.0, 0.0, {testRange[j]}, 0.0, 0.0, 0.0, {testRange[j]}, 0.0, 0.0],\n')
    g.write(f'stress = {testRange[j]} [mu], AlMg5 = {almg5s[j]} [MPa], AlMg10 = {almg10s[j]} [MPa], AlMg15 = {almg15s[j]} [MPa]\n')

