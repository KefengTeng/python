# -*- coding: utf-8 -*-
import re


def write_dict(filename):
    f_dict = {}
    with open(filename, encoding='utf-8') as f:
        f_list = f.readlines()
        k, v = 2, 1
        f_dict.setdefault(f_list[k], f_list[v])
        while v <= len(f_list) - 4:
            k += 3
            v += 3
            f_dict.setdefault(f_list[k].strip(), f_list[v].strip())
    return f_dict


fi_dict = write_dict('IPTV.m3u')
fn_dict = write_dict('New.m3u')

title_regex = re.compile(r'(.*),(.*)')
for key in fn_dict.keys():
    if key in fi_dict:
        fn_dict[key] = title_regex.search(fn_dict[key]).group(
            1) + ',' + title_regex.search(fi_dict[key]).group(2)

with open('final.m3u', 'w') as f:
    for k, v in fn_dict.items():
        f.write(v + '\r' + k + '\r')