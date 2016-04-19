#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import socket
import threading

#漂亮的十六进制导出函数
#http://code.activestate.com/recipes/142812-hex-dumper/
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    #如果采用ucs-2编码，即每两个字节表示一个字符，表示的字符有限
    for i in xrange(0, len(src), length):
        #按16字节分割数据流
        s = src[i:i + length]
        #ord()给定字符，ASCII数值，或者Unicode数值
        #digits为所占宽度
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))

    print b'\n'.join(result)


#接收数据函数
def receive_from(connection):
    buffer = ""

    # We set a 2 second time out depending on your
    # target this may need to be adjusted
    connection.settimeout(10)
    #两秒的超时
    try:
        # keep reading into the buffer until there's no more data
        # or we time out
        while True:
            data = connection.recv(4096)

            if not data:
                break

            buffer += data


    except:
        pass
    #返回数据
    return buffer

#修改客户端数据
# modify any requests destined for the remote host
def request_handler(buffer):
    # perform packet modifications
    return buffer

#修改远程主机数据
# modify any responses destined for the local host
def response_handler(buffer):
    # perform packet modifications
    return buffer

#代理处理主函数
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # connect to the remote host
    #连接至远程主机

    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # receive data from the remote end if necessary
    #是否先接受远程主机数据，转发给客户端
    if receive_first:

        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)

        # if we have data to send to our local client send it
        if len(remote_buffer):
            print "[<==] Sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)

    # now let's loop and reading from local, send to remote, send to local
    # rinse wash repeat
    #开始转发数剧
    while True:

        # read from local host
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print "[==>] Received %d bytes from localhost." % len(local_buffer)
            hexdump(local_buffer)

            # send it to our request handler
            local_buffer = request_handler(local_buffer)

            # send off the data to the remote host
            remote_socket.send(local_buffer)
            print "[==>] Sent to remote."


        # receive back the response
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print "[<==] Received %d bytes from remote." % len(remote_buffer)
            hexdump(remote_buffer)

            # send to our response handler
            remote_buffer = response_handler(remote_buffer)

            # send the response to the local socket
            client_socket.send(remote_buffer)

            print "[<==] Sent to localhost."

        # if no more data on either side close the connections
        #如果没有数据，关闭套接字
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print "[*] No more data. Closing connections."

            break

#服务器主体
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #本地监听
        server.bind((local_host, local_port))
    except:
        print "[!!] Failed to listen on %s:%d" % (local_host, local_port)
        print "[!!] Check for other listening sockets or correct permissions."
        sys.exit(0)

    print "[*] Listening on %s:%d" % (local_host, local_port)

    server.listen(5)
    #接受客户端连接，多线程处理
    while True:
        client_socket, addr = server.accept()

        # print out the local connection information
        print "[==>] Received incoming connection from %s:%d" % (addr[0], addr[1])

        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

#主函数
def main():
    # no fancy command line parsing here
    if len(sys.argv[1:]) != 5:
        print "Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]"
        print "Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)

    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # this tells our proxy to connect and receive data
    # before sending to the remote host
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False


    # now spin up our listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


main()
