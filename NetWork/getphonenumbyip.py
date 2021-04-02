#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import sqlite3
import sys
import time
from telnetlib import Telnet

# 获取分组号
no = sys.argv[1]

# 创建/连接数据库对象
conn = sqlite3.connect('ip_group.db')

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
        if re.search(r'>>', DeviceType):
            # 华为

            # 密码字典
            zt_dict = {'xxxx': 'xxxx',
                       'xxxx': 'xxxx',
                       'xxxx': 'xxxx'}

            for password, username in zt_dict.items():
                # 匹配登录用户名提示符
                tn.read_until(b'>>User name:', timeout=10)
                tn.write(username.encode('ascii') + b'\n')
                time.sleep(1)

                # 匹配登录密码提示符
                tn.read_until(b'>>User password:', timeout=10)
                tn.write(password.encode('ascii') + b'\n')
                time.sleep(3)

                # 首次获取登录结果
                cmd_result = tn.read_very_eager().decode('ascii')

                # 截取设备型号
                model = 'null'
                if re.search(r'Software\s+\(\S+\)', cmd_result, re.M | re.I):
                    model = re.search(r'Software\s+\((\S+)\)',
                                      cmd_result, re.M).group(1)

                # 设备首次登陆提醒处理
                if re.search(r"Press\s+'Q'\s+to\s+break", cmd_result, re.M | re.I):
                    tn.write(b'Q')
                    time.sleep(1)
                    cmd_result = tn.read_very_eager().decode('ascii')
                elif re.search(r"Are you sure to modify system time", cmd_result, re.M | re.I):
                    tn.write(b'n')
                    time.sleep(1)
                    cmd_result = tn.read_very_eager().decode('ascii')

                # 判断是否成功登录
                if re.search(r'>\s*$', cmd_result):
                    logging.warning(
                        f'①[{ip}: [{model}, {username}, {password}]]: 登录成功...')
                else:
                    logging.warning(
                        f'①[{ip}: [{model}, {username}, {password}]]: 登录失败, 尝试其他用户名/密码...')
                    # 登录失败则尝试下一组用户名/密码
                    continue

                # 执行enable
                tn.write(b'enable\n')

                # 获取enable结果
                time.sleep(3)
                cmd_result = tn.read_very_eager().decode('ascii')
                logging.warning(cmd_result)

                # 判断是否成功进入特权模式
                if re.search(r'#\s*$', cmd_result):
                    logging.warning(
                        f'②[{ip}: [{model}, {username}, {password}]]: 进入特权模式成功...')
                else:
                    logging.warning(
                        f'②[{ip}: [{model}, {username}, {password}]]: 进入特权模式失败...')
                    # 进入特权模式失败则尝试下一组用户名/密码
                    continue

                # 获取设备管理IP
                tn.write(b'display ip interface brief\n')
                time.sleep(1)
                cmd_result = tn.read_very_eager().decode('ascii')
                if re.search(r'<cr>', cmd_result, re.M):
                    tn.write(b'\n')
                    time.sleep(1)
                cmd_result = tn.read_very_eager().decode('ascii')
                logging.warning(cmd_result)
                vlan_ip = {}
                for line in cmd_result.split('\n'):
                    if re.search(r'vlanif\d+', line, re.I):
                        (vlan, mgmt_ip) = re.search(
                            r'vlanif(\d+)\s+(\d+.\d+.\d+.\d+)', line, re.I).groups()
                        vlan_ip.setdefault(int(vlan), mgmt_ip)

                # 按VLAN从小到大排序, 取最小VLAN的值
                mgmt_ip = sorted(vlan_ip.items())[0][1]

                # 执行采集命令
                tn.write(b'display current-configuration section esl\n')
                tn.write(b'\n')
                time.sleep(3)
                cmd_result = tn.read_very_eager().decode('ascii')
                while cmd_result.endswith("Press 'Q' to break ) ----"):
                    tn.write(b' \n')
                    time.sleep(1)
                    cmd_result += tn.read_very_eager().decode('ascii')
                logging.warning(cmd_result)

                # 号码列表
                phone_list = []
                for line in cmd_result.split('\n'):
                    if re.search(r'sippstnuser\s+add.*telno\s+(\S+)', line):
                        phone_list.append(
                            re.search(r'sippstnuser\s+add.*telno\s+(\S+)', line).group(1))

                logging.warning(f'当前业务号码: --->>>{phone_list}')

                # 写文件
                with open(r'/home/brokensmile/telephone/data/' + f'{no}.csv', 'a') as f:
                    if len(phone_list) > 0:
                        for phonenum in phone_list:
                            f.write(f'{ip}:{mgmt_ip},{model},{phonenum}\n')

                # 退出登录
                tn.write(b'quit\n')
                tn.write(b'Y\n')
                logging.warning(f'[{ip}]: 退出成功...')

                # 采集成功则退出用户名/密码循环
                break

        elif re.search(r'##', DeviceType):
            # 中兴

            model = 'null'
            # 截取设备型号
            if re.search(r'ZTE\s+\S+\s+', DeviceType, re.M | re.I):
                model = re.search(r'ZTE\s+(\S+)\s+', DeviceType,
                                  re.M | re.I).group(1)

            # 密码字典
            zt_dict = {'xxxx': 'xxxx',
                       'xxxx': 'xxxx',
                       'xxxx': 'xxxx'}

            # 执行回车, 获取登录用户名提示符
            tn.write(b'\r\n')
            time.sleep(1)

            for password, username in zt_dict.items():
                # 匹配登录用户名提示符
                tn.read_until(b'Login:', timeout=10)
                tn.write(username.encode('ascii') + b'\r\n')
                time.sleep(1)

                # 匹配登录密码提示符
                tn.read_until(b'Password:', timeout=10)
                tn.write(password.encode('ascii') + b'\r\n')
                time.sleep(3)

                # 获取登录结果
                cmd_result = tn.read_very_eager().decode('ascii')
                logging.warning(cmd_result)

                # 判断是否成功登录
                if re.search(r'>\s*$', cmd_result):
                    logging.warning(
                        f'①[{ip}: [{model}, {username}, {password}]]: 登录成功...')
                else:
                    logging.warning(
                        f'①[{ip}: [{model}, {username}, {password}]]: 登录失败, 尝试其他用户名/密码...')
                    # 登录失败则尝试下一组用户名/密码
                    continue

                # 输入enable密码
                tn.write(b'enable\r\n')
                tn.read_until(b'Please input password:', timeout=10)
                tn.write(password.encode('ascii') + b'\r\n')
                time.sleep(3)

                # 获取enable结果
                cmd_result = tn.read_very_eager().decode('ascii')
                logging.warning(cmd_result)

                # 判断是否成功进入特权模式
                if re.search(r'#\s*$', cmd_result):
                    logging.warning(
                        f'②[{ip}: [{model}, {username}, {password}]]: 进入特权模式成功...')
                else:
                    logging.warning(
                        f'②[{ip}: [{model}, {username}, {password}]]: 进入特权模式失败, 尝试其他用户名/密码...')
                    # 进入特权模式失败则尝试下一组用户名/密码
                    continue

                # 获取板卡号并存至列表
                tn.write(b'show card\r\n')
                time.sleep(1)
                cmd_result = tn.read_very_eager().decode('ascii')
                logging.warning(cmd_result)
                card_list = []
                for line in cmd_result.split('\r\n'):
                    if re.search(r'^\s+(\d)', line):
                        card_list.append(re.search(r'^\s*(\d)', line).group(1))

                # 执行采集命令
                if re.search(r'98', model):

                    # 获取设备管理IP
                    tn.write(b'show ip subnet\r\n')
                    time.sleep(1)
                    cmd_result = tn.read_very_eager().decode('ascii')
                    logging.warning(cmd_result)
                    vlan_ip = {}
                    for line in cmd_result.split('\r\n'):
                        if re.search(r'\d+.\d+.\d+.\d+\s+\d+.\d+.\d+.\d+\s+\d+', line):
                            (mgmt_ip, vlan) = re.search(
                                r'(\d+.\d+.\d+.\d+)\s+\d+.\d+.\d+.\d+\s+(\d+)', line).groups()
                            vlan_ip.setdefault(int(vlan), mgmt_ip)

                    # 按VLAN从小到大排序, 取最小VLAN的值
                    mgmt_ip = sorted(vlan_ip.items())[0][1]

                    # 号码列表
                    phone_list = []

                    # 遍历板卡
                    tn.write(b'voice\r\n')
                    time.sleep(1)
                    for card in card_list[:-1]:
                        tn.write(
                            b'show voice sipuser pstnuser slot %d\r\n' % int(card))
                        time.sleep(1)
                        cmd_result = tn.read_very_eager().decode('ascii')
                        while cmd_result.endswith('(Q to quit)'):
                            tn.write(b'\r\n')
                            time.sleep(1)
                            cmd_result += tn.read_very_eager().decode('ascii')
                        logging.warning(cmd_result)
                        for line in cmd_result.split('\r\n'):
                            if re.search(r'sipdigit:\s+(\S+)', line):
                                phone_list.append(
                                    re.search(r'sipdigit:\s+(\S+)', line).group(1))

                    logging.warning(f'当前设备业务号码: --->>>{phone_list}')
                    tn.write(b'quit\r\n')

                    # 写文件
                    with open(r'/home/brokensmile/telephone/data/' + f'{no}.csv', 'a') as f:
                        if len(phone_list) > 0:
                            for phonenum in phone_list:
                                f.write(f'{ip}:{mgmt_ip},{model},{phonenum}\n')
                else:

                    # 获取设备管理IP
                    tn.write(b'show ip inband-vlan\r\n')
                    time.sleep(1)
                    cmd_result = tn.read_very_eager().decode('ascii')
                    logging.warning(cmd_result)
                    vlan_ip = {}
                    for line in cmd_result.split('\r\n'):
                        if re.search(r'\d+.\d+.\d+.\d+\s+\d+.\d+.\d+.\d+\s+\d+', line):
                            (mgmt_ip, vlan) = re.search(
                                r'(\d+.\d+.\d+.\d+)\s+\d+.\d+.\d+.\d+\s+(\d+)', line).groups()
                            vlan_ip.setdefault(int(vlan), mgmt_ip)

                    # 按VLAN从小到大排序, 取最小VLAN的值
                    mgmt_ip = sorted(vlan_ip.items())[0][1]

                    # 号码列表
                    phone_list = []

                    # 遍历板卡
                    tn.write(b'ag\r\n')
                    time.sleep(0.5)
                    for card in card_list[:-1]:
                        tn.write(b'get-sipuser slot %d\r\n' % int(card))
                        time.sleep(0.5)
                        cmd_result = tn.read_very_eager().decode('ascii')
                        while cmd_result.endswith('(Q to quit)'):
                            tn.write(b'\r\n')
                            time.sleep(1)
                            cmd_result += tn.read_very_eager().decode('ascii')
                        logging.warning(cmd_result)
                        for line in cmd_result.split('\r\n'):
                            if re.search(r'sipdigit:\s+(\S+)', line):
                                phone_list.append(
                                    re.search(r'sipdigit:\s+(\S+)', line).group(1))

                    logging.warning(f'当前业务号码: --->>>{phone_list}')
                    tn.write(b'quit\r\n')

                    # 写文件
                    with open(r'/home/brokensmile/telephone/data/' + f'{no}.csv', 'a') as f:
                        if len(phone_list) > 0:
                            for phonenum in phone_list:
                                f.write(f'{ip}:{mgmt_ip},{model},{phonenum}\n')

                # 退出登录
                tn.write(b'quit\r\n')
                tn.write(b'Y\r\n')
                logging.warning(f'[{ip}]: 退出成功...')

                # 采集成功则退出用户名/密码循环
                break

        elif re.search(r'Username:', DeviceType):
            # 瑞斯康达

            username = 'xxxx'
            password = 'xxxx'

            # 输入用户名
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

            # 号码列表
            phone_list = []
            for line in cmd_result.split('\r\n'):
                if re.search(r'sip pots authentication.*tj.ctcims.cn', line, re.I):
                    phone_list.append(re.search(
                        r'sip pots authentication (\S+)\@tj.ctcims.cn potsId \d+', line, re.I).group(1))

            logging.warning(f'当前设备业务号码: --->>>{phone_list}\n')

            # 写文件
            with open(r'/home/brokensmile/telephone/data/' + f'{no}.csv', 'a') as f:
                if len(phone_list) > 0:
                    for phonenum in phone_list:
                        f.write(f'{ip}:{ip},A8-C,{phonenum}\n')

            # 退出登录
            tn.write(b'quit\r\n')
            logging.warning(f'[{ip}]: 退出成功...')

        elif re.search(r'F\d{3}', DeviceType):
            # 中兴FTTH

            model = 'null'
            # 截取设备型号
            if re.search(r'F\d{3}', DeviceType, re.M | re.I):
                model = re.search(r'(F\d{3})', DeviceType).group(1)

            # 密码字典
            zt_dict = {'root': 'root',
                       'Zte521': 'root'}

            for password, username in zt_dict.items():
                # 输入用户名
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
                        f'①[{ip}: [{model}, {username}, {password}]]: 登录失败, 尝试其他用户名/密码...')
                    continue

                # 执行采集命令
                logging.warning(f'[{ip}]: 开始执行采集...')
                tn.write(b'sendcmd 1 DB p VoIPSIPLine\n')
                time.sleep(1)
                cmd_result = tn.read_very_eager().decode('ascii')

                # 号码列表
                phone_list = []
                for line in cmd_result.split('\r\n'):
                    if re.search(r'name="AuthUserName" val="\S+?"', line, re.I):
                        phone_list.append(re.search(
                            r'name="AuthUserName" val="(.*)"', line, re.I).group(1))

                logging.warning(f'当前设备业务号码: --->>>{phone_list}\n')

                # 写文件
                with open(r'/home/brokensmile/telephone/data/' + f'{no}.csv', 'a') as f:
                    if len(phone_list) > 0:
                        for phonenum in phone_list:
                            f.write(f'{ip}:{ip},{model},{phonenum}\n')

                # 退出登录
                tn.write(b'exit\r\n')
                logging.warning(f'[{ip}]: 退出成功...')

                # 采集成功则退出用户名/密码循环
                break

        else:
            # 去掉回车及换行
            DeviceType = DeviceType.replace('\r', '').replace('\n', '')
            logging.warning(f"[{ip}: {DeviceType}]: 其他类型设备...")

    except ConnectionResetError:
        logging.warning(f'[{ip}]: Telnet连接被重置...\n')
    except:
        logging.warning(f'[{ip}]: 建立Telnet连接失败...\n')
    finally:
        tn.close()
    n += 1
    logging.warning(f'当前分组已处理设备数/总设备数: {n}/{len(rows)}...')
