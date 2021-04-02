#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import sqlite3
import sys
import time
from telnetlib import Telnet

# 将IP、用户名、密码保存到字典里
src_dict = {}
with open(r'/home/brokensmile/telephone/password_hw.txt', 'r') as f:
    for line in f:
        voip, userid, userpasswd = line.split()
        src_dict.setdefault(voip, {}).setdefault(userid, userpasswd)

# 获取分组号
no = sys.argv[1]

# 创建/连接数据库对象
conn = sqlite3.connect('A8-C.db')

# 获取游标
c = conn.cursor()

# 读取数据
t = (no, )
c.execute('SELECT ip FROM device_group WHERE groupno = ?', t)
rows = c.fetchall()

# 关闭连接
conn.close()

# 密码字典
hw_dict = {'xxxx': 'xxxx',
           'xxxx': 'xxxx'}

# 创建一个Telnet对象
tn = Telnet()
# 设置调试等级
tn.set_debuglevel(0)

# 尝试建立telnet连接
n = 0
for row in rows:
    ip = row[0]
    try:
        tn.open(ip, timeout=10)

        for password, username in hw_dict.items():
            # 匹配登录用户名提示符
            tn.read_until(b'Login:', timeout=10)
            tn.write(username.encode('ascii') + b'\n')
            time.sleep(1)
            # 匹配登录密码提示符
            tn.read_until(b'Password:', timeout=10)
            tn.write(password.encode('ascii') + b'\n')
            time.sleep(1)
            # 首次获取登录结果
            cmd_result = tn.read_very_eager().decode('ascii')
            # 判断是否成功登录
            if re.search(r'>\s*$', cmd_result):
                logging.warning(
                    f'①[{ip}: [HW, {username}, {password}]]: 登录成功...')
            else:
                logging.warning(
                    f'①[{ip}: [HW, {username}, {password}]]: 登录失败, 尝试其他用户名/密码...')
                continue
            # 执行enable
            tn.write(b'su\n')
            time.sleep(1)
            cmd_result = tn.read_very_eager().decode('ascii')
            if re.search(r'>\s*$', cmd_result, re.M | re.I):
                logging.warning(
                    f'①[{ip}: [HW, {username}, {password}]]: 进入特权模式成功...')
            else:
                logging.warning(
                    f'①[{ip}: [HW, {username}, {password}]]: 进入特权模式失败...')
                continue

            tn.write(b'shell\n')
            time.sleep(1)
            cmd_result = tn.read_very_eager().decode('ascii')
            logging.warning(cmd_result)

            # 执行修改命令
            logging.warning(f'[{ip}]: 开始执行修改...')
            cmd_result = ''
            if len(src_dict[ip]) == 1:
                for k, v in src_dict[ip].items():
                    tn.write(b'shellconfig InternetGatewayDevice.Services.VoiceService.1.VoiceProfile.1.Line.1.SIP set AuthPassword ' +
                             src_dict[ip][k].encode('ascii') + b'\n')
                    time.sleep(1)
                    cmd_result = tn.read_very_eager().decode('ascii')
                    # 写文件
                    with open(r'/home/brokensmile/telephone/data/HU/' + f'{no}.csv', 'a') as f:
                        f.write(f'{ip},{k},{v}\n')
            else:
                logging.warning(f'[{ip}]: 号码数量不唯一...')

            logging.warning(cmd_result)

            # 退出shell配置
            tn.write(b'exit\n')
            time.sleep(1)

            # 退出配置模式
            tn.write(b'quit\n')
            time.sleep(1)

            # 退出配置模式
            tn.write(b'save data\n')
            time.sleep(1)

            # 退出登录
            tn.write(b'quit\n')
            logging.warning(f'[{ip}]: 退出成功...')
            break
    except ConnectionResetError:
        logging.warning(f'[{ip}]: Telnet连接被重置...\n')
    except:
        logging.warning(f'[{ip}]: 建立Telnet连接失败...\n')
    finally:
        tn.close()

    n += 1
    logging.warning(f'当前分组已处理设备数/总设备数: {n}/{len(rows)}...')
