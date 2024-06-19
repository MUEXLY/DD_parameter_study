#!/bin/python3

testRange = {
    'temperature' : [0],
    'alloy' : ['AlMg5'],
    'lineTension' : [1],
    'boxSize' : [
        [500,500,3000]
        ],
    'periodicDipoleSlipSystemIDs' : [
        '0 1',
    ],
    'periodicDipoleExitFaceIDs': [
        '1 1',
    ],
    'periodicDipoleNodes': [
        '150 150',
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
    'dxMax': [
        1,
        0.8,
        0.6,
        0.5,
        0.3,
        0.1,
        0.02,
    ],
}
