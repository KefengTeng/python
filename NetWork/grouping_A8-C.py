#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import subprocess

# 分组大小
num = int(input('请输入分组数量: '))

# 创建/连接数据库对象
conn = sqlite3.connect('A8-C.db')

# 获取游标
c = conn.cursor()

# 建表
c.execute('CREATE TABLE IF NOT EXISTS device_group (ip, groupno)')

# 清空表数据
c.execute('DELETE FROM device_group')

# 插入数据
device = []
with open(r'/home/brokensmile/telephone/A8-C.txt', 'r') as f:
    # 列表解析, 去掉换行
    lines = [x.strip() for x in f.readlines()]
    # 列表解析, 分组
    lines_list = [lines[i:i+num] for i in range(0, len(lines), num)]
    # 标记分组, 最后一个分组长度不固定
    for group in lines_list:
        for count in range(1, len(group)+1):
            device.append((group[count-1], 'G1' + str(count).zfill(2)))

c.executemany('INSERT INTO device_group VALUES (?, ?)', device)

# 提交
conn.commit()

# 读取分组
c.execute('SELECT DISTINCT groupno FROM device_group')
rows = c.fetchall()

# 关闭连接
conn.close()

# 调用进程
for row in rows:
    with open(f'/home/brokensmile/telephone/logs/A8-C/{row[0]}.txt', 'a') as f:
        subprocess.Popen(['/home/brokensmile/telephone/changePhonePass_A8-C.py',
                          row[0], '&'], stdout=f, stderr=f)
