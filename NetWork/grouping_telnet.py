#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import subprocess

# 分组数量
num = int(input('请输入分组数量: '))

# 创建/连接数据库对象
conn = sqlite3.connect('ip_group.db')

# 获取游标
c = conn.cursor()

# 建表
c.execute('CREATE TABLE IF NOT EXISTS telnet_group (ip, username, password, groupno)')

# 清空表数据
c.execute('DELETE FROM telnet_group')

# 插入数据
device = []
with open(r'/tmp/telnet.txt', 'r') as f:
    # 列表解析, 去掉换行符
    lines = [x.strip() for x in f.readlines()]
    # 列表解析, 分组
    lines_list = [lines[i:i+num] for i in range(0, len(lines), num)]
    # 标记分组, 最后一个分组长度不固定
    for group in lines_list:
        for count in range(1, len(group)+1):
            device.append((group[count-1].split('\t')[0], group[count-1].split('\t')[1], group[count-1].split('\t')[2], 'G1' + str(count).zfill(2)))

c.executemany('INSERT INTO telnet_group VALUES (?, ?, ?, ?)', device)

# 提交
conn.commit()

# 读取分组
c.execute('SELECT DISTINCT groupno FROM telnet_group')
rows = c.fetchall()

# 关闭连接
conn.close()

# 调用进程
for row in rows:
    with open(r'/tmp/' + f'telnet_{row[0]}.txt', 'a') as f:
        subprocess.Popen(['/tmp/PingAndSnmpTest.py',
                          row[0], '&'], stdout=f, stderr=f)
