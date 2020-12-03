#!/bin/env python3
# -*- coding: utf-8 -*-

'''
寻找水仙花数
1^3 + 5^3 + 3^3 = 153
'''

for num in range(100, 1000):
    # 求余
    low = num % 10
    # 地板除然后求余
    mid = num // 10 % 10
    # 地板除
    high = num // 100
    if high ** 3 + mid ** 3 + low ** 3 == num:
        print(num)

'''
反转正整数
'''
num = int(input('num = '))
reversed_num = 0
while num > 0:
    reversed_num = reversed_num * 10 + num % 10
    num //= 10
print(reversed_num)
