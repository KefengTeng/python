#!/bin/env python3
# -*- coding: utf-8 -*-

import re

def is_valid_email(addr):
    if re.match(r'[\w.]+@\w+\.\w+', addr):
        return True

# 测试
assert is_valid_email('someone@gmail.com')
assert is_valid_email('bill.gates@microsoft.com')
assert not is_valid_email('bob#example.com')
assert not is_valid_email('mr-bob@example.com')
print('ok')

def name_of_email(addr):
    nameRegex = re.compile(r'<?([\s\w]+)>?[\s\w]*@(.*)')
    if nameRegex.match(addr):
        return nameRegex.match(addr).group(1)

# 测试:
assert name_of_email('<Tom Paris> tom@voyager.org') == 'Tom Paris'
assert name_of_email('tom@voyager.org') == 'tom'
print('ok')
