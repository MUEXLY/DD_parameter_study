import sys
sys.path.insert(1,'../')
import testRange


#def setTestRange(userInputs):
#    studyInputRange = []
#    for userInput in userInputs:
#        match userInput:
#            case '1':
#                studyInputRange.append(testRange.tempRange)
#            case '2':
#                studyInputRange.append(testRange.dislocLength)
#            case '3':
#                studyInputRange.append(testRange.dislocDist)
#            case '4':
#                studyInputRange.append(testRange.concentration)
#            case '5':
#                studyInputRange.append(testRange.dislocCharacter)
#            case '6':
#                studyInputRange.append(testRange.langevinNoise)
#            case '7':
#                studyInputRange.append(testRange.gaussQuadDensity)
#            case '8':
#                studyInputRange.append(testRange.remeshFreq)
#            case '9':
#                studyInputRange.append(testRange.dipoleNodeDensity)
#            case '10':
#                studyInputRange.append(testRange.stressRate)
#            case '11':
#                studyInputRange.append(testRange.seeds)
#            case '12':
#                studyInputRange.append(testRange.dislocPosition)
#            case '13':
#                studyInputRange.append(testRange.dipoleGlideStep)
#            case '14':
#                studyInputRange.append(testRange.Lmax)
#            case '15':
#                studyInputRange.append(testRange.ExternalStress0)
#            case '16':
#                studyInputRange.append(testRange.SSnoise)
#            case '17':
#                studyInputRange.append(testRange.SFnoise)
#            case '18':
#                studyInputRange.append(testRange.gridsize)
#            case _:
#                raise ValueError("this is not available option")
#    return studyInputRange;

def setTestRange(parameterLists: list):
    testRanges = {}
    lineTensionsToTest = []
    temperatureToTest = []
    dislocLengthToTest = []
    dislocDipoleDistToTest = []
    dislocCharacterToTest = []
    dislocPositionToTest = []
    dislocDipoleGlideStepToTest = []
    alloyToTest = []
    langevinToTest = []
    gaussPointDensityToTest = []
    remeshFreqToTest = []
    periodicDipoleNodeDensityToTest = []
    stressRateToTest = []
    initialStressToTest = []
    maxSegLengthToTest = []
    gridSizeToTest = []
    for userInput in parameterLists:
        match userInput:
            case 'LT':
                pass
            case 'T':
                testRanges['temperature'] = testRange.tempRange
            case 'A':
            case 'DC':
            case 'DD':
            case 'L':
            case 'GP':
            case 'RF':
            case 'DN':
            case 'SR':
            case 'DP':
            case 'DG':
            case 'LMAX':
            case 'IES': 
            case 'DG':
            case _:
                raise ValueError("this is not available option")
    return studyInputRange;
