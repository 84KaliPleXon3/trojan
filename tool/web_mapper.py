#!/usr/bin/python
#-*- coding:utf-8 -*-
#开源web应用爬虫

import Queue
import threading
import os
import urllib2
#总线程数
threads = 10
#目标网站
target = "http://www.hackerl.com"
directory = "/root/folder/project/Web/FOUR"
#需要查找的文件类型
filters = [".jpg", ".gif", "png", ".css"]

#chdir切换当前工作目录
os.chdir(directory)
#构建Queue对象
web_paths = Queue.Queue()

#os.walk返回当前目录下的所有信息，[(路径，所有目录，所有文件)，.....]
for r, d, f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        #如果路径以 . 开头
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)

#爬取文件
def test_remote():
    while not web_paths.empty():
        #取出对象
        path = web_paths.get()
        #请求网址
        url = "%s%s" % (target, path)
        #发送请求
        request = urllib2.Request(url)

        try:
            response = urllib2.urlopen(request)
            content = response.read()
            #打印响应
            print "[%d] => %s" % (response.code, path)

            response.close()

        except urllib2.HTTPError as error:
            # print "Failed %s" % error.code
            pass

#开启多线程
for i in range(threads):
    print "Spawning thread: %d" % i
    t = threading.Thread(target=test_remote)
    t.start()
