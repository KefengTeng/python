#!/bin/env python3
# -*- coding: utf-8 -*-

'''
百钱百鸡
'''

for x in range(20):
    for y in range(33):
        z = 100 - y - x
        if x * 5 + y * 3 + z / 3 == 100:
            print(f'公鸡:{x}只, 母鸡:{y}只, 小鸡:{z}只')
