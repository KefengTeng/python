#!/bin/env python3
# -*- coding: utf-8 -*-

from netaddr import *
from openpyxl import *

# 打开Excel文件
wb = load_workbook(r'C:\\Users\\PaintMyLove\\Desktop\\副本专线机房数据1218.xlsx')

# 读取源工作表
wbr = wb.get_sheet_by_name('机房IP地址段信息')

# 创建新工作表
wbw = wb.create_sheet('机房IP地址段反掩码')

# 写表头
wbw.append(['*机房名称', '*起始IP地址', '*终止IP地址', '*网络号', '*反掩码'])

# 读取源工作表数据, 忽略表头
for row in wbr.iter_rows(min_row=2):
    # 网络号
    netWork = str(iprange_to_cidrs(row[1].value, row[2].value)[0].network)
    # 反掩码
    reversedMask = str(iprange_to_cidrs(
        row[1].value, row[2].value)[0].hostmask)
    # 写工作表
    wbw.append([row[0].value, row[1].value,
                row[2].value, netWork, reversedMask])

# 保存工作簿
wb.save(r'C:\\Users\\PaintMyLove\\Desktop\\副本专线机房数据1218.xlsx')
