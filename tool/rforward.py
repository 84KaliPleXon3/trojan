#!/usr/bin/python
#-*- coding:utf-8 -*-
#SSH端口转发

import socket
import paramiko
import threading
import sys
import select
import getopt

forward_port=''
server=''
remote=''

def main():
    global forward_port
    global server
    global remote
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:r:p:",
            ["help","remote=","server=","port="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-s", "--server"):
            server = a
        elif o in ("-r", "--remote"):
            remote = a
        elif o in ("-p", "--port"):
            forward_port = int(a)
        else:
            assert False, "Unhandled Option"
    try:
        server,port=server.split(':')
        remote_host,remote_port=remote.split(':')
    except:
        usage()

    ssh_client(server,port,remote_host,remote_port,forward_port)

def ssh_client(server,port,remote_host,remote_port,forward_port):
    client=paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Connecting to ssh host %s:%s ...') %(server,port)
    try:
        client.connect(server,int(port),username='hackerl',password='liupan')
    except Exception as e:
        print '*** Failed to connect to %s:%s'%(server,port)
        sys.exit(0)

    print('Now forwarding remote port %d to %s:%s')%(forward_port,remote_host,remote_port)
    try:
        reverse_forwarding_tunnel(forward_port,remote_host,remote_port,client.get_transport())
    except KeyboardInterrupt:
        print '[-]Port forwarding stoped!'
        sys.exit(0)

def reverse_forwarding_tunnel(forward_port,remote_host,remote_port,transport):
    transport.request_port_forward('',forward_port)
    while True:
        chan=transport.accept(1024)
        if chan is None:
            continue
        thr=threading.Thread(target=handler,args=(chan,remote_host,remote_port))
        thr.setDaemon(True)
        thr.start()

def handler(chan,host,port):
    sock=socket.socket()
    try:
        sock.connect((host,int(port)))
    except Exception as e:
        print('[FAILED]Forwarding request to %s:%s failed: %r'%(host,port,e))
        return
    print('[+]Connected Tunnel open %r >>> %r >>> %r'%(chan.origin_addr,chan.getpeername(),(host,port)))

    while True:
        r,w,x=select.select([sock,chan],[],[])
        if sock in r:
            data=sock.recv(1024)
            if len(data)==0:
                break
            chan.send(data)
        if chan in r:
            data= chan.recv(1024)
            if len(data)==0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    print('[FINISH]Tunnel closed')

def usage():
    print "SSH FORWARD"
    print "Usage: rforward.py -s ip:port -r ip:port -p port"
    print "Examples: "
    print "bh_sshcmd.py -s 192.168.0.1:22 -r 192.168.0.2:80 -p 8080"
    sys.exit(0)

main()
