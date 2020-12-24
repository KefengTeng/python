#!/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import time
import logging
#import cx_Oracle
from telnetlib import Telnet

# 将用户名密码保存到字典里
src_dict = {}
# with open(r'/root/tengkf/F832/password.txt', 'r') as f:
#     for line in f:
#         userid, userpasswd = line.split()
#         src_dict.setdefault(userid, userpasswd)

username = 'telecomadmin'
password = 'nE7jA%5m'
enable = ' '

# 创建一个Telnet对象
tn = Telnet()
# 设置调试等级
tn.set_debuglevel(0)

# 尝试建立telnet连接
ip = '10.87.24.14'
try:
    tn.open(ip, timeout=10)
except:
    logging.warning(f'[{ip}]: 建立Telnet连接失败...\n')

# 取设备回显, 判断设备类型
DeviceType = tn.expect([], timeout=1)[2].decode('ascii').strip()
if re.search(r'>>', DeviceType):
    # 华为
    pass
elif re.search(r'##', DeviceType):
    # 中兴
    pass
else:
    # 瑞斯康达
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
        logging.warning(f'[{ip}]: 登录成功...')
    else:
        logging.warning(f'[{ip}]: 登录失败...')

    # 执行enable
    tn.write(b'enable\n')
    time.sleep(1)

    # 获取enable结果
    cmd_result = tn.read_very_eager().decode('ascii')
    logging.warning(cmd_result)

    # 判断是否成功进入特权模式
    if re.search(r'#\s*$', cmd_result):
        logging.warning(f'[{ip}]: 进入特权模式成功...')
    else:
        logging.warning(f'[{ip}]: 进入特权模式失败...')

    # 执行采集命令
    tn.write(b'show running-config voip\n')
    time.sleep(1)

    cmd_result = tn.read_very_eager().decode('ascii')
    while cmd_result.endswith('bytes)'):
        tn.write(b' ')
        time.sleep(1)
        cmd_result += tn.read_very_eager().decode('ascii')
    logging.warning(cmd_result)

    # 号码对应接口字典
    phone_list = []
    for line in cmd_result.split('\r\n'):
        if re.search(r'sip pots authentication.*tj.ctcims.cn', line, re.I):
            phone_list.append(re.search(
                r'sip pots authentication (\S+)\@tj.ctcims.cn potsId (\d+)', line, re.I).group(1))

    logging.warning(f'当前设备业务号码: --->>>{phone_list}\n')
