# -*- coding: utf-8 -*-

with open("D:\\python\\NetWork\\H3C\\device.txt") as f:
    for line in f:
        line.strip()
        info = line.split()
        name = info[0]
        vlan = info[1]
        ip = info[2]
        with open(
            "D:\\python\\NetWork\\H3C\\{}_{}_{}.txt".format(name, vlan, ip), "w+"
        ) as nf:
            config = """
 sysname {0}_{1}_{2}
#
 lldp global enable
#
 password-recovery enable
#
vlan 1
#
vlan {1}
#
vlan 4020
des management
#
 stp global enable
 stp bpdu-protection
#
interface Vlan-interface4020
 des management
 ip address {2} 255.255.255.0
#
interface range GigabitEthernet 1/0/1 to GigabitEthernet 1/0/23
 port access vlan {1}
#
interface GigabitEthernet1/0/24
 port link-mode bridge
 port link-type trunk
 undo port trunk permit vlan 1
 port trunk permit vlan {1} 2290 2710 2720 2730 2740 2750 2760 2770 2780 2790 2800 2810 2820 2830 2840 2850 2860 2870 4000 4020
 poe enable
#
interface range Ten-GigabitEthernet 1/0/25 to Ten-GigabitEthernet 1/0/27
 des JieRu55
 port link-mode bridge
 port access vlan {1}
#
interface Ten-GigabitEthernet1/0/28
 des HeXin76
 port link-mode bridge
 port link-type trunk
 undo port trunk permit vlan 1
 port trunk permit vlan {1} 2290 2710 2720 2730 2740 2750 2760 2770 2780 2790 2800 2810 2820 2830 2840 2850 2860 2870 4000 4020
 poe enable
#
line class vty
 user-role network-operator
#
line vty 0 63
 authentication-mode scheme
 idle-timeout 5 0
 protocol inbound ssh
 user-role network-operator
#
local-user h3c class manage
 password simple H3c@123456
 service-type ssh  https terminal
 authorization-attribute user-role network-admin
 authorization-attribute user-role network-operator
 quit
#
undo ip http enable
undo telnet server enable
ssh server enable
#
ssh2 algorithm cipher aes256-ctr aes128-gcm aes192-ctr aes256-gcm
#
 ip route-static 0.0.0.0 0 20.0.0.254
#
return
sa f
""".format(
                name, vlan, ip
            )
            nf.write(config)
