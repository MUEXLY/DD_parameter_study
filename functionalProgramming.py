import numpy as np

def changeParameter(parameter, value):

def modifyTxt(func, txtFile) -> None:
    with open(txtFile, 'w') as file:
        for line in file:
            file.write(func(line))

paramsToChange = ['DD', 'T']
paramsToChangeSame = ['DD']
ddConfigFile = 'DD.txt'
modifyTxt(changeParameter, ddConfigFile)

#load text file

# Define a pure function that calculates the square of a number
#def square(x):
#    return x * x
#
## Define a higher-order function that applies a function to all elements in a list
#def apply_function(func, lst):
#    return [func(item) for item in lst]
#
## Example usage
#numbers = [1, 2, 3, 4, 5]
#squared_numbers = apply_function(square, numbers)
#
#print(squared_numbers)  # Output: [1, 4, 9, 16, 25]
#
