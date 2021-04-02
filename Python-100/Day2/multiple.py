#!/bin/env python3
# -*- coding: utf-8 -*-

'''
求x, y的最大公约数和最小公倍数
'''
x = int(input('x = '))
y = int(input('y = '))

# 数字小的排前面
if x > y:
    x, y = y, x

# 将x按-1递减, 如果都能被x, y整除, 则为最大公约数
for factor in range(x, 0, -1):
    if x % factor == 0 and y % factor == 0:
        print(f'{x}和{y}的最大公约数是{factor}')
        print('%d和%d的最小公倍数是%d' % (x, y, x * y // x))
        break
