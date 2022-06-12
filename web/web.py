#!/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver


options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
# to supress the error messages/logs
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

driver.get(
    'https://kc.zhixueyun.com/#/study/subject/detail/3961220a-ddb5-4cdb-a906-4f923bf74ecd')

# 获取html源码
html = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
