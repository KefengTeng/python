#!/bin/env python3
# -*- coding: utf-8 -*-

def log(text):
    def decorator(func):
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator

@log('excute')

def now():
    print('2015-3-25')

now()
