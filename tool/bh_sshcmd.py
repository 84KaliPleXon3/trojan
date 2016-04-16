#!/usr/bin/python
#-*- coding:utf-8 -*-
#连接远程ssh服务器，执行命令
import paramiko
import subprocess
import sys

def ssh_command(ip,user=None,passwd=None):
	client=paramiko.SSHClient()
	client.load_host_keys('/root/.ssh/known_hosts')
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		if user and passwd:
			client.connect(ip,username=user,password=passwd)
		else:
			client.connect(ip)
	except:
		print('connect failed!')
	while True:
		try:
			command=raw_input("command:")
			stdin, stdout, stderr = client.exec_command(command)
			response=''
			for line in stdout.readlines():
				response+=line.encode('utf-8')
			print(response)
		except KeyboardInterrupt:
			client.close()
			sys.exit(0)

ssh_command(sys.argv[1])
