#!/bin/env python3
# -*- coding: utf-8 -*-

import email, smtplib

from email.mime.text import MIMEText
msg = MIMEText('能发送成功吗？我猜能!', 'plain', 'utf-8')

# 输入Email地址和口令
from_addr = input('From: ')
password = input('Password: ')
# 输入收件人地址
to_addr = input('To: ')
# 输入SMTP服务器地址
smtp_server = input('SMTP server: ')

server = smtplib.SMTP(smtp_server, 25)
server.set_debuglevel(1)
server.login(from_addr, password)
server.sendmail(from_addr, [to_addr], msg.as_string())
server.quit()
