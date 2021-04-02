#!/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import sys
import time
from telnetlib import Telnet

import cx_Oracle

# 将用户名密码保存到字典里
src_dict = {}
with open(r'/root/tengkf/F832/password.txt', 'r') as f:
    for line in f:
        userid, userpasswd = line.split()
        src_dict.setdefault(userid, userpasswd)

username = 'xxxx'
password = 'xxxx'
enable = 'xxxx'

node = sys.argv[1]

with cx_Oracle.connect('xxxx', 'xxxx', 'x.x.x.x:x/dbnms', encoding='UTF-8') as conn:
    cur = conn.cursor()
    sql = f"""SELECT A.DEVICEMODELCODE, A.LOOPADDRESS, A.DETAILMODELCODE
               FROM DEVICE_TMP A
              WHERE A.CHANGETYPE = '0'
                AND A.NODECODE = :node
                AND A.LOOPADDRESS IS NOT NULL
                AND A.DEVICETYPECODE IN ('DEV_IP_X', 'DEV_IP_Y')
                AND A.TELNETSTATUS = '1'
                AND A.LOOPADDRESS IN (SELECT IP FROM MDUIP_HU WHERE DAY = '2020121801')
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
            time.sleep(3)
            cmd_result = self.tn.read_very_eager().decode('ascii')
            card_list = []
            for line in cmd_result.split('\r\n'):
                if re.search(r'^\s+(\d)', line):
                    card_list.append(re.search(r'^\s*(\d)', line).group(1))

            # 执行采集命令
            if re.search(r'98', model):

                # 号码对应接口字典
                phone_dict = {}

                # 遍历板卡
                self.tn.write(b'voice\r\n')
                time.sleep(1)
                for card in card_list[:-1]:
                    phone_dict.setdefault(card, {})
                    self.tn.write(
                        b'show voice sipuser pstnuser slot %d\r\n' % int(card))
                    time.sleep(1)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    while cmd_result.endswith('(Q to quit)'):
                        self.tn.write(b'\r\n')
                        time.sleep(1)
                        cmd_result += self.tn.read_very_eager().decode('ascii')
                    #cmd_result = re.sub(r'Press.*[\x00-\x1f]', '', cmd_result)
                    logging.warning(cmd_result)
                    for line in cmd_result.split('\r\n'):
                        if re.search(r'index:\s+(\d+)', line):
                            index = re.search(r'index:\s+(\d+)', line).group(1)
                            phone_dict[card].setdefault(index, '')
                        if re.search(r'sipdigit:\s+(\S+)', line):
                            phone_dict[card][index] = re.search(
                                r'sipdigit:\s+(\S+)', line).group(1)

                logging.warning(f'当前业务号码: --->>>{phone_dict}\r\n')

                cmd_result = ''
                # 遍历字典
                for ko, vo in phone_dict.items():
                    if len(vo) > 0:
                        for ki, vi in vo.items():
                            if vi in src_dict:
                                self.tn.write(b'sipuser user-authentication modify slot ' + ko.encode('ascii') + b' beginindex ' + ki.encode('ascii') + b' num 1 authusername ' +
                                              vi[:-1].encode('ascii') + b' password ' + src_dict[vi].encode('ascii') + b' type 2 beginno ' + vi[-1].encode('ascii') + b'\r\n')
                                time.sleep(1)
                                cmd_result += self.tn.read_very_eager().decode('ascii')
                                # 写文件
                                with open(r'/root/tengkf/F832/' + f'{node}.csv', 'a') as f:
                                    f.write(f'{ip},{model},{vi}\n')

                        logging.warning(cmd_result)

                # 重新注册
                self.tn.write(b'sipuser unregister all\r\n')
                time.sleep(1)
                self.tn.write(b'\r\n')
                time.sleep(1)
                self.tn.write(b'sipuser register all\r\n')
                time.sleep(1)
                self.tn.write(b'\r\n')
                time.sleep(1)

                # 退出遍历板卡
                self.tn.write(b'exit\r\n')

                # 保存配置
                self.tn.write(b'save\r\n')
                time.sleep(0.5)

            else:

                # 判断F822是否为旧版本
                old_version = 0
                self.tn.write(b'show version\r\n')
                time.sleep(1)
                cmd_result = self.tn.read_very_eager().decode('ascii')
                while cmd_result.endswith('(Q to quit)'):
                    self.tn.write(b'\r\n')
                    time.sleep(1)
                    cmd_result += self.tn.read_very_eager().decode('ascii')
                cmd_result = re.sub(r'Press.*[\x00-\x1f]', '', cmd_result)
                logging.warning(cmd_result)
                if re.search(r'V1\.[12]\.0', cmd_result, re.M | re.I):
                    old_version = 1

                # 获取VLAN号
                vlan = ''
                self.tn.write(b'show ip inband-vlan\r\n')
                time.sleep(1)
                cmd_result = self.tn.read_very_eager().decode('ascii')
                cmd_result = re.sub(r'Press.*[\x00-\x1f]', '', cmd_result)
                logging.warning(cmd_result)
                for line in cmd_result.split('\r\n'):
                    if re.search(r'(\d+).*voip', line, re.I):
                        vlan = re.search(r'(\d+)\s+(\S+)\s+voip',
                                         line, re.I).group(1)

                # 号码对应接口字典
                phone_dict = {}

                # 遍历板卡
                self.tn.write(b'ag\r\n')
                time.sleep(1)
                for card in card_list[:-1]:
                    phone_dict.setdefault(card, {})
                    self.tn.write(b'get-sipuser slot %d\r\n' % int(card))
                    time.sleep(1)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    while cmd_result.endswith('(Q to quit)'):
                        self.tn.write(b'\r\n')
                        time.sleep(1)
                        cmd_result += self.tn.read_very_eager().decode('ascii')
                    #cmd_result = re.sub(r'Press.*[\x00-\x1f]', '', cmd_result)
                    logging.warning(cmd_result)
                    for line in cmd_result.split('\r\n'):
                        if re.search(r'index:\s+(\d+)', line):
                            index = re.search(r'index:\s+(\d+)', line).group(1)
                            phone_dict[card].setdefault(index, '')
                        if re.search(r'sipdigit:\s+(\S+)', line):
                            phone_dict[card][index] = re.search(
                                r'sipdigit:\s+(\S+)', line).group(1)

                logging.warning(f'当前业务号码: --->>>{phone_dict}\r\n')

                cmd_result = ''
                # 遍历字典
                for ko, vo in phone_dict.items():
                    if len(vo) > 0:
                        for ki, vi in vo.items():
                            if vi in src_dict:
                                self.tn.write(b'mod-sipuser beginslot ' + ko.encode('ascii') + b' beginindex ' + ki.encode(
                                    'ascii') + b' num 1 password ' + src_dict[vi].encode('ascii') + b'\r\n')
                                time.sleep(1)
                                cmd_result += self.tn.read_very_eager().decode('ascii')
                                # 写文件
                                with open(r'/root/tengkf/F832/' + f'{node}.csv', 'a') as f:
                                    f.write(f'{ip},{model},{vi}\n')

                        logging.warning(cmd_result)

                # 退出遍历板卡
                self.tn.write(b'exit\r\n')

                if vlan != '':
                    # 进入配置模式
                    self.tn.write(b'configure\r\n')
                    time.sleep(1)

                    # 重新注册
                    self.tn.write(b'ip dhcp-client disable\r\n')
                    time.sleep(1)
                    self.tn.write(b'ip dhcp-client disable\r\n')
                    time.sleep(3)
                    if re.search(r'822', model) and old_version == 1:
                        self.tn.write(b'ip dhcp-client enable\r\n')
                        time.sleep(1)
                    else:
                        self.tn.write(b'ip dhcp-client enable vlan ' +
                                      vlan.encode('ascii') + b'\r\n')
                        time.sleep(1)

                    # 退出配置模式
                    self.tn.write(b'exit\r\n')
                    time.sleep(1)

                # 保存配置
                self.tn.write(b'write\r\n')
                time.sleep(1)

            # 退出登录
            self.tn.write(b'quit\r\n')
            time.sleep(1)
            self.tn.write(b'y\r\n')
            cmd_result = self.tn.read_very_eager().decode('ascii')
            cmd_result = re.sub(r'--.*[\x00-\x1f]', '', cmd_result)
            logging.warning(cmd_result)
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
            #cmd_result = re.sub(r'--.*[\x00-\x1f]', '', cmd_result)
            logging.warning(cmd_result)

            # 号码对应接口字典
            phone_dict = {}
            for line in cmd_result.split('\n'):
                if re.search(r'sippstnuser\s+add.*telno', line):
                    (port, userid) = re.search(
                        r'sippstnuser\s+add\s+(\S+).*telno\s+(\S+)', line).groups()
                    phone_dict.setdefault(userid, port)

            logging.warning(f'当前业务号码: --->>>{phone_dict}\n')

            # 进入配置模式
            self.tn.write(b'config\n')
            time.sleep(1)
            # 进入语音配置
            self.tn.write(b'esl user\n')
            time.sleep(1)

            cmd_result = self.tn.read_very_eager().decode('ascii')
            logging.warning(cmd_result)
            # 遍历号码对应接口字典, 判断号码是否在密码字典中存在, 存在的话下发改密码配置
            for k, v in phone_dict.items():
                cmd_result = ''
                if k in src_dict:
                    self.tn.write(b'sippstnuser auth set ' + v.encode('ascii') +
                                  b' telno ' + k.encode('ascii') + b'\n')
                    time.sleep(1)
                    cmd_result += self.tn.read_very_eager().decode('ascii')
                    if re.search(r'<cr>', cmd_result, re.I | re.M):
                        self.tn.write(b'\n')
                        time.sleep(1)
                    cmd_result += self.tn.read_very_eager().decode('ascii')
                    self.tn.write(('+' + k).encode('ascii') + b'\n')
                    time.sleep(1)
                    cmd_result += self.tn.read_very_eager().decode('ascii')
                    self.tn.write(src_dict[k].encode('ascii') + b'\n')
                    time.sleep(1)
                    cmd_result += self.tn.read_very_eager().decode('ascii')

                    # 写文件
                    with open(r'/root/tengkf/F832/' + f'{node}.csv', 'a') as f:
                        f.write(f'{ip},{model},{k}\n')

                logging.warning(cmd_result)

            # 退出语音配置
            self.tn.write(b'quit\n')
            time.sleep(1)

            # 复位SIP接口
            self.tn.write(b'interface sip 0\n')
            time.sleep(1)
            self.tn.write(b'reset\n')
            time.sleep(1)
            self.tn.write(b'y\n')
            time.sleep(1)
            self.tn.write(b'quit\n')
            time.sleep(1)

            # 退出配置模式
            self.tn.write(b'quit\n')
            time.sleep(1)

            # 保存配置
            self.tn.write(b'save configuration\n')
            time.sleep(1)

            # 退出登录
            self.tn.write(b'quit\n')
            time.sleep(0.5)
            self.tn.write(b'y\n')
            cmd_result = self.tn.read_very_eager().decode('ascii')
            cmd_result = re.sub(r'--.*[\x00-\x1f]', '', cmd_result)
            logging.warning(cmd_result)
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
