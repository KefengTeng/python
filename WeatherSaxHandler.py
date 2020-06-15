#!/bin/env python3
# -*- coding: utf-8 -*-

from xml.parsers.expat import ParserCreate
from urllib import request

class WeatherSaxHandler(object):
    weather = {'city': 1, 'cityname': [], 'forecast': []}

    def start_element(self, name, attrs):
        if name == 'beijing':
            self.weather['city'] = '北京'
        if name == 'city':
            self.weather['cityname'].append(attrs['cityname'])
            self.weather['forecast'].append({
                'state': attrs['stateDetailed'],
                'high': attrs['tem2'],
                'low': attrs['tem1']
            })

def parseXml(xml_str):

    handler = WeatherSaxHandler()
    parser = ParserCreate()
    parser.StartElementHandler = handler.start_element
    parser.Parse(xml_str)
    print('City:' + handler.weather['city'])
    for (x, y) in zip(handler.weather['cityname'], handler.weather['forecast']):
        print('Region:'+x)
        print(y)
    return handler.weather

URL = 'http://flash.weather.com.cn/wmaps/xml/beijing.xml'

with request.urlopen(URL, timeout=4) as f:
    data = f.read()

result = parseXml(data.decode('utf-8'))
