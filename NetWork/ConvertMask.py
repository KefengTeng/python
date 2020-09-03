import re


def exchange_binmask(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(int(maskint)):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


with open('ip.txt') as f:
    for line in f:
        servno = line.split('\t')[0]
        ipmask = line.split('\t')[1]
