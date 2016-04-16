#!/usr/bin/python
#-*- coding:utf-8 -*-
#连接远程ssh服务器，执行命令
import paramiko
import sys

def ssh_command(ip,user,passwd):
	#初始化ssh客户端
	client=paramiko.SSHClient()
	#加载密钥
	client.load_host_keys('/root/.ssh/known_hosts')
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		#如果提供帐号密码
		if user and passwd:
			client.connect(ip,username=user,password=passwd)
		else:
			#密钥连接
			client.connect(ip)
	except:
		print('connect failed!')
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
def main():
	try:
		user=sys.argv[2]
		passwd=sys.argv[3]
	except Exception:
		user=None
		passwd=None
	ssh_command(sys.argv[1],user,passwd)

main()
