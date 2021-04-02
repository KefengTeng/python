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
with open(r'/home/brokensmile/telephone/password_zt.txt', 'r') as f:
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

        # 取设备回显, 判断设备类型
        DeviceType = tn.expect([], timeout=1)[2].decode('ascii').strip()

        # 截取设备型号
        model = 'null'
        if re.search(r'F\d{3}', DeviceType, re.M | re.I):
            model = re.search(r'(F\d{3})', DeviceType).group(1)

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
        if re.search(r'#\s*$', cmd_result):
            logging.warning(
                f'①[{ip}: [{model}, {username}, {password}]]: 登录成功...')
        else:
            logging.warning(
                f'①[{ip}: [{model}, {username}, {password}]]: 登录失败...')
            continue

        # 执行采集命令
        logging.warning(f'[{ip}]: 开始执行采集...')
        tn.write(b'sendcmd 1 DB p VoIPSIPLine\n')
        time.sleep(2)
        cmd_result = tn.read_very_eager().decode('ascii')
        logging.warning(cmd_result)

        # 号码对应接口字典
        phone_dict = {}
        for line in cmd_result.split('\r\n'):
            if re.search(r'Row No="\d"', line, re.I):
                index = re.search(r'Row No="(\d)"', line, re.I).group(1)
                phone_dict.setdefault(index, '')
            if re.search(r'DM name="AuthUserName" val="\S+"', line, re.I):
                phone_dict[index] = re.search(
                    r'DM name="AuthUserName" val="(\S+)"', line, re.I).group(1)

        logging.warning(f'当前设备业务号码: --->>>{phone_dict}\n')

        # 遍历号码对应接口字典, 判断号码是否在密码字典中存在, 存在的话下发改密码配置
        for k, v in phone_dict.items():
            cmd_result = ''
            if v in src_dict:
                logging.warning(f'[{ip}]: 开始执行修改...')
                tn.write(b'sendcmd 1 DB set VoIPSIPLine ' + k.encode('ascii') + b' AuthPassword ' +
                         src_dict[v].encode('ascii') + b'\n')
                time.sleep(1)
                cmd_result += tn.read_very_eager().decode('ascii')

                # 写文件
                with open(r'/home/brokensmile/telephone/data/ZT/' + f'{no}.csv', 'a') as f:
                    f.write(f'{ip},{model},{v}\n')

            logging.warning(cmd_result)

        # 保存配置
        tn.write(b'sendcmd 1 DB save\n')
        time.sleep(1)
        cmd_result = tn.read_very_eager().decode('ascii')
        logging.warning(cmd_result)

        # 退出登录
        tn.write(b'exit\n')
        logging.warning(f'[{ip}]: 退出成功...')
    except ConnectionResetError:
        logging.warning(f'[{ip}]: Telnet连接被重置...\n')
    except:
        logging.warning(f'[{ip}]: 建立Telnet连接失败...\n')
    finally:
        tn.close()

    n += 1
    logging.warning(f'当前分组已处理设备数/总设备数: {n}/{len(rows)}...')
