#!/bin/env python3
# -*- coding: utf-8 -*-

# 打印三角形图案

row = int(input('请输入行数: '))

# *
# **
# ***
# ****
# *****

for i in range(1, 6):
    print('*' * i)

for i in range(row):
    for _ in range(i + 1):
        print('*', end='')
    print()

#     *
#    **
#   ***
#  ****
# *****
for i in range(5, 0, -1):
    print(' ' * (i - 1), '*' * (6 - i), sep='')

for i in range(row):
    for j in range(row):
        if j < row - i - 1:
            print(' ', end='')
        else:
            print('*', end='')
    print()

#     *
#    ***
#   *****
#  *******
# *********
for i in range(1, 10, 2):
    print(' ' * int((9 - i) / 2), '*' * i, ' ' * int((9 - i) / 2), sep='')

for i in range(row):
    for _ in range(row - i - 1):
        print(' ', end='')
    for _ in range(2 * i + 1):
        print('*', end='')
    print()
