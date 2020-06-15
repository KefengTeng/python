#!/bin/env python3
# -*- coding: utf-8 -*-

import time, functools

def metric(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kw):
        startTime = time.time()
        result = fn(*args, **kw)
        stopTime = time.time()
        print('%s excuted in %.4fs!' %(fn.__name__, (stopTime - startTime)))
        return result
    return wrapper

@metric
def fast(x, y):
    time.sleep(0.5)
    return x + y

@metric
def slow(x, y, z):
    time.sleep(0.1234)
    return x * y * z

f = fast(11, 22)
s = slow(11, 22, 33)

if f != 33:
    print('f测试失败!')
elif s != 7986:
    print('s测试失败!')
