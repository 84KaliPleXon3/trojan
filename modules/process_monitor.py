#!/usr/bin/python
#-*- coding:utf-8 -*-

import win32con
import win32api
import win32security
import wmi
import sys
import os

#获取进程开启的权限
def get_process_privileges(pid):
    try:
        #根据进程id，获得目标进程的句柄
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,pid)
        #打开进程的令牌
        htok = win32security.OpenProcessToken(hproc,win32con.TOKEN_QUERY)
        #获取权限列表，记录了每个权限权限是否启用
        privs = win32security.GetTokenInformation(htok, win32security.
        TokenPrivileges)

        #迭代每个权限，如果i[1] == 3则为已启用的权限
        priv_list = ""
        for i in privs:
            if i[1] == 3:
                #获得权限名称
                priv_list += "%s|" % win32security.LookupPrivilegeName(None,i[0])
    except:
        priv_list = "N/A"
    return priv_lis
#日志记载
def log_to_file(message):
    fd = open("process_monitor_log.csv", "ab")
    fd.write("%s\r\n" % message)
    fd.close()
    return

#写入日志头
log_to_file("Time,User,Executable,CommandLine,PID,Parent PID,Privileges")

#初始化WMI接口
c = wmi.WMI()

#创建进程创建事件的监视器
process_watcher = c.Win32_Process.watch_for("creation")

while True:
    try:
        #从监视器得到进程创建事件的信息
        new_process = process_watcher()

        #获得启动进程者
        proc_owner  = new_process.GetOwner()
        proc_owner  = "%s\\%s" % (proc_owner[0],proc_owner[2])
        create_date = new_process.CreationDate
        executable  = new_process.ExecutablePath
        cmdline     = new_process.CommandLine
        pid         = new_process.ProcessId
        parent_pid  = new_process.ParentProcessId
        privileges = get_process_privileges(pid)
        process_log_message = "%s,%s,%s,%s,%s,%s,%s\r\n" % (create_date,
        proc_owner, executable, cmdline, pid, parent_pid, privileges)
        print process_log_message
        log_to_file(process_log_message)
    except:
        pass
