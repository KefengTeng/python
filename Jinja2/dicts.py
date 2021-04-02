#!/bin/env python3
# -*- coding: utf-8 -*-

from jinja2 import Template

person = {'name': 'Claire', 'age': 34}

tm = Template("My name is {{ per.name }} and I am {{ per.age }}")
#tm = Template("My name is {{ per['name'] }} and I amd {{ per['age'] }}")

msg = tm.render(per=person)

print(msg)
