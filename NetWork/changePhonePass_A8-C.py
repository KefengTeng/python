#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import sqlite3
import sys
import time
from telnetlib import Telnet

# 将用户名密码保存到字典里
src_dict = {}
with open(r'/home/brokensmile/telephone/password.txt', 'r') as f:
    for line in f:
        userid, userpasswd = line.split()
        src_dict.setdefault(userid, userpasswd)

username = 'xxxx'
password = 'xxxx'

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

        # 匹配登录用户名提示符
        tn.read_until(b'Username:', timeout=10)
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
                f'①[{ip}: [A8-C, {username}, {password}]]: 登录成功...')
        else:
            logging.warning(
                f'①[{ip}: [A8-C, {username}, {password}]]: 登录失败...')
            continue
        # 执行enable
        tn.write(b'enable\n')
        time.sleep(1)
        # 获取enable结果
        cmd_result = tn.read_very_eager().decode('ascii')
        logging.warning(cmd_result)
        # 判断是否成功进入特权模式
        if re.search(r'#\s*$', cmd_result):
            logging.warning(
                f'②[{ip}: [A8-C, {username}, {password}]]: 进入特权模式成功...')
        else:
            logging.warning(
                f'②[{ip}: [A8-C, {username}, {password}]]: 进入特权模式失败...')
            continue
        # 执行采集命令
        logging.warning(f'[{ip}]: 开始执行采集...')
        tn.write(b'show running-config voip\n')
        time.sleep(1)
        cmd_result = tn.read_very_eager().decode('ascii')
        while cmd_result.endswith('bytes)'):
            tn.write(b' ')
            time.sleep(1)
            cmd_result += tn.read_very_eager().decode('ascii')
        logging.warning(cmd_result)
        # 号码对应接口字典
        phone_dict = {}
        for line in cmd_result.split('\r\n'):
            if re.search(r'sip pots authentication.*tj.ctcims.cn', line, re.I):
                (userid, port) = re.search(
                    r'sip pots authentication (\S+)\@tj.ctcims.cn potsId (\d+)', line, re.I).groups()
                phone_dict.setdefault(userid, port)
        logging.warning(f'当前设备业务号码: --->>>{phone_dict}\n')

        # 进入配置模式
        tn.write(b'config terminal\n')
        time.sleep(1)
        # 进入语音配置
        tn.write(b'voip\n')
        time.sleep(1)
        cmd_result = tn.read_very_eager().decode('ascii')
        logging.warning(cmd_result)

        # 遍历号码对应接口字典, 判断号码是否在密码字典中存在, 存在的话下发改密码配置
        for k, v in phone_dict.items():
            cmd_result = ''
            if k in src_dict:
                tn.write(b'sip pots authentication password ' + src_dict[k].encode('ascii') +
                         b' potsId ' + v.encode('ascii') + b'\n')
                time.sleep(1)
                cmd_result += tn.read_very_eager().decode('ascii')

                # 写文件
                with open(r'/home/brokensmile/telephone/data/A8-C/' + f'{no}.csv', 'a') as f:
                    f.write(f'{ip},A8-C,{k}\n')

            logging.warning(cmd_result)

        # 退出语音配置
        tn.write(b'exit\n')
        time.sleep(1)

        # 退出配置模式
        tn.write(b'exit\n')
        time.sleep(1)

        # 保存配置
        tn.write(b'write file\n')
        time.sleep(1)

        # 退出登录
        tn.write(b'quit\n')
        logging.warning(f'[{ip}]: 退出成功...')
    except ConnectionResetError:
        logging.warning(f'[{ip}]: Telnet连接被重置...\n')
    except:
        logging.warning(f'[{ip}]: 建立Telnet连接失败...\n')
    finally:
        tn.close()

    n += 1
    logging.warning(f'当前分组已处理设备数/总设备数: {n}/{len(rows)}...')
