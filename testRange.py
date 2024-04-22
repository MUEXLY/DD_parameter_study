#!/bin/python3

#T : temperature
#A : alloy to test
#LT : line tension
#DL : dislocation length
#DD : dislocation dipole distance
#DC : dislocation character (screw, edge)
#L : langevin noise
#GP : gauss point density
#RF : remesh frequency
#DN: periodic dipole node density
#SR : stress rate
#DP : Dislocation Position
#DG : Dipole Glide Steps
#LMAX : Max segment length
#IES : Initial external stress
#SS : Solid Solution Noise
#SF : Stacking Fault Noise
#GS : Grid Size
#S : seed number # removed, it needs to change anyway

testRange = {
    'T' : [1, 2],
    'A' : [],
    'LT' : [2.0, 3.0],
    'DL' : [],
    'DD' : [],
    'DC' : [],
    'L' : [],
    'GP' : [],
    'RF' : [],
    'DN' : [],
    'SR' : [],
    'DP' : [],
    'DG' : [],
    'LMAX' : [],
#    'IES' : [],
    'SS' : [],
    'SF' : [],
    'GS' : [],
}

# Physcis
#tempRange = [ 1 ] # {$MoDeLib}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/polycrystal.txt
#dislocLength = [ [200, 200, 4000] ] # dislcoation length [ xlength, ylength, zlength, # of glide planes between dipole ]
#dislocDist = [2000]
#concentration = [ 5 ] # {$MoDeLib}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/polycrystal.txt, at every different concentration, I need to resample the noise
#dislocCharacter = [ 0 ] # {$MoDeLib}/tutorials/DislocationDynamics/MicrostructureLibrary/periodicDipole.txt
#langevinNoise = [ 0 ] # {$MoDeLib}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/DD.txt
#
#gaussQuadDensity = [ 2 ] # {$MoDeLib}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/DD.txt, quadPerLength=1
#remeshFreq = [ ]
##meshsize = [ 0,1 ] # remesh or not, {$MoDeLib}/tutorials/DislocationDynamics/periodicDomains/uniformLoadController/inputFiles/DD.txt
#dipoleNodeDensity = [ 0, 1, 3, 5, 10, 20 ]
#stressRate = [ ] 
#seeds = [ 1234 ]
#dislocPosition = [ [100, 100, 1000] ]
#dipoleGlideStep = [ 20 ]
#Lmax = [ ]
#ExternalStress0 = [ 
#[0.0, 0.0, 2e-05, 0.0, 0.0, 0.0, 2e-05, 0.0, 0.0],
#[0.0, 0.0, 4.526315789473684e-05, 0.0, 0.0, 0.0, 4.526315789473684e-05, 0.0, 0.0],
#[0.0, 0.0, 7.052631578947368e-05, 0.0, 0.0, 0.0, 7.052631578947368e-05, 0.0, 0.0],
#[0.0, 0.0, 9.578947368421052e-05, 0.0, 0.0, 0.0, 9.578947368421052e-05, 0.0, 0.0],
#[0.0, 0.0, 0.00012105263157894736, 0.0, 0.0, 0.0, 0.00012105263157894736, 0.0, 0.0],
#[0.0, 0.0, 0.0001463157894736842, 0.0, 0.0, 0.0, 0.0001463157894736842, 0.0, 0.0],
#[0.0, 0.0, 0.00017157894736842105, 0.0, 0.0, 0.0, 0.00017157894736842105, 0.0, 0.0],
#[0.0, 0.0, 0.0001968421052631579, 0.0, 0.0, 0.0, 0.0001968421052631579, 0.0, 0.0],
#[0.0, 0.0, 0.00022210526315789473, 0.0, 0.0, 0.0, 0.00022210526315789473, 0.0, 0.0],
#[0.0, 0.0, 0.0002473684210526316, 0.0, 0.0, 0.0, 0.0002473684210526316, 0.0, 0.0],
#[0.0, 0.0, 0.0002726315789473684, 0.0, 0.0, 0.0, 0.0002726315789473684, 0.0, 0.0],
#[0.0, 0.0, 0.0002978947368421052, 0.0, 0.0, 0.0, 0.0002978947368421052, 0.0, 0.0],
#[0.0, 0.0, 0.0003231578947368421, 0.0, 0.0, 0.0, 0.0003231578947368421, 0.0, 0.0],
#[0.0, 0.0, 0.00034842105263157896, 0.0, 0.0, 0.0, 0.00034842105263157896, 0.0, 0.0],
#[0.0, 0.0, 0.0003736842105263158, 0.0, 0.0, 0.0, 0.0003736842105263158, 0.0, 0.0],
#[0.0, 0.0, 0.0003989473684210526, 0.0, 0.0, 0.0, 0.0003989473684210526, 0.0, 0.0],
#[0.0, 0.0, 0.00042421052631578946, 0.0, 0.0, 0.0, 0.00042421052631578946, 0.0, 0.0],
#[0.0, 0.0, 0.00044947368421052633, 0.0, 0.0, 0.0, 0.00044947368421052633, 0.0, 0.0],
#[0.0, 0.0, 0.00047473684210526314, 0.0, 0.0, 0.0, 0.00047473684210526314, 0.0, 0.0],
#[0.0, 0.0, 0.0005, 0.0, 0.0, 0.0, 0.0005, 0.0, 0.0],
#                   ] 
#SSnoise = [ 2 ]
#SFnoise = [ 1 ]
#gridsize = [ [512, 512] ]

#AlMg5 mu0_SI = 28.595 [GPa]
# AlMg10 mu0_SI = 26.784 [GPa]
# AlMg15 mu0_SI = 24.972 [GPa]



