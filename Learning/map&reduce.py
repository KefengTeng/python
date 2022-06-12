#!/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce

def fn(x, y):
    return x * 10 + y

def char2num(s):
    digits = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
    return digits[s]

num = reduce(fn, map(char2num, '13579'))

print(num)