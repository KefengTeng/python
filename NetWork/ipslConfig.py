#!/bin/env python3
# -*- coding: utf-8 -*-

import pypinyin
import paramiko
import os
import re
import pandas as pd

# A high-level representation of a session with an SSH server
client = paramiko.SSHClient()

# Set policy to use when connecting to servers without a known host key
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# 查找指定目录下最新Excel文件, 忽略子目录
excelDir = r'/home/brokensmile/Data/Python3/data/'
fileList = os.listdir(excelDir)
fileList.sort(key=lambda file: os.path.getmtime(excelDir + file)
              if os.path.isfile(excelDir + file) else 0)
print('\n当前待读取Excel文件: %s\n' % fileList[-1])

# 读取Excel文件中的参数, 并转存到字典
with pd.ExcelFile(excelDir + fileList[-1]) as xls:
    dataArray = pd.read_excel(xls, '工单详细信息', header=None).values

paraDict = dict(dataArray.reshape(int(dataArray.size / 2), 2))
custEnName = "".join(map(lambda lowerEn: lowerEn.capitalize(),
                         pypinyin.lazy_pinyin(paraDict['客户名称'])))
servNo = paraDict['电路代号']
servQos = paraDict['速率(M)']
servVlan = paraDict['VLAN']
interNet, interMask = paraDict['互联IP'].split('/')
interIP1, interIP2 = ".".join(interNet.split('.')[0:3]) + '.' + str(int(interNet.split(
    '.')[3]) + 1), ".".join(interNet.split('.')[0:3]) + '.' + str(int(interNet.split('.')[3]) + 2)
binInterMask = "255." * int(int(interMask) // 8) + \
    str(int(256 - 256 / 2**(int(interMask) % 8)))
custNet = ''
if '用户IP' in paraDict:
    custNet, custMask = paraDict['用户IP'].split('/')
    binCustMask = "255." * int(int(interMask) // 8) + \
        str(int(256 - 256 / 2**(int(custMask) % 8)))
srDev = paraDict['SR设备'] if 'SR设备' in paraDict else ''
srIp = re.search(r'(\d+\.\d+\.\d+\.\d+)',
                 srDev).group(1) if srDev != '' else ''
srDownPort = paraDict['SR设备下联口'] if 'SR设备下联口' in paraDict else ''
swIp = paraDict['交换机设备IP']
swDownPort = paraDict['交换机设备下联口']

print('*********SR配置*********\n')
print('######限速模板#####\n')
print('qos-profile uni_%sm' % (servQos))
print('car cir %d pir %d inbound' %
      (int(servQos) * 1024 * 1.15, int(servQos) * 1024 * 1.15))
print('car cir %d pir %d outbound' %
      (int(servQos) * 1024 * 1.15, int(servQos) * 1024 * 1.15))
print('quit\n')
print('###接口及路由配置###\n')
if srDownPort != '':
    print('interface %s.%s0000' % (srDownPort, servVlan))
print('description USER::%s::%s.CO::%sM' % (servNo, custEnName, servQos))
print('undo enable snmp trap updown')
print('control-vid %s dot1q-termination' % (servVlan))
print('dot1q termination vid %s' % (servVlan))
print('ip address %s %s' % (interIP1, binInterMask))
print('undo icmp host-unreachable send')
print('undo icmp redirect send')
print('traffic-policy uni_denyweb outbound')
print('arp broadcast enable')
print('ip urpf strict')
print('qos-profile uni_%sm inbound vlan %s identifier none' %
      (servQos, servVlan))
print('qos-profile uni_%sm outbound vlan %s identifier none' %
      (servQos, servVlan))
print('statistic enable')
print('quit')

if custNet != '' and srDownPort:
    print('ip route-static %s %s %s%s0000 %s description USER::%s::%s.CO::%sM'
          % (custNet, binCustMask, srDownPort, servVlan, interIP2, servNo, custEnName, servQos))
# 下发命令字典
ConfigDict = {}
if srIp != '' and srDownPort != '' and swIp != '' and swDownPort != '':
    qosSrCmdList = ConfigDict.setdefault(srIp, {}).setdefault('Qos-config', [])
    interfaceSrCmdList = ConfigDict.setdefault(
        srIp, {}).setdefault('interface-config', [])
    routeSrCmdList = ConfigDict.setdefault(
        srIp, {}).setdefault('route-config', [])
    swCmdList = ConfigDict.setdefault(swIp, [])
    qosSrCmdList.append('qos-profile uni_%sm' % (servQos))
    qosSrCmdList.append('car cir %d pir %d inbound' % (
        int(servQos) * 1024 * 1.15, int(servQos) * 1024 * 1.15))
    qosSrCmdList.append('car cir %d pir %d outbound' % (
        int(servQos) * 1024 * 1.15, int(servQos) * 1024 * 1.15))
    qosSrCmdList.append('quit')
    interfaceSrCmdList.append('interface %s.%s0000' % (srDownPort, servVlan))
    interfaceSrCmdList.append(
        'description USER::%s::%s.CO::%sM' % (servNo, custEnName, servQos))
    interfaceSrCmdList.append('undo enable snmp trap updown')
    interfaceSrCmdList.append('control-vid %s dot1q-termination' % (servVlan))
    interfaceSrCmdList.append('dot1q termination vid %s' % (servVlan))
    interfaceSrCmdList.append('ip address %s %s' % (interIP1, binInterMask))
    interfaceSrCmdList.append('undo icmp host-unreachable send')
    interfaceSrCmdList.append('undo icmp redirect send')
    interfaceSrCmdList.append('traffic-policy uni_denyweb outbound')
    interfaceSrCmdList.append('arp broadcast enable')
    interfaceSrCmdList.append('ip urpf strict')
    interfaceSrCmdList.append(
        'qos-profile uni_%sm inbound vlan %s identifier none' % (servQos, servVlan))
    interfaceSrCmdList.append(
        'qos-profile uni_%sm outbound vlan %s identifier none' % (servQos, servVlan))
    interfaceSrCmdList.append('statistic enable')
    interfaceSrCmdList.append('quit')
    if custNet != '' and srDownPort != '':
        interfaceSrCmdList.append('ip route-static %s %s %s%s0000 %s description USER::%s::%s.CO::%sM'
                                  % (custNet, binCustMask, srDownPort, servVlan, interIP2, servNo, custEnName, servQos))
    qosSrCmdList = ['dis device']
    interfaceSrCmdList = ['dis device']
    routeSrCmdList = ['dis device']
    # Connect to an SSH server and authenticate to it
    client.connect(hostname=srIp, username="xxxx", password="xxxx")

    # Start an interactive shell session on the SSH server
    channel = client.invoke_shell()
    time.sleep(0.2)

    # Send data to the channel
    channel.send("system-view\n")

    # Receive data from the channel
    time.sleep(0.2)
    print(channel.recv(1024).decode('utf-8'))

    def runCmd(*List):
        for cmd in List:
            channel.send(cmd + "\n")
            time.sleep(0.2)
            print(channel.recv(1024).decode('utf-8'))

    # 检查子接口是否存在
    channel.send("display dot1q information termination interface %s | include control-vid %s\n" %
                 (srDownPort, servVlan))
    if not re.search(r'control-vid', channel.recv(1024).decode('utf-8')):
        channel.send("display qos-profile configuration uni_%sm\n" % (servQos))
        if not re.search(r'qos-profile:', channel.recv(1024).decode('utf-8')):
            runCmd(*qosSrCmdList)
        runCmd(*interfaceSrCmdList)
        if custNet != '':
            runCmd(*routeSrCmdList)
