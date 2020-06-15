#!/bin/env python3
# -*- coding: utf-8 -*-

def findMinAndMax(L):
    Min, Max = None, None 

    if len(L) > 0:
        Min, Max = L[0], L[0]
        for num in L:
            if num < Min:
                Min = num 
            if num > Max:
                Max = num

    return (Min, Max)

if __name__ == '__main__':
    print(findMinAndMax([7]))
