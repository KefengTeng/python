#!/bin/env python3
# -*- coding: utf-8 -*-

import re
import cx_Oracle


def exchange_binmask(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(int(mask_int)):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


with open(r'C:\\Users\\PaintMyLove\\Documents\\Download\\ip2.txt') as f:
    for line in f:
        servno = line.split()[0]
        ipmask = line.split()[1]
        ip1t3, ip4 = re.search(r'(\d+\.\d+\.\d+\.)(\d+)', ipmask).group(1, 2)
        ip4 = int(ip4) + 1
        intmask = re.search(r'\d+$', ipmask).group(0)
        binmask = exchange_binmask(intmask)
        ip = ip1t3 + str(ip4)

        with cx_Oracle.connect('x', 'x', '127.0.0.10:1521/dbnms', encoding='UTF-8') as conn:
            cur = conn.cursor()
            sql = f"""SELECT C.LOOPADDRESS, A.INTDESCR, A.IPADDRESS, A.NETMASK
                        FROM DEVADDR A, DEVICE C, PORTINFO D
                        WHERE A.IPADDRESS = :ip
                        AND A.NETMASK = :binmask
                        AND A.DEVICEID = D.DEVICEID
                        AND A.INTDESCR = D.PORTDESCR
                        AND D.OPERSTATUS = 'up
                        AND C.CHANGETYPE = '0'
                        AND A.DEVICEID = C.DEVICEID"""
            cur.execute(sql, [ip, binmask])
            rows = cur.fetchall()
            for row in rows:
                print(servno, row)
