#!/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import logging
import cx_Oracle
from telnetlib import Telnet

username = 'xxx'
password = 'xxx'
enable = 'xxx'

with cx_Oracle.connect('xxx', 'xxx', 'x.x.x.x:x/dbnms', encoding='UTF-8') as conn:
    cur = conn.cursor()
    sql = f"""SELECT A.DEVICEMODELCODE, A.LOOPADDRESS, A.DETAILMODELCODE
                FROM DEVICE A
               WHERE A.CHANGETYPE = '0'
                 AND A.LOOPADDRESS IS NOT NULL
                 AND A.DEVICETYPECODE IN ('DEV_IP_X', 'DEV_IP_Y')
                 AND A.TELNETSTATUS = '1'
            """
    cur.execute(sql)
    rows = cur.fetchall()


class TelnetClient():
    def __init__(self):
        self.tn = Telnet()
        self.tn.set_debuglevel(1)

    def deal_ZT(self, ip, model, username, password, enablepassword):
        try:
            self.tn.open(ip, timeout=10)
            # 获取登陆提示符
            self.tn.read_until(b'#', timeout=10)
            self.tn.write(b'\r\n')
            time.sleep(1)

            # 匹配登录用户名提示符
            self.tn.read_until(b'Login:', timeout=10)
            self.tn.write(username.encode('ascii') + b'\r\n')
            time.sleep(1)

            # 匹配登录密码提示符
            self.tn.read_until(b'Password:', timeout=10)
            self.tn.write(password.encode('ascii') + b'\r\n')
            time.sleep(3)

            # 获取登录结果
            cmd_result = self.tn.read_very_eager().decode('ascii')
            logging.warning(cmd_result)

            # 判断是否成功登录
            if re.search(r'>\s*$', cmd_result):
                logging.warning(f'[{ip}]: 登录成功...')
            else:
                logging.warning(f'[{ip}]: 登录失败...')
                return False

            # 输入enable密码
            self.tn.write(b'enable\r\n')
            self.tn.read_until(b'Please input password:', timeout=10)
            self.tn.write(enablepassword.encode('ascii') + b'\r\n')
            time.sleep(3)

            # 获取enable结果
            cmd_result = self.tn.read_very_eager().decode('ascii')
            logging.warning(cmd_result)

            # 判断是否成功进入特权模式
            if re.search(r'#\s*$', cmd_result):
                logging.warning(f'[{ip}]: 进入特权模式成功...')
            else:
                logging.warning(f'[{ip}]: 进入特权模式失败...')
                return False

            # 执行采集命令
            self.tn.write(b'show running-config module vlan\r\n')
            time.sleep(3)
            cmd_result = self.tn.read_very_eager().decode('ascii')
            while cmd_result.endswith('(Q to quit)'):
                self.tn.write(b'\r\n')
                time.sleep(1)
                cmd_result += self.tn.read_very_eager().decode('ascii')
            cmd_result = re.sub(
                r'Press any key to continue \(Q to quit\)\\x00', '', cmd_result)
            logging.warning(cmd_result)

            # 分析结果
            vlan_dict = {}
            if re.search(r'98', model):
                for line in cmd_result.split('\r\n'):
                    if re.search(r'vlan.*tag', line, re.I):
                        vlan, slot, ports, tagging = re.search(
                            r'vlan\s+(\d+)\s+(\d)/(\S+)\s+(.*tag)', line, re.I).groups()
                        port_list = []
                        for port in ports.split(','):
                            if re.search(r'-', port):
                                begin, end = re.search(
                                    r'(\d+)-(\d+)', port).groups()
                                all_port = [i for i in range(
                                    int(begin), int(end)+1)]
                                for tmp_port in all_port:
                                    port_list.append(
                                        slot + '/' + str(tmp_port))
                            else:
                                port_list.append(slot + '/' + port)
                        vlan_dict.setdefault(
                            vlan, {}).setdefault(tagging, port_list)
            else:
                vlan_dict = {}
                for line in cmd_result.split('\r\n'):
                    if re.search(r'configure vlan \d+', line, re.I):
                        vlan = re.search(
                            r'configure vlan (\d+)', line, re.I).group(1)
                    if re.search(r'addport.*tag', line, re.I):
                        slot, ports, tagging = re.search(
                            r'addport\s+(\S+)/(\S+)\s+(.*tag)', line, re.I).groups()
                        port_list = []
                        for port in ports.split(','):
                            if re.search(r'-', port):
                                begin, end = re.search(
                                    r'(\d+)-(\d+)', port).groups()
                                all_port = [i for i in range(
                                    int(begin), int(end)+1)]
                                for tmp_port in all_port:
                                    port_list.append(
                                        slot + '/' + str(tmp_port))
                            else:
                                port_list.append(slot + '/' + port)
                        vlan_dict.setdefault(
                            vlan, {}).setdefault(tagging, port_list)
            print(vlan_dict)

            # 写文件
            with open(r'/root/tengkf/phonenum/portvlan.csv', 'a') as f:
                for ko, vo in vlan_dict.items():
                    for ki, vi in vo.items():
                        for port in vi:
                            f.write(f'{ip},{model},{ko},{ki},{port}\n')

            # 退出登录
            self.tn.write(b'quit\r\n')
            self.tn.write(b'Y\r\n')
            logging.warning(f'[{ip}]: 退出成功...')
        except ConnectionResetError:
            logging.warning(f'[{ip}]: Telnet连接被重置...\n')
        except:
            logging.warning(f'[{ip}]: 采集异常...\n')
        finally:
            self.tn.close()

    def deal_HU(self, ip, model, username, password, enablepassword):
        try:
            self.tn.open(ip, timeout=10)
            # 匹配登录用户名提示符
            time.sleep(1)
            self.tn.read_until(b'>>User name:', timeout=10)
            self.tn.write(username.encode('ascii') + b'\n')
            time.sleep(1)

            # 匹配登录密码提示符
            self.tn.read_until(b'>>User password:', timeout=10)
            self.tn.write(password.encode('ascii') + b'\n')
            time.sleep(3)

            # 首次获取登录结果
            cmd_result = self.tn.read_very_eager().decode('ascii')

            # 设备首次登陆提醒处理
            if re.search(r"Press\s+'Q'\s+to\s+break", cmd_result, re.M):
                self.tn.write(b'Q')
                time.sleep(1)
                cmd_result = self.tn.read_very_eager().decode('ascii')
            elif re.search(r"Are you sure to modify system time", cmd_result, re.M):
                self.tn.write(b'n')
                time.sleep(1)
                cmd_result = self.tn.read_very_eager().decode('ascii')

            # 判断是否成功登录
            if re.search(r'>\s*$', cmd_result):
                logging.warning(f'[{ip}]: 登录成功...')
            else:
                logging.warning(f'[{ip}]: 登录失败...')
                return False

            # 执行enable
            self.tn.write(b'enable\n')

            # 获取enable结果
            time.sleep(3)
            cmd_result = self.tn.read_very_eager().decode('ascii')
            logging.warning(cmd_result)

            # 判断是否成功进入特权模式
            if re.search(r'#\s*$', cmd_result):
                logging.warning(f'[{ip}]: 进入特权模式成功...')
            else:
                logging.warning(f'[{ip}]: 进入特权模式失败...')
                return False

            # 执行采集命令
            self.tn.write(b'display service-port all\n')
            self.tn.write(b'\n')
            time.sleep(3)
            cmd_result = self.tn.read_very_eager().decode('ascii')
            while cmd_result.endswith("Press 'Q' to break ) ----"):
                self.tn.write(b' \n')
                time.sleep(1)
                cmd_result += self.tn.read_very_eager().decode('ascii')
            cmd_result = re.sub(
                r'---- More \( Press \'Q\' to break \) ----', '', cmd_result)
            cmd_result = re.sub(r'\\x1b\[37D', '', cmd_result)
            logging.warning(cmd_result)

            # 分析结果
            vlan_dict = {}
            for line in cmd_result.split('\r\n'):
                if re.search(r'\d+.*vlan', line, re.I):
                    vlan, slot, port, tagging = re.search(
                        r'(\d+)\s+[a-zA-Z]+\s+[a-zA-Z]+\s+(\S+)\s+(\S+).*vlan\s+(\S+)', line, re.I).groups()
                    vlan_dict.setdefault(
                        vlan, {}).setdefault(tagging, []).append(slot + port)
            print(vlan_dict)

            # 写文件
            with open(r'/root/tengkf/phonenum/portvlan.csv', 'a') as f:
                for ko, vo in vlan_dict.items():
                    for ki, vi in vo.items():
                        for port in vi:
                            f.write(f'{ip},{model},{ko},{ki},{port}\n')

            # 退出登录
            self.tn.write(b'quit\n')
            self.tn.write(b'Y\n')
            logging.warning(f'[{ip}]: 退出成功...')
        except ConnectionResetError:
            logging.warning(f'[{ip}]: Telnet连接被重置...\n')
        except:
            logging.warning(f'[{ip}]: 采集异常...\n')
        finally:
            self.tn.close()


for row in rows:
    Telnet_Client = TelnetClient()
    if re.search(r'ZT', row[0]):
        Telnet_Client.deal_ZT(row[1], row[2], username, password, enable)
    else:
        Telnet_Client.deal_HU(row[1], row[2], username, password, enable)
