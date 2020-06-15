#!/bin/env python3
# -*- coding: utf-8 -*-

import psutil

print(psutil.cpu_count())
print(psutil.cpu_count(logical=False))

for x in range(10):
    print(psutil.cpu_percent(interval=1, percpu=True))