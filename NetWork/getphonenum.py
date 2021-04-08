#!/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys
import time
from telnetlib import Telnet

import cx_Oracle

username = 'xxxx'
password = 'xxxx'
enable = 'xxxx'
node = sys.argv[1]

with cx_Oracle.connect('xxxx', 'xxxx', 'x.x.x.x:1521/dbnms', encoding='UTF-8') as conn:
    cur = conn.cursor()
    sql = f"""SELECT A.DEVICEMODELCODE, A.LOOPADDRESS, A.DETAILMODELCODE
                FROM DEVICE A
               WHERE A.CHANGETYPE = '0'
                 AND A.NODECODE = :node
                 AND A.LOOPADDRESS IS NOT NULL
                 AND A.DEVICETYPECODE IN ('DEV_IP_X', 'DEV_IP_Y')
                 AND A.TELNETSTATUS = '1'
            """
    cur.execute(sql, [node])
    rows = cur.fetchall()


class TelnetClient():
    def __init__(self):
        self.tn = Telnet()
        self.tn.set_debuglevel(0)

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

            # 获取板卡号并存至列表
            self.tn.write(b'show card\r\n')
            time.sleep(0.5)
            cmd_result = self.tn.read_very_eager().decode('ascii')
            card_list = []
            for line in cmd_result.split('\r\n'):
                if re.search(r'^\s+(\d)', line):
                    card_list.append(re.search(r'^\s*(\d)', line).group(1))

            # 号码字典
            phone_dict = {}
            # 执行采集命令
            if re.search(r'98', model):

                # 遍历板卡
                self.tn.write(b'voice\r\n')
                time.sleep(0.5)
                for card in card_list[:-1]:
                    self.tn.write(
                        b'show voice sipuser pstnuser slot %d\r\n' % int(card))
                    time.sleep(0.5)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    while cmd_result.endswith('(Q to quit)'):
                        self.tn.write(b'\r\n')
                        time.sleep(1)
                        cmd_result += self.tn.read_very_eager().decode('ascii')
                    cmd_result = re.sub(
                        r'Press any key to continue \(Q to quit\)\\x00', '', cmd_result)
                    logging.warning(cmd_result)
                    for line in cmd_result.split('\r\n'):
                        if re.search(r'slot:\s+\d+', line):
                            slot = re.search(r'slot:\s+(\d+)',
                                             line, re.I).group(1)
                        if re.search(r'index:\s+\d+', line):
                            port = re.search(
                                r'index:\s+(\d+)', line, re.I).group(1)
                        if re.search(r'sipdigit:\s+\S+', line):
                            no = re.search(r'sipdigit:\s+(\S+)',
                                           line, re.I).group(1)
                            phone_dict.setdefault(slot + '/' + port, no)

                logging.warning(f'当前业务号码: --->>>{phone_dict}')
                self.tn.write(b'quit\r\n')

                # 写文件
                with open(r'/root/tengkf/phonenum/' + f'{node}.csv', 'a') as f:
                    if len(phone_dict) > 0:
                        for k, v in phone_dict.items():
                            f.write(f'{ip},{model},{k},{v}\n')
            else:

                # 遍历板卡
                self.tn.write(b'ag\r\n')
                time.sleep(0.5)
                for card in card_list[:-1]:
                    self.tn.write(b'get-sipuser slot %d\r\n' % int(card))
                    time.sleep(0.5)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    while cmd_result.endswith('(Q to quit)'):
                        self.tn.write(b'\r\n')
                        time.sleep(1)
                        cmd_result += self.tn.read_very_eager().decode('ascii')
                    cmd_result = re.sub(
                        r'Press any key to continue \(Q to quit\)\\x00', '', cmd_result)
                    logging.warning(cmd_result)
                    for line in cmd_result.split('\r\n'):
                        if re.search(r'index:\s+\d+', line):
                            port = re.search(
                                r'index:\s+(\d+)', line, re.I).group(1)
                        if re.search(r'sipdigit:\s+\S+', line):
                            no = re.search(r'sipdigit:\s+(\S+)', line).group(1)
                            phone_dict.setdefault(card + '/' + port, no)

                logging.warning(f'当前业务号码: --->>>{phone_dict}')
                self.tn.write(b'quit\r\n')

                # 写文件
                with open(r'/root/tengkf/phonenum/' + f'{node}.csv', 'a') as f:
                    if len(phone_dict) > 0:
                        for k, v in phone_dict.items():
                            f.write(f'{ip},{model},{k},{v}\n')

            # 退出登录
            self.tn.write(b'quit\r\n')
            self.tn.write(b'Y\r\n')
            logging.warning(f'[{ip}]: 退出成功...')
        except ConnectionResetError:
            logging.warning(f'[{ip}]: Telnet连接被重置...\n')
        except:
            logging.warning(f'[{ip}]: 建立Telnet连接失败...\n')
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
            self.tn.write(b'display current-configuration section esl\n')
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

            # 号码字典
            phone_dict = {}
            for line in cmd_result.split('\n'):
                if re.search(r'sippstnuser\s+add.*telno\s+(\S+)', line):
                    port, no = re.search(
                        r'sippstnuser\s+add\s+(\S+).*telno\s+(\S+)', line).groups()
                    phone_dict.setdefault(port, no)

            logging.warning(f'当前业务号码: --->>>{phone_dict}')

            # 写文件
            with open(r'/root/tengkf/phonenum/' + f'{node}.csv', 'a') as f:
                if len(phone_dict) > 0:
                    for k, v in phone_dict.items():
                        f.write(f'{ip},{model},{k},{v}\n')

            # 退出登录
            self.tn.write(b'quit\n')
            self.tn.write(b'Y\n')
            logging.warning(f'[{ip}]: 退出成功...')
        except ConnectionResetError:
            logging.warning(f'[{ip}]: Telnet连接被重置...\n')
        except:
            logging.warning(f'[{ip}]: 建立Telnet连接失败...\n')
        finally:
            self.tn.close()


for row in rows:
    Telnet_Client = TelnetClient()
    if re.search(r'ZT', row[0]):
        Telnet_Client.deal_ZT(row[1], row[2], username, password, enable)
    else:
        Telnet_Client.deal_HU(row[1], row[2], username, password, enable)
