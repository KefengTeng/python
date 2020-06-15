#!/bin/env python3
# -*- coding: utf-8 -*-

import re
from datetime import datetime, timezone, timedelta 

def to_timestamp(dt_str, tz_str):
    tzRegex = re.compile(r'UTC(.*):')
    tZone = 0 - int(tzRegex.match(tz_str).group(1))
    return (datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S') + timedelta(hours = tZone)).timestamp()

# 测试:
t1 = to_timestamp('2015-6-1 08:10:30', 'UTC+7:00')
assert t1 == 1433092230.0, t1

t2 = to_timestamp('2015-5-31 16:10:30', 'UTC-09:00')
assert t2 == 1433092230.0, t2

print('ok')
