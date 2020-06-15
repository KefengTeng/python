#!/bin/env python3
# -*- coding: utf-8 -*-

import os

fPath = r'/root/python3'

def all_file(path, end_type):

    list_file = os.listdir(path)

    for item in list_file:
        
        new_path = os.path.join(path, item)

        if os.path.isfile(new_path):
        
            if os.path.split(new_path)[1].endswith(end_type):
               
               print(os.path.abspath(new_path))

        else:
            
            all_file(new_path, end_type)


all_file(fPath, '.py')
