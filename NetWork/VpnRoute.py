# -*- coding: gbk -*-

import os
import re

# 判断网段格式是否符合要求
Network_Regex = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)/(\d+)$')
Flag = 1
while Flag:
    Personal_Network_Sum = input(
        "[请输入自定义网段,多段地址以分号分隔]: 例 (114.114.114.114/32;114.114.115.115/32)\n")
    Personal_Network_List = Personal_Network_Sum.split(';')
    for Personal_Network in Personal_Network_List:
        if Network_Regex.search(Personal_Network):
            Bin1, Bin2, Bin3, Bin4, Mask = Network_Regex.search(
                Personal_Network).groups()
            if int(Bin1) != 127 and 0 < int(Bin1) < 255 and 0 < int(Bin2) < 255 and 0 < int(Bin3) < 255 and 0 < int(Bin4) < 255 and 1 <= int(Mask) <= 32:
                print("[您输入的网段为]:\t%s\n" % Personal_Network)
                Flag = 0
            else:
                print("您输入的网段错误, 请重新输入...\n")
        else:
            print("您输入的网段格式不正确, 请重新输入...\n")

# 查找本机IP
Ip_Result = os.popen("ipconfig").read()
Ip = re.search(r'(2\.0\.1\.\d+)', Ip_Result, re.M).group(1)
print("[本机IP]:\t%s\n" % Ip)


def exchange_maskint(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(int(mask_int)):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


# 查找VPN网关
try:
    Route_Result = os.popen("route PRINT -4").read()
    GateWay = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+%s' %
                        Ip, Route_Result, re.M).group(1)
    print("[默认网关]:\t%s\n" % GateWay)
    InterFace = re.search(r'(\d+)\.\.\..*Sangfor SSL VPN',
                          Route_Result, re.M).group(1)
    print("[出接口]:\t%s\n" % InterFace)

    Route_Regex = re.compile(
        r'(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+%s\s+%s' % (GateWay, Ip))
    for line in Route_Result.split('\n'):
        if Route_Regex.search(line):
            Del_Net, Del_Mask = Route_Regex.search(line).groups()
            if re.search(r'192\.168\.6', Del_Net):
                print("[忽略公司内网网段]:\t%s %s\n" % (Del_Net, Del_Mask))
            else:
                print("[即将删除网段]:\t%s %s\n" % (Del_Net, Del_Mask))
                print(os.popen("route DELETE %s" % Del_Net).read())

    Personal_Network_List = Personal_Network_Sum.split(';')
    for Personal_Network in Personal_Network_List:
        CustNet, CustMask = Personal_Network.split('/')
        # if CustMask == 32:
        #    CustBinMask = "255.255.255.255"
        #CustBinMask = "255." * int(int(CustMask) // 8) + str(int(256 - 256 / 2**(int(CustMask) % 8)))
        CustBinMask = exchange_maskint(CustMask)
        print("[即将添加网段]:\t%s %s\n" % (CustNet, CustBinMask))
        print(os.popen("route ADD %s MASK %s %s METRIC 256 IF %s" %
                       (CustNet, CustBinMask, GateWay, InterFace)).read())
except AttributeError:
    print('VPN路由表已清空, 无法获取默认网关，请重连VPN之后再次运行该程序...\n')
