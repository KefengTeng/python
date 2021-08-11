#!/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import time
import logging
import sqlite3
import subprocess
from telnetlib import Telnet

# 获取分组号
no = sys.argv[1]

# 创建/连接数据库对象
conn = sqlite3.connect('ip_group.db')

# 获取游标
c = conn.cursor()

# 读取数据
t = (no, )
c.execute('SELECT ip, username, password FROM telnet_group WHERE groupno = ?', t)
rows = c.fetchall()

# 关闭连接
conn.close()

hour = time.strftime('%Y-%m-%d_%H', )

# 创建一个Telnet对象
tn = Telnet()
# 设置调试等级
tn.set_debuglevel(0)

# 连通性测试
n = 0
for row in rows:
    (ip, username, password) = row
    # ping测试
    ping_result = subprocess.call(["ping", "-c", "3", "-n", "-W", "2", ip])
    if ping_result == 0:
        ping_status = 1
    else:
        ping_status = 0

    # telnet测试
    try:
        tn.open(ip, timeout=10)
        # 匹配登录用户名提示符
        if tn.read_until(b'login:', timeout=10) or tn.read_until(b'Username:', timeout=10):
            tn.write(username.encode('ascii') + b'\n')
            time.sleep(1)

        # 匹配登录密码提示符
        tn.read_until(b'Password:', timeout=10)
        tn.write(password.encode('ascii') + b'\n')
        time.sleep(3)

        # 获取登录结果
        cmd_result = tn.read_very_eager().decode('ascii')
        logging.warning(cmd_result)

        # 判断是否成功登录
        if re.search(r'>\s*$|>#\s*$', cmd_result):
            logging.warning(f'[{ip}]: 登录成功...')
            telnet_status = 1
        else:
            logging.warning(f'[{ip}]: 登录失败...')
            telnet_status = 0
    except ConnectionResetError:
        logging.warning(f'[{ip}]: Telnet连接被重置...\n')
        telnet_status = -1
    except:
        logging.warning(f'[{ip}]: 建立Telnet连接异常...\n')
        telnet_status = -1
    finally:
        tn.close()

    with open(r'/tmp/' + f'telnet_{hour}.txt', 'a') as f:
        f.write(f'{ip}\t{ping_status}\t{telnet_status}\n')

    n += 1
    logging.warning(f'当前分组已处理设备数/总设备数: {n}/{len(rows)}...')