#!/bin/python3

testRange = {
    'temperature' : [1],
    'alloy' : ['AlMg5'],
    'lineTension' : [10,15,20],
    'boxSize' : [
        [100,100,1000]
        ],
    'periodicDipoleSlipSystemIDs' : [
        '0 1',
    ],
    'periodicDipoleExitFaceIDs': [
        '1 1',
    ],
    'periodicDipoleNodes': [
        '10 10',
    ],
    'periodicDipolePoints': [
        '50 50 0\n 30 30 0',
    ],
    'periodicDipoleHeights': [
        '700 700',
    ],
    'periodicDipoleGlideSteps': [
        '30 60',
    ],
}

#AlMg5 mu0_SI = 28.595 [GPa]
# AlMg10 mu0_SI = 26.784 [GPa]
# AlMg15 mu0_SI = 24.972 [GPa]



