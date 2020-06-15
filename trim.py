#!/bin/env python3
# -*- coding: utf-8 -*-

def trim(s):

    while s[-1:] == ' ':
       s = s[:-1]

    while s[:1] == ' ':
       s = s[1:]

    return s

if __name__ == '__main__':
    print(trim('  nihao '))
