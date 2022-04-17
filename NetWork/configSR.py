#!/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import paramiko

# A high-level representation of a session with an SSH server
client = paramiko.SSHClient()

# Set policy to use when connecting to servers without a known host key
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def ConfigSR():

    # Create an empty dictionary, use the ip as key, append the port into a
    # list as value
    dev_dict = {}

    with open('dev.txt') as f:
        for line in f:
            dev_dict.setdefault(line.split()[0], []).append(line.split()[1])

    for dev_Ip, dev_Port in dev_dict.items():

        # Connect to an SSH server and authenticate to it
        client.connect(hostname=dev_Ip, username='xxxx',
                       password='xxxx', timeout=30)

        # Start an interactive shell session on the SSH server
        channel = client.invoke_shell()
        time.sleep(1)

        # Send data to the channel
        channel.send("\n")
        time.sleep(1)

        # Determine which kind of device it is
        prompt = channel.recv(1024).decode('utf-8', 'ignore')

        # HUAWEI
        if prompt.endswith('>'):

            # Send data to the channel
            channel.send("screen-length 0 temporary\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

            # Send data to the channel
            channel.send("system-view\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

            for port in dev_Port:

                # Determine whether this port has configuration
                channel.send(
                    "display current-configuration interface {}\n".format(port))
                time.sleep(1)

                result = channel.recv(1024).decode('utf-8', 'ignore')
                print("%s\n" % result)
                if re.search(r'Wrong parameter', result, flags=re.M + re.I):
                    lport = port + '0000'
                    # Determine whether this port has configuration
                    channel.send(
                        "display current-configuration interface {}\n".format(lport))
                    time.sleep(1)

                    result = channel.recv(1024).decode('utf-8', 'ignore')
                    print("%s\n" % result)
                    if re.search(r'Wrong parameter', result, flags=re.M + re.I):
                        print("%s\t%s,%s\t主、备选端口均不存在\n" %
                              (dev_Ip, port, lport))
                    elif re.search(r'ip address', result, flags=re.M + re.I):
                        if not re.search(r'statistic enable', result, flags=re.M + re.I):

                            # Send data to the channel
                            channel.send("interface {}\n".format(lport))
                            time.sleep(1)

                            # Receive data from the channel
                            print(channel.recv(1024).decode('utf-8', 'ignore'))

                            # Send data to the channel
                            channel.send("statistic enable\n")
                            time.sleep(1)

                            # Receive data from the channel
                            print(channel.recv(1024).decode('utf-8', 'ignore'))

                            # Send data to the channel
                            channel.send("quit\n".format(port))
                            time.sleep(1)

                            # Receive data from the channel
                            print(channel.recv(1024).decode('utf-8', 'ignore'))
                    else:
                        print("%s\t%s\t备选端口存在, 业务不存在\n" % (dev_Ip, lport))

                elif re.search(r'ip address', result, flags=re.M + re.I):

                    if not re.search(r'statistic enable', result, flags=re.M + re.I):

                        # Send data to the channel
                        channel.send("interface {}\n".format(port))
                        time.sleep(1)

                        # Receive data from the channel
                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                        # Send data to the channel
                        channel.send("statistic enable\n")
                        time.sleep(1)

                        # Receive data from the channel
                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                        # Send data to the channel
                        channel.send("quit\n".format(port))
                        time.sleep(1)

                        # Receive data from the channel
                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                else:
                    print("%s\t%s\t主选端口存在, 业务不存在\n" % (dev_Ip, port))

            # Send data to the channel
            channel.send("return\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

            # Send data to the channel
            channel.send("save\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

            # Send data to the channel
            channel.send("y\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

        # ZTE
        elif prompt.endswith('#'):

            # Send data to the channel
            channel.send("terminal length 0\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

            # Send data to the channel
            channel.send("configure terminal\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

            for port in dev_Port:

                # Determine whether this port has configuration
                channel.send("show running-config-interface {}\n".format(port))
                time.sleep(1)

                result = channel.recv(1024).decode('utf-8', 'ignore')
                print("%s\n" % result)
                if not re.search(r'if-intf', result, flags=re.M + re.I):
                    lport = port + '0000'
                    # Determine whether this port has configuration
                    channel.send(
                        "show running-config-interface {}\n".format(lport))
                    time.sleep(1)

                    result = channel.recv(1024).decode('utf-8', 'ignore')
                    print("%s\n" % result)
                    if not re.search(r'if-intf', result, flags=re.M + re.I):
                        print("%s\t%s,%s\t主、备选端口均不存在\n" %
                              (dev_Ip, port, lport))
                    elif re.search(r'ip address', result, flags=re.M + re.I):

                        if not re.search(r'traffic-statistics enable', result, flags=re.M + re.I):

                            # Send data to the channel
                            channel.send("intf-statistics\n".format(port))
                            time.sleep(1)
                            # Receive data from the channel

                            print(channel.recv(1024).decode('utf-8', 'ignore'))

                            # Send data to the channel
                            channel.send("interface {}\n".format(lport))
                            time.sleep(1)
                            # Receive data from the channel

                            print(channel.recv(1024).decode('utf-8', 'ignore'))

                            # Send data to the channel
                            channel.send("traffic-statistics enable\n")
                            time.sleep(1)

                            # Receive data from the channel
                            print(channel.recv(1024).decode('utf-8', 'ignore'))

                            # Send data to the channel
                            channel.send("exit\n".format(port))
                            time.sleep(1)

                            # Receive data from the channel
                            print(channel.recv(1024).decode('utf-8', 'ignore'))

                            # Send data to the channel
                            channel.send("exit\n".format(port))
                            time.sleep(1)

                            # Receive data from the channel
                            print(channel.recv(1024).decode('utf-8', 'ignore'))
                    else:
                        print("%s\t%s\t备选端口存在, 业务不存在\n" % (dev_Ip, lport))

                elif re.search(r'ip address', result, flags=re.M + re.I):

                    if not re.search(r'traffic-statistics enable', result, flags=re.M + re.I):

                        # Send data to the channel
                        channel.send("intf-statistics\n".format(port))
                        time.sleep(1)
                        # Receive data from the channel

                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                        # Send data to the channel
                        channel.send("interface {}\n".format(port))
                        time.sleep(1)
                        # Receive data from the channel

                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                        # Send data to the channel
                        channel.send("traffic-statistics enable\n")
                        time.sleep(1)

                        # Receive data from the channel
                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                        # Send data to the channel
                        channel.send("exit\n".format(port))
                        time.sleep(1)

                        # Receive data from the channel
                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                        # Send data to the channel
                        channel.send("exit\n".format(port))
                        time.sleep(1)

                        # Receive data from the channel
                        print(channel.recv(1024).decode('utf-8', 'ignore'))

                else:
                    print("%s\t%s\t主选端口存在, 业务不存在\n" % (dev_Ip, port))

            # Send data to the channel
            channel.send("end\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

            # Send data to the channel
            channel.send("write\n")
            time.sleep(1)

            # Receive data from the channel
            print(channel.recv(1024).decode('utf-8', 'ignore'))

        # Close the channel
        channel.close()

        # Close this SSHClient and its underlying Transport.
        client.close()


if __name__ == '__main__':
    ConfigSR()
