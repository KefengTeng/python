#!/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

# 节点编码列表
nodes = ['NOD06q', 'NOD06u']

# 配置文件绝对路径列表
abs_dir = []
for node in nodes:
    # 节点绝对路径
    abs_1stdir = os.path.join(r'/slview/nms/data/configfile/', node)
    for subdir1 in os.listdir(abs_1stdir):
        # IP地址段汇总绝对路径
        abs_2nddir = os.path.join(abs_1stdir, subdir1)
        for subdir2 in os.listdir(abs_2nddir):
            if re.search(r'\d+\.\d+\.\d+\.\d+$', subdir2):
                # IP地址绝对路径
                abs_dir.append(os.path.join(abs_2nddir, subdir2))

# 最新配置文件列表
newestfile_list = []
for subdir in abs_dir:
    # 所有配置文件列表
    file_list = []
    for file in os.listdir(subdir):
        file_list.append(os.path.join(subdir, file))
    # 配置文件列表按修改时间排序
    file_list.sort(key=lambda f: os.path.getmtime(f))
    # 过滤2020年配置文件
    if re.search(r'2020', file_list[-1]):
        newestfile_list.append(file_list[-1])

for cfg in newestfile_list:
    if re.search(r'NOD06q', cfg):
        os.system("cp %s /tmp/NK/" % cfg)
    elif re.search(r'NOD06u', cfg):
        os.system("cp %s /tmp/HQ/" % cfg)
