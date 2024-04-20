#!/bin/python

inputValue = (1, [100, 100, 2000], 1000, 5, 0, 0, 2, 32, [50, 50, 1000], 20, 2, 0, [0.0, 0.0, 0.009333333333333332, 0.0, 0.0, 0.0, 0.009333333333333332, 0.0, 0.0], [256, 256])

blacklist = []
blacklist.append(32)
print(blacklist)

if 32 in inputValue:
    print("yes")

for blist in blacklist:
    if blist in inputValue:
        print('yes')
