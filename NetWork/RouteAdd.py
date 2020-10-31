#!/bin/env python3
# -*- coding: utf-8 -*-

# Author: brokensmile@yeah.net
# Make configurations to the disconnected FTTB devices through OLT.

import logging
import re
import time
from telnetlib import Telnet

# 设备字典 Key: OltIp, Value: FttbIp
ConfigDev = {}
with open('devices.txt', 'r') as f:
    for line in f.readlines():
        IpList = line.split()
        if len(IpList) == 2 and (IpList[0] != IpList[1]):
            ConfigDev.setdefault(IpList[0], []).append(IpList[1])

# 遍历字典登录OLT设备查询默认网关, 对FTTB设备做Ping测试, 能Ping通则登录设备下发相关配置
(OltUserName, OltPassWord, FttbUserName, FttbPassWord) = (
    'xxxx', 'xxxx', 'xxxx', 'xxxx')


class TelnetClient():
    def __init__(self):
        self.tn = Telnet()

    # 登陆设备
    def login_dev(self, Ip, UserName, PassWord):
        try:
            self.tn.open(Ip)
        except:
            logging.warning('[%s]: 网络不通!' % Ip)
            return False

        # 匹配登录用户名提示符
        self.tn.read_until(b'>>User name:', timeout=10)
        self.tn.write(UserName.encode('ascii') + b'\n')

        # 匹配登录密码提示符
        self.tn.read_until(b'>>User password:', timeout=10)
        self.tn.write(PassWord.encode('ascii') + b'\n')

        # 获取登录结果
        time.sleep(2)
        cmd_result = self.tn.read_very_eager().decode('ascii')
        logging.warning('[①]:\n' + cmd_result)

        # 判断是否成功登录
        if re.search(r'>$', cmd_result):
            logging.warning('[%s]: 登录OLT成功!' % Ip)
            return True
        else:
            logging.warning('[%s]: 登录OLT失败!' % Ip)
            return False

    # 给连通的FTTB设备下发配置
    def exec_cmd(self, UserName, PassWord, *Fttb_Ip):
        self.tn.write(b'enable\n')
        self.tn.write(b'display ip routing-table 0.0.0.0 0.0.0.0\n')
        self.tn.write(b'\n')
        time.sleep(2)
        cmd_result = self.tn.read_very_eager().decode('ascii')
        if re.search(r'RD\s+(\d+.\d+.\d+.\d+)', cmd_result, re.M):
            GateWay = re.search(r'RD\s+(\d+.\d+.\d+.\d+)',
                                cmd_result, re.M).group(1)
            logging.warning('[默认网关]: %s' % GateWay)
        DealCount = 0

        # 循环FTTB设备列表
        for Fttb in Fttb_Ip:
            # Ping连通性测试
            self.tn.write(b'ping ' + str(Fttb).encode('ascii') + b'\n')
            self.tn.write(b'\n')
            time.sleep(5)
            cmd_result = self.tn.read_very_eager().decode('ascii')
            logging.warning(cmd_result)
            if re.search(r'Reply from', cmd_result):
                logging.warning('[%s]: Ping连通, 准备下发配置...' % Fttb)
                # if self.login_dev(Fttb, UserName, PassWord):
                self.tn.write(b'telnet ' + Fttb.encode('ascii') + b'\n')
                self.tn.write(b'\n')
                time.sleep(3)

                # 匹配登录用户名提示符
                self.tn.read_until(b'>>User name:', timeout=10)
                self.tn.write(UserName.encode('ascii') + b'\n')

                # 匹配登录密码提示符
                self.tn.read_until(b'>>User password:', timeout=10)
                self.tn.write(PassWord.encode('ascii') + b'\n')

                # 首次获取登录结果
                time.sleep(2)
                cmd_result = self.tn.read_very_eager().decode('ascii')
                logging.warning('[②]:\n' + cmd_result)

                # FTTB设备首次登陆提醒处理
                if re.search(r"Press\s+'Q'\s+to\s+break", cmd_result, re.M):
                    self.tn.write(b'Q')
                    time.sleep(1)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    logging.warning('[③]:\n' + cmd_result)
                    time.sleep(1)
                elif re.search(r"Are you sure to modify system time", cmd_result, re.M):
                    self.tn.write(b'n')
                    time.sleep(1)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    logging.warning('[③]:\n' + cmd_result)
                    time.sleep(1)

                # 判断是否成功登录
                if re.search(r'>$', cmd_result):
                    logging.warning('[%s]: 登录FTTB成功!' % Fttb)

                    self.tn.write(b'enable\n')
                    time.sleep(1)
                    self.tn.write(b'config\n')
                    time.sleep(1)

                    # 静态路由配置
                    self.tn.write(
                        b'display current-configuration section post-system\n')
                    self.tn.write(b'\n')
                    time.sleep(2)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    logging.warning('[路由初始配置]: ...\n' + cmd_result)
                    if not re.search(r'ip\s+route-static\s+10.41.81.64\s+255.255.255.224\s+%s' % GateWay, cmd_result,
                                     re.M):
                        self.tn.write(
                            b'ip route-static 10.41.81.64 255.255.255.224 ' + GateWay.encode('ascii') + b'\n')
                        self.tn.write(b'\n')
                        time.sleep(1)
                        logging.warning('[路由①]: 配置成功...')
                    else:
                        logging.warning('[路由①]: 配置已存在...')
                    if not re.search(r'ip\s+route-static\s+10.40.0.0\s+255.248.0.0\s+%s' % GateWay, cmd_result, re.M):
                        self.tn.write(
                            b"ip route-static 10.40.0.0 255.248.0.0 " + GateWay.encode('ascii') + b'\n')
                        self.tn.write(b'\n')
                        time.sleep(1)
                        logging.warning('[路由②]: 配置成功...')
                    else:
                        logging.warning('[路由②]: 配置已存在...')
                    if not re.search(r'ip\s+route-static\s+10.48.0.0\s+255.254.0.0\s+%s' % GateWay, cmd_result, re.M):
                        self.tn.write(
                            b'ip route-static 10.48.0.0 255.254.0.0 ' + GateWay.encode('ascii') + b'\n')
                        self.tn.write(b'\n')
                        time.sleep(1)
                        logging.warning('[路由③]: 配置成功...')
                    else:
                        logging.warning('[路由③]: 配置已存在...')
                    if not re.search(r'ip\s+route-static\s+10.0.0.0\s+255.240.0.0\s+%s' % GateWay, cmd_result, re.M):
                        self.tn.write(
                            b'ip route-static 10.0.0.0 255.240.0.0 ' + GateWay.encode('ascii') + b'\n')
                        self.tn.write(b'\n')
                        time.sleep(1)
                        logging.warning('[路由④]: 配置成功...')
                    else:
                        logging.warning('[路由④]: 配置已存在...')

                    self.tn.write(
                        b'display current-configuration section post-system\n')
                    self.tn.write(b'\n')
                    time.sleep(2)
                    logging.warning('[路由变更后或者初始配置]: ...\n' +
                                    self.tn.read_very_eager().decode('ascii'))

                    # snmp-agent配置
                    self.tn.write(
                        b'display current-configuration section public-config | include  snmp-agent target-host\n')
                    self.tn.write(b'\n')
                    time.sleep(2)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    logging.warning('[SNMP初始配置]: ...\n' + cmd_result)
                    if not re.search(r'snmp-agent\s+target-host\s+trap-hostname\s+.*\s+address\s+10.41.81.81',
                                     cmd_result, re.M):
                        self.tn.write(
                            b'snmp-agent target-host trap-hostname 1MTU.10.41.81.81 address 10.41.81.81 udp-port 162 trap-paramsname 3MTU.10.41.81.81' + b'\n')
                        self.tn.write(b'\n')
                        time.sleep(1)
                        logging.warning('[SNMP①]: 配置成功...')
                    else:
                        logging.warning('[SNMP①]: 配置已存在...')
                    if not re.search(r'snmp-agent\s+target-host\s+trap-paramsname\s+.*\s+v2C\s+securityname',
                                     cmd_result, re.M):
                        self.tn.write(
                            b'snmp-agent target-host trap-paramsname 3MTU.10.41.81.81 v2C securityname U2000' + b'\n')
                        self.tn.write(b'\n')
                        time.sleep(1)
                        logging.warning('[SNMP②]: 配置成功...')
                    else:
                        logging.warning('[SNMP②]: 配置已存在...')

                    self.tn.write(
                        b'display current-configuration section public-config | include  snmp-agent target-host\n')
                    self.tn.write(b'\n')
                    time.sleep(2)
                    cmd_result = self.tn.read_very_eager().decode('ascii')
                    logging.warning('[SNMP变更后或者初始配置]: ...\n' + cmd_result)

                    self.tn.write(b'return\n')
                    self.tn.write(b'save\n')
                    self.tn.write(b'\n')
                    self.tn.write(b'quit\n')
                    self.tn.write(b'y\n')
                    logging.warning(self.tn.read_very_eager().decode('ascii'))
                else:
                    logging.warning('[%s]: 登录FTTB失败!' % Fttb)

            else:
                logging.warning('[%s]: Ping不通, 忽略配置下发...\n' % Fttb)

            DealCount += 1
            logging.warning('[当前OLT下待处理FTTB设备总数/已处理数]: %d/%d...\n' %
                            (len(Fttb_Ip), DealCount))

        self.logout_dev()

    # 退出登录保存配置
    def logout_dev(self):
        self.tn.write(b'quit\n')
        self.tn.write(b'y\n')


for key, value in ConfigDev.items():
    Telnet_Client = TelnetClient()
    if Telnet_Client.login_dev(key, OltUserName, OltPassWord):
        Telnet_Client.exec_cmd(FttbUserName, FttbPassWord, *value)
