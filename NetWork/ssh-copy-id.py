#!/bin/env python2
# -*- coding: utf-8 -*-

# Author: brokensmile@yeah.net
# Copy the ssh public key of master host to the other hosts automaticaly, the master host need to install nmap
import os
import re
import time
import getpass
import logging
import paramiko

# 输入主机登录用户名
while True:
    user_name = raw_input('请输入主机用户名: \n')
    if user_name != '':
        if os.getlogin() != user_name:
            logging.warning('要操作的用户和当前登录的用户不一致, 请重新输入...')
        else:
            break
    else:
        logging.warning('用户名不能为空...\n')

# 输入主机密码
user_pass = getpass.getpass(prompt='请输入主机户密码: \n')

# 输入用户家目录绝对路径
while True:
    home = raw_input('请输入主机用户名绝对路径: 例如(/root)\n')
    if re.search(r'^/', home):
        logging.warning('用户家目录为: %s\n' % home)
        break
    else:
        logging.warning('用户家目录输入错误，请重新输入...\n')


# 输入要扫描的网段
while True:
    network = raw_input('请以CIDR方式输入要扫描的网段: 例如(192.168.1.0/24)\n')
    if re.search(r'\d+\.\d+\.\d+\.\d+/\d+', network):
        logging.warning('要扫描的网段为: %s\n' % network)
        break
    else:
        logging.warning('网段输入错误，请重新输入...\n')


def exec_cmd(cmd):
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    if stderr.read() == '':
        logging.warning('[%s]: 命令执行√...\n' % cmd)
    else:
        logging.warning('[%s]: 命令执行×...\n' % cmd)


# 判断主机公钥是否存在, 不存在则创建
if not os.path.isfile("%s/.ssh/id_rsa.pub" % home):
    logging.warning('主机公钥不存在, 准备生成...\n')
    os.system("ssh-keygen -t rsa -P '' -f %s/.ssh/id_rsa" % home)
    if os.path.isfile("%s/.ssh/id_rsa.pub" % home):
        logging.warning('主机公钥生成成功, 准备拷贝公钥至其他主机...\n')
else:
    logging.warning('主机公钥已存在, 准备拷贝公钥至其他主机...\n')

with open("%s/.ssh/id_rsa.pub" % home) as kf:
    pub_key = kf.readlines()[0]

# 调用shell命令扫描SSH默认端口开放主机, 并将结果写入文件
time_begin = time.time()
os.system("nmap -sS %s -p22 -oG hosts.txt" % network)
if int(os.stat("hosts.txt").st_mtime) > time_begin:
    logging.warning('SSH端口开放主机扫描成功...\n')
else:
    logging.warning('SSH端口开放主机扫描失败...\n')

# 拷贝公钥至SSH开放的主机
with open('hosts.txt', 'r') as f:
    for line in f:
        target_ip = re.compile(r'(\d+\.\d+\.\d+\.\d+).*Ports:\s+22/open', re.M)
        if target_ip.search(line):
            dst_ip = target_ip.search(line).group(1)
            logging.warning('尝试拷贝SSH公钥至: %s...\n' % dst_ip)
            try:
                # A high-level representation of a session with an SSH server
                ssh_client = paramiko.SSHClient()

                # Set policy to use when connecting to servers without a known host key
                ssh_client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())

                # Connect to an SSH server and authenticate to it
                logging.warning('尝试登录主机: %s ...\n' % dst_ip)
                ssh_client.connect(
                    hostname=dst_ip, username=user_name, password=user_pass)
                logging.warning('登录主机成功: %s ...\n' % dst_ip)

                # 创建.ssh目录
                exec_cmd("test -d %s/.ssh || mkdir -p %s/.ssh/" % (home, home))

                # 修改.ssh目录权限
                exec_cmd("chmod 700 %s/.ssh/" % home)

                # 追加写入authorized_keys
                exec_cmd("echo -n '%s' >> %s/.ssh/authorized_keys" %
                         (pub_key, home))

                # 修改authorized_keys权限
                exec_cmd("chmod 600 %s/.ssh/authorized_keys" % home)

            except paramiko.AuthenticationException:
                logging.warning('登录主机失败...\n')

            finally:
                logging.warning('登出主机成功: %s...\n' % dst_ip)
                ssh_client.close()
