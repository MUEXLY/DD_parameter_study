#!/bin/python3

testRange = {
    'temperature' : [0],
    'alloy' : ['AlMg5'],
    'lineTension' : [1],
    'boxSize' : [
        [400,400,3000],
        [600,600,3000],
        [800,800,3000]
        ],
    'periodicDipoleSlipSystemIDs' : [
        '0 1',
    ],
    'periodicDipoleExitFaceIDs': [
        '1 1',
    ],
    'periodicDipoleNodes': [
        '100 100',
        '200 200',
    ],
    'periodicDipolePoints': [
        '0 0 0\n 0 0 0',
    ],
    'periodicDipoleHeights': [
        '8000 8000',
    ],
    'periodicDipoleGlideSteps': [
        '1 200',
    ],
}
