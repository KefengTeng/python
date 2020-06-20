#!/bin/env python3
# -*- coding: utf-8 -*-

import time
import paramiko

# A high-level representation of a session with an SSH server
client = paramiko.SSHClient()

# Set policy to use when connecting to servers without a known host key
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def searchSRIP():

    filename = 'searchSR_{}.txt'.format(time.strftime('%Y_%m_%d'))
    with open(r'/root/tengkf/logs/' + filename, 'a') as final:

        sr_Dict = {}

        # Connect to an SSH server and authenticate to it
        client.connect(hostname='x.x.x.x', username="xxxx", password="xxxx")

        # Start an interactive shell session on the SSH server
        channel = client.invoke_shell()
        time.sleep(1)

        # Send data to the channel
        channel.send("screen-length 0 temporary\n")

        # Receive data from the channel
        time.sleep(1)
        print(channel.recv(1024).decode('utf-8'))

        with open('ip.txt') as f:

            for line in f:

                # Remove line break
                line = line.strip()

                circuit_Code = line.split('\t')[0]
                # Remove spaces
                circuit_Name = line.split('\t')[1].replace(' ', '')
                circuit_Ip = line.split('\t')[2]
                circuit_Bandwidth = line.split('\t')[3]

                # Send data to the channel
                channel.send(
                    "display ip routing-table {}\n".format(circuit_Ip))

                # buff
                buff = ""
                while not buff.endswith('>'):
                    # Receive data from the channel
                    time.sleep(1)
                    respond = channel.recv(1024).decode('utf-8')
                    buff += respond

                print(buff)
                sr_Dict.setdefault(buff.split('\r\n')[-2].split()[-2], []).append(
                    [circuit_Code, circuit_Name, circuit_Ip, circuit_Bandwidth])

        # Close the channel
        channel.close()

        # Close this SSHClient and its underlying Transport.
        client.close()

        for sr_Ip, user_Info in sr_Dict.items():

            if sr_Ip != '0.0.0.0':

                # Connect to an SSH server and authenticate to it
                client.connect(hostname=sr_Ip, username="xxxx",
                               password="xxxx")

                # Start an interactive shell session on the SSH server
                channel = client.invoke_shell()
                time.sleep(1)

                # Send data to the channel
                channel.send("\n")
                time.sleep(1)

                if channel.recv(1024).decode('utf-8').endswith('>'):

                    # Send data to the channel
                    channel.send("screen-length 0 temporary\n")

                    # Receive data from the channel
                    time.sleep(1)
                    print(channel.recv(1024).decode('utf-8'))

                    for num in range(len(user_Info)):

                        # Send data to the channel
                        channel.send(
                            "display ip routing-table {}\n".format(user_Info[num][-2]))

                        # buff
                        buff = ""
                        while not buff.endswith('>'):
                            # Receive data from the channel
                            time.sleep(1)
                            respond = channel.recv(1024).decode('utf-8')
                            buff += respond

                        print(buff)

                    # Append port info into list
                        user_Info[num].append(
                            buff.split('\r\n')[-3].split()[-1])

                    # Close the channel
                    channel.close()

                    # Close this SSHClient and its underlying Transport.
                    client.close()

                    print(sr_Ip + ':', user_Info)

                else:

                    # Send data to the channel
                    channel.send("terminal length 0\n")

                    # Receive data from the channel
                    time.sleep(1)
                    print(channel.recv(1024).decode('utf-8'))

                    for num in range(len(user_Info)):
                        # Send data to the channel
                        channel.send("show ip forwarding route {} | include Static|Direct\n".format(
                            user_Info[num][-2]))

                        # buff
                        buff = ""
                        while not buff.endswith('#'):
                            # Receive data from the channel
                            time.sleep(1)
                            respond = channel.recv(1024).decode('utf-8')
                            buff += respond

                        print(buff)
                    # Append port info into list
                        user_Info[num].append(
                            buff.split('\r\n')[-2].split()[3])

                    # Close the channel
                    channel.close()

                    # Close this SSHClient and its underlying Transport.
                    client.close()

                    print(sr_Ip + ':', user_Info)

            else:

                for num in range(len(user_Info)):
                    user_Info[num].append('NULL')

        final.write('电路名\t带宽\tSR设备\t子接口\t用户IP\t接入号\n')
        for sr_Ip, user_Info in sr_Dict.items():
            for num in range(len(user_Info)):
                final.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                    user_Info[num][1], user_Info[num][3], sr_Ip, user_Info[num][4], user_Info[num][2], user_Info[num][0]))


if __name__ == '__main__':
    searchSRIP()
