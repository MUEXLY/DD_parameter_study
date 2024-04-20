def initDataAcronyms(userInput):
    datAcronym = []
    for i in range(len(userInput)):
        match userInput[i]:
            case '1':
                acronym = 'T'
            case '2':
                acronym = 'DL'
            case '3':
                acronym = 'DD'
            case '4':
                acronym = 'C'
            case '5':
                acronym = 'DC'
            case '6':
                acronym = 'L'
            case '7':
                acronym = 'GP'
            case '8':
                acronym = 'RF'
            case '9':
                acronym = 'DN'
            case '10':
                acronym = 'SR'
            case '11':
                acronym = 'S'
            case '12':
                acronym = 'DP'
            case '13':
                acronym = 'DG'
            case '14':
                acronym = 'LMAX'
            case '15':
                acronym = 'IES'
            case '16':
                acronym = 'SS'
            case '17':
                acronym = 'SF'
            case '18':
                acronym = 'GS'
            case _:
                print('Something is wrong')
                exit()
        datAcronym.append(acronym)
    return datAcronym;
