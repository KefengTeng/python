#!/bin/env python3
# -*- coding: utf-8 -*-

def triangles():
    # L = [1] 
    # while True:
    #     yield L
    #     L = [sum(i) for i in zip([0] + L, L + [0])]
    L = [1]
    while True:
        yield L
        L = [1] + [L[i] +  L[i + 1] for i in range(len(L) - 1)] + [1]

n = 0

results = []

for t in triangles():
    results.append(t)
    n += 1
    if n == 10:
        break

for t in results:
    print(t)

print(results)
