#!/bin/env python3
# -*- coding: utf-8 -*-

import base64

#def safe_base64_decode(s):
#    while len(s) % 4 != 0:
#        s += b'='
#    return base64.b64decode(s)


def safe_base64_decode(s):
    s += b'=' * (4 - len(s) % 4)
    return base64.b64decode(s)

# 测试:
assert b'abcd' == safe_base64_decode(b'YWJjZA=='), safe_base64_decode('YWJjZA==')
assert b'abcd' == safe_base64_decode(b'YWJjZA'), safe_base64_decode('YWJjZA')
print('ok')
