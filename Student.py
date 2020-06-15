#!/bin/env python3
# -*- coding: utf-8 -*-

class Student(object):

    def __init__(self, name, gender):
        self.name = name
        self.__gender = gender

    def set_gender(self, gender):
        if gender in ('male', 'female'):
            self.__gender = gender 
        else:
            raise ValueError('bad gender')
    
    def get_gender(self):
        return self.__gender

bart = Student('Bart', 'male')

if bart.get_gender() != 'male':
    print('测试失败!')
else:
    bart.set_gender('female')
    if bart.get_gender() != 'female':
        print('测试失败!')
    else:
        print('测试成功!')

        
