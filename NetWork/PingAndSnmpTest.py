#!/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
import sqlite3
import subprocess

# 获取分组号
no = sys.argv[1]

# 创建/连接数据库对象
conn = sqlite3.connect('ip_group.db')

# 获取游标
c = conn.cursor()

# 读取数据
t = (no, )
c.execute('SELECT ip, ro, rw FROM snmp_group WHERE groupno = ?', t)
rows = c.fetchall()

# 关闭连接
conn.close()

hour = time.strftime('%Y-%m-%d_%H', )

# 连通性测试
n = 0
for row in rows:
    (ip, ro, rw) = row
    # ping测试
    ping_result = subprocess.call(["ping", "-c", "3", "-n", "-W", "2", ip])
    if ping_result == 0:
        ping_status = 1
    else:
        ping_status = 0

    # snmp读测试
    snmpr_result = subprocess.call(["snmpwalk", "-v2c", "-c", ro, ip, 'sysobject'])
    if snmpr_result == 0:
        snmpr_status = 1
    else:
        snmpr_status = 0

    # snmp写测试
    snmpw_result = subprocess.call(["snmpwalk", "-v2c", "-c", rw, ip, 'sysobject'])
    if snmpw_result == 0:
        snmpw_status = 1
    else:
        snmpw_status = 0

    with open(r'/tmp/' + f'snmp_{hour}.txt', 'a') as f:
        f.write(f'{ip}\t{ping_status}\t{snmpr_status}\t{snmpw_status}\n')

    n += 1
    logging.warning(f'当前分组已处理设备数/总设备数: {n}/{len(rows)}...')