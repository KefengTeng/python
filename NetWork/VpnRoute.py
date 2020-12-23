#!/bin/env python3
# -*- coding: utf-8-*-

import os
import re
import sys
import time

# �ж����θ�ʽ�Ƿ����Ҫ��
Network_Regex = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)/(\d+)$')
Flag = 1
while Flag:
    Personal_Network_Sum = input(
        "[�������Զ�������,��ε�ַ�Էֺŷָ�]: �� (114.114.114.114/32;114.114.115.115/32)\n")
    Personal_Network_List = Personal_Network_Sum.split(';')
    Flag = len(Personal_Network_List)
    for Personal_Network in Personal_Network_List:
        if Network_Regex.search(Personal_Network):
            Bin1, Bin2, Bin3, Bin4, Mask = Network_Regex.search(
                Personal_Network).groups()
            if int(Bin1) != 127 and 0 <= int(Bin1) <= 255 and 0 <= int(Bin2) <= 255 and 0 <= int(Bin3) <= 255 and 0 <= int(Bin4) <= 255 and 1 <= int(Mask) <= 32:
                print("[�����������Ϊ]:\t%s\n" % Personal_Network)
                Flag -= 1
            else:
                print("����������δ���, ����������...\n")
        else:
            print("����������θ�ʽ����ȷ, ����������...\n")

# ���ұ���IP
Ip_Result = os.popen("ipconfig").read()
Ip = re.search(r'(192\.168\.251\.\d+)', Ip_Result, re.M).group(1)
print("[����IP]:\t%s\n" % Ip)


def exchange_maskint(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(int(mask_int)):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


# ����VPN����
try:
    Route_Result = os.popen("route PRINT -4").read()
    GateWay = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+%s' %
                        Ip, Route_Result, re.M).group(1)
    print("[Ĭ������]:\t%s\n" % GateWay)
    InterFace = re.search(r'(\d+)\.\.\..*Sangfor SSL VPN',
                          Route_Result, re.M).group(1)
    print("[���ӿ�]:\t%s\n" % InterFace)

    Route_Regex = re.compile(
        r'(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+%s\s+%s' % (GateWay, Ip))
    for line in Route_Result.split('\n'):
        if Route_Regex.search(line):
            Del_Net, Del_Mask = Route_Regex.search(line).groups()
            if Del_Net != "192.168.251.0":
                print("[����ɾ������]:\t%s %s\n" % (Del_Net, Del_Mask))
                print(os.popen("route DELETE %s" % (Del_Net)).read())
    Company_Net = ['192.168.5.0', '192.168.6.0',
                   '192.168.118.0', '192.168.130.0']
    for Private_Net in Company_Net:
        print("[�������ӹ�˾�ڲ�����]:\t%s 255.255.255.0\n" % Private_Net)
        print(os.popen("route ADD %s MASK 255.255.255.0 %s METRIC 256 IF %s" %
                       (Private_Net, GateWay, InterFace)).read())

    Personal_Network_List = Personal_Network_Sum.split(';')
    for Personal_Network in Personal_Network_List:
        CustNet, CustMask = Personal_Network.split('/')
        CustBinMask = exchange_maskint(CustMask)
        print("[���������Զ�������]:\t%s %s\n" % (CustNet, CustBinMask))
        print(os.popen("route ADD %s MASK %s %s METRIC 256 IF %s" %
                       (CustNet, CustBinMask, GateWay, InterFace)).read())
except AttributeError:
    print('VPN·�ɱ������, �޷���ȡĬ�����أ�������VPN֮���ٴ����иó���...\n������10s���˳�...\n')
finally:
    print('������10s���˳�...\n')
    for i in range(20):
        time.sleep(0.5)
        sys.stdout.write('#')
        sys.stdout.flush()
