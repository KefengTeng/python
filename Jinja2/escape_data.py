#!/bin/env python3
# -*- coding: utf-8 -*-

from jinja2 import Template, escape

data = '<a>Today is a sunny day</a>'

tm = Template("{{ data|e }}")
msg = tm.render(data=data)

print(msg)
print(escape(data))
