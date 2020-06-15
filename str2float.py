#!/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce

Dict_str = {'0': 1, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, \
    '6': 6, '7': 7, '8': 8, '9': 9, '10': 10}

def char2num(t):

    return Dict_str[t]

def str2float(s):

    L = s.split('.')
    
    Int = reduce(lambda x, y: x * 10 + y, map(char2num, L[0]))
    Float = reduce(lambda x, y: x * 10 + y, map(char2num, L[1]))
  
    return Int + (Float / pow(10, len(L[1])))

print('str2float(\'123.456\') =', str2float('123.456'))

if abs(str2float('123.456') - 123.456) < 0.00001:
    print('测试成功!')
else:
    print('测试失败!')
