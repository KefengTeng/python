#!/bin/env python3
# -*- coding: utf-8 -*-

import time
import paramiko

# A high-level representation of a session with an SSH server
client = paramiko.SSHClient()

# Set policy to use when connecting to servers without a known host key
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def ConfigSR():

    # Create an empty dictionary, use the ip as key, append the port into a list as value
    dev_dict = {}

    with open('dev.txt') as f:
        for line in f:
            dev_dict.setdefault(line.split()[0], []).append(line.split()[1])

    for dev_Ip, dev_Port in dev_dict.items():

        # Connect to an SSH server and authenticate to it
        client.connect(hostname=dev_Ip, username="xxxx", password="xxxx")

        # Start an interactive shell session on the SSH server
        channel = client.invoke_shell()
        time.sleep(1)

        # Send data to the channel
        channel.send("screen-length 0 temporary\n")

        # Receive data from the channel
        time.sleep(1)
        print(channel.recv(1024).decode('utf-8'))

        # Send data to the channel
        channel.send("system-view\n")

        # Receive data from the channel
        time.sleep(1)
        print(channel.recv(1024).decode('utf-8'))


        for port in dev_Port:

            # Send data to the channel
            channel.send("interface {}\n".format(port))

            # Receive data from the channel
            time.sleep(1)
            print(channel.recv(1024).decode('utf-8'))

            # Send data to the channel
            channel.send("statistic enable\n")

            # Receive data from the channel
            time.sleep(1)
            print(channel.recv(1024).decode('utf-8'))

            # Send data to the channel
            channel.send("quit\n".format(port))

            # Receive data from the channel
            time.sleep(1)
            print(channel.recv(1024).decode('utf-8'))

        # Send data to the channel
        channel.send("return\n")

        # Receive data from the channel
        time.sleep(1)
        print(channel.recv(1024).decode('utf-8'))

        # Send data to the channel
        channel.send("save\n")

        # Receive data from the channel
        time.sleep(1)
        print(channel.recv(1024).decode('utf-8'))

        # Send data to the channel
        channel.send("y\n")

        # Receive data from the channel
        time.sleep(1)
        print(channel.recv(1024).decode('utf-8'))

        # Close the channel
        channel.close()

        # Close this SSHClient and its underlying Transport.
        client.close()

if __name__ == '__main__':
    ConfigSR()
