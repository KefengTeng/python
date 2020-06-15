#!/bin/env python3
# -*- coding: utf-8 -*-

import paramiko 

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.1.1', port=22, username='root', password='pt880609')
    print('connected-respinring')
    (stdin, stdout, stderr) = client.exec_command('ls')
    print(stdout.readlines())
    client.close()

finally:
    print('done')
