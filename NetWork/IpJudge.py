#!/bin/env python3
# -*- coding: utf-8 -*-

import ipaddr
import re

while True:
    while True:
        Ip = input('请输入单个IP地址: ')
        if(re.search(r'^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$', Ip)):
            break
        else:
            print('您输入的IP地址格式不正确, 请重新输入\n\r')

    Ip = ipaddr.IPAddress(Ip)

    NetTuple = ('123.150.0.0/15', '180.212.0.0/15', '221.238.0.0/16', '221.239.0.0/17', '219.150.32.0/19', '219.150.64.0/19',
                '219.150.96.0/20', '42.80.0.0/16', '42.122.0.0/16', '106.47.0.0/16', '36.106.0.0/16', '42.81.0.0/16')

    for Net in NetTuple:
        IpNet = ipaddr.IPv4Network(Net)
        if(Ip in IpNet):
            print('--->>>√, 该地址属于天津电信\n\r')
            break
    else:
        print('--->>>×, 该地址不属于天津电信\n\r')
