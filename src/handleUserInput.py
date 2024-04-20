#!/bin/python3

import sys, os

def printHelpMessage() -> None:
    print(f" *** Selection ***")
    print(f"1 : Change Temperature ")
    print(f"2 : Change Dislocation Length")
    print(f"3 : Change distance between dislocations")
    print(f"4 : Change Concentration")
    print(f"5 : Change Dislocation Character (edge vs screw)")
    print(f"6 : Change Lengevin Noise (Deactivate vs Activate)")
    print(f"7 : Change Gauss Quadrature Points Density")
    print(f"8 : Change Remesh Frequency") # fix remesh frequency, probably not gonna test
    print(f"9 : Change Dipole Node Density")
    print(f"10 : Change External Stress Rate")
    print(f"11 : Change the seed number for noise sampling")
    print(f"12 : Change dislocation position")
    print(f"13 : Change dipole glide steps")
    print(f"14 : Change max segment length for remesh (Lmax)")
    print(f"15 : Change initial stress applied to the system")
    print(f"16 : Change solid solution noise mode")
    print(f"17 : Change stacking fault noise mode")
    print(f"18 : Change grid size")
    print(" Example input 1 : 1 2 3 4")
    print(" Example input 2 : 2 4 6")

# main processing function
def selectVariables():
    if len(sys.argv) > 1:
        # sys.argv[1] is the data output path
        userInput = sys.argv[2:]
    else:
        userInput = input("Select the variables to study: ")
        userInput = userInput.split()

    # write acronym information in the output path
    #writeAcronymInfo(filePath)
    ## save the tested range
    #saveTestedRange(filePath)
    # return user inputs 
    return userInput;

def writeAcronymInfo(filePath):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    f = open(f'{filePath}Acronyms.txt','w')
    f.write(f"T : temperature\n")
    f.write(f"DL : dislocation length\n")
    f.write(f"DD : dislocation dipole distance\n")
    f.write(f"C : concentration of the alloy\n")
    f.write(f"DC : dislocation character (screw, edge)\n")
    f.write(f"L : langevin noise\n")
    f.write(f"GP : gauss point density\n")
    f.write(f"RF : remesh frequency\n")
    f.write(f"DN: periodic dipole node density\n")
    f.write(f"SR : stress rate\n")
    f.write(f"S : seed number\n")
    f.write(f"DP : Dislocation Position\n")
    f.write(f"DG : Dipole Glide Steps\n")
    f.write(f"LMAX : Max segment length\n")
    f.write(f"IES : Initial external stress\n")
    f.write(f"SS : Solid Solution Noise\n")
    f.write(f"SF : Stacking Fault Noise\n")
    f.write(f"GS : Grid Size\n")

def saveTestedRange(filePath):
    os.system(f"cp ./src/testRange.py {filePath}")

    
