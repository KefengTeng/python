#!/bin/env python3
# -*- coding: utf-8 -*-

# def lazy_sum(*args):
#     def sum():
#         ax = 0
#         for n in args:
#             ax += n
#         return ax
#     return sum
# 
# f1 = lazy_sum(1, 3, 5, 7 ,9) 
# f2 = lazy_sum(1, 3, 5, 7 ,9) 
# print(f1(), f2())
# 
# print(f1 == f2)

def createCounter():
    '''
    list的原理类似C语言的数组和指针，不受作用域影响。
    直接改变值对应的地址。也就是说不是改变值的引用，而是永久改变值本身。
    '''
    L = [0]
    def counter():
        L[0] += 1
        return L[0]
    return counter

counterA = createCounter()

print(counterA(), counterA(), counterA(), counterA(), counterA()) 

counterB = createCounter()
if [counterB(), counterB(), counterB(), counterB()] == [1, 2, 3, 4]:
    print('测试通过!')
else:
    print('测试失败!')
