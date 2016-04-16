#!/usr/bin/python
#-*- coding:utf-8 -*-

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
	transport = client.get_transport()
	transport.set_keepalive(100)
	while True:
		try:
			ssh_session=transport.open_session()
			if ssh_session.active:
				command=raw_input("command:")
				ssh_session.exec_command(command)
				print ssh_session.recv(1024)
			else:
				ssh_session.close()
				sys.exit(0)
		except KeyboardInterrupt:
				ssh_session.close()
				sys.exit(0)

ssh_command(sys.argv[1])
