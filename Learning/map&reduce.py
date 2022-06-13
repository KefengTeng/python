#!/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce


def fn(x, y):
    return x * 10 + y


def char2num(s):
    digits = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
              '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
    return digits[s]


print(reduce(fn, map(char2num, '13579')))

DIGITS = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
          '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}


def str2int(s):
    def fn(x, y):
        return x * 10 + y

    def char2num(s):
        return DIGITS[s]
    return reduce(fn, map(char2num, s))


print(str2int('13579'))


def char2num(s):
    return DIGITS[s]


def str2intn(s):
    return reduce(char2num, )


def normalize(name):
    return name[0].upper()+name[1:].lower()


print(list(map(normalize, ['adam', 'LISA', 'barT'])))


def prod(L):
    return reduce(lambda x, y: x * y, L)


L = [1, 3, 5, 7, 9]

print(prod(L))

digits = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
          '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}


def str2float(s):

    # 字符串转数字
    def str2num(s):
        return digits[s]

    # 按小数点分隔字符串
    s = s.split('.')

    # 整数部分x * 10 + y, 浮点数部分x * 10 + y / 10 ** 小数长度
    return reduce(lambda x, y: x * 10 + y, map(str2num, s[0])) + reduce(lambda x, y: x * 10 + y, map(str2num, s[1]))/(10 ** len(s[1]))


s = '123.456'

print(str2float(s))
