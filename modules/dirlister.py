#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

def run(**args):
    files=[]
    print '[*] In dirlist module.'
    for r,d,f in os.walk("."):
        dir=r.split('/')[-1]
        files.append(dir+'\n')
        for file in f:
            path="%s/%s"%(r,file)
            files.append(path)
    return str(files)
