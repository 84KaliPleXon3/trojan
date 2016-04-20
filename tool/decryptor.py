#!/usr/bin/python
#-*- coding:utf-8 -*-
#解密IE自动化窃取的数据

import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
private_key = "###PASTE PRIVATE KEY HERE###"

#导入私钥
rsakey = RSA.importKey(private_key)
rsakey = PKCS1_OAEP.new(rsakey)

chunk_size= 256
offset = 0
decrypted = ""

#进行base64解密
encrypted = base64.b64decode(encrypted)
#使用私钥进行256数据块解密
while offset < len(encrypted):
    decrypted += rsakey.decrypt(encrypted[offset:offset+chunk_size])
    offset += chunk_size

plaintext = zlib.decompress(decrypted)
print plaintext
