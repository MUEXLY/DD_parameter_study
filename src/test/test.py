#!/bin/python

import detectCRSS as dc

def main():
    bPIndex = 5
    path = '/home/anon/Documents/Research/MoDELib/tutorials/DislocationDynamics/a/T1DL100_100_2000DD1000C5DC0L0GP2S32DP50_50_1000DG20SS2SF0IES0.0_0.0_0.00034842105263157896_0.0_0.0_0.0_0.00034842105263157896_0.0_0.0GS256_256'
    t, d = dc.loadData(f'{path}', bPIndex)
    print(t)
    print(d)
    print(len(t), len(d))
    exit()

    gg = dc.calc1stDiff(t, d)
    print(gg)
    a = dc.detectCRSS(gg)
    print(a)

    return 0;

main()
