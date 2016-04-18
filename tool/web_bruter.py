#!/usr/bin/env python
#-*- coding:utf-8 -*-
#暴力破解网站目录和文件位置

import urllib2
import urllib
import threading
import Queue

threads = 5
target_url = "http://www.nczkevin.com"
wordlist_file = "/root/asd.txt"  # from SVNDigger
#恢复位置
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"

#生成字典
def build_wordlist(wordlist_file):
    # read in the word list
    #打开字典文件
    fd = open(wordlist_file, "rb")
    #返回每一行的列表
    raw_words = fd.readlines()
    fd.close()
    #是否找到恢复点
    found_resume = False
    words = Queue.Queue()
    #开始初始化Queue
    for word in raw_words:
        #去除末尾空格符
        word = word.rstrip()
        #如果需要恢复
        if resume is not None:
            #如果找到了恢复点，开始加入Queue
            if found_resume:
                words.put(word)
            else:
                #如果当前word为恢复点
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from: %s" % resume

        else:
            words.put(word)
    #返回Queue对象
    return words

#破解函数
def dir_bruter(word_queue,extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()
        #需要尝试的列表
        attempt_list = []

        # check if there is a file extension if not
        # it's a directory path we're bruting
        #是目录还是文件
        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)

        #如果需要拓展
        # if we want to bruteforce extensions
        if extensions:
            for extension in extensions:
                attempt_list.append("%s%s" % (attempt, extension))

        # iterate over our list of attempts        
        for brute in attempt_list:
            #quote将网址中的特殊字符格式化，以传输
            url = "%s%s" % (target_url, urllib.quote(brute))

            try:
                #设置http头
                headers = {}
                headers["User-Agent"] = user_agent
                #构造http请求
                r = urllib2.Request(url, headers=headers)
                #发送请求
                response = urllib2.urlopen(r)
                #避免网站重定向不存在的页面到另一页面
                if response.geturl() == url:
                    if len(response.read()):
                        print "[%d] => %s" % (response.code, url)

            except urllib2.HTTPError, e:

                if e.code != 404:
                    print "!!! %d => %s" % (e.code, url)

                pass

#获得返回的字典Queue对象
word_queue = build_wordlist(wordlist_file)
extensions = None
#开启多线程破解
for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue,extensions,))
    t.start()
