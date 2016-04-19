#!/usr/bin/env python
#-*- coding:utf-8 -*-
#处理嗅探到的数据包，检测图片、人脸识别
#需安装opencv-python

import re
import zlib
import cv2
from scapy.all import *

#数据包文件，图片储存目录
pictures_directory = "pic_carver/pictures"
faces_directory    = "pic_carver/faces"
pcap_file          = "bhp.pcap"
#人脸识别函数，传入图片路径、文件名
def face_detect(path,file_name):
        #读入文件
        img     = cv2.imread(path)
        #读入人脸识别规则
        cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

        #使用规则检测图片
        rects   = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

        if len(rects) == 0:
                return False

        rects[:, 2:] += rects[:, :2]

    # highlight the faces in the image
    #人脸位置
    for x1,y1,x2,y2 in rects:
        #画出人脸框
        cv2.rectangle(img,(x1,y1),(x2,y2),(127,255,0),2)

    cv2.imwrite("%s/%s-%s" % (faces_directory,pcap_file,file_name),img)

        return True
#传入http报文，返回http头
def get_http_headers(http_payload):

    try:
        # split the headers off if it is HTTP traffic
        #index返回字符串第一位所在引索
        headers_raw = http_payload[:http_payload.index("\r\n\r\n")+2]

        # break out the headers
        #使用正则，返回[(name,value),(name,value)....]列表
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers_raw))
    except:
        return None
    #没有连接类型，则返回None
    if "Content-Type" not in headers:
        return None

    return headers

def extract_image(headers,http_payload):

    image      = None
    image_type = None

    try:
        if "image" in headers['Content-Type']:

            # grab the image type and image body
            image_type = headers['Content-Type'].split("/")[1]
            #去除http头，即使图片数据
            image = http_payload[http_payload.index("\r\n\r\n")+4:]
            #如果进行了压缩
            # if we detect compression decompress the image
            try:
                if "Content-Encoding" in headers.keys():
                    if headers['Content-Encoding'] == "gzip":
                        image = zlib.decompress(image,16+zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == "deflate":
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None,None

    return image,image_type
#处理数据包，进行数据重组
def http_assembler(pcap_file):

    carved_images   = 0
    faces_detected  = 0

    a = rdpcap(pcap_file)
    #会话分割，得到会话列表
    sessions      = a.sessions()

    for session in sessions:

        http_payload = ""
        #迭代一次会话的数据包，进行负载重组，得到http报文
        for packet in sessions[session]:

            try:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:

                    # reassemble the stream into a single buffer
                    http_payload += str(packet[TCP].payload)

            except:
                pass
        #调用函数，返回http头
        headers = get_http_headers(http_payload)

        if headers is None:
            continue
        #检测图片传输
        image,image_type = extract_image(headers,http_payload)
        #储存图片
        if image is not None and image_type is not None:

            # store the image
            file_name = "%s-pic_carver_%d.%s" % (pcap_file,carved_images,image_type)
            fd = open("%s/%s" % (pictures_directory,file_name),"wb")
            fd.write(image)
            fd.close()

            carved_images += 1

            # now attempt face detection
            try:
                #尝试人脸识别
                result = face_detect("%s/%s" % (pictures_directory,file_name),file_name)

                if result is True:
                    faces_detected += 1
            except:
                pass


    return carved_images, faces_detected


carved_images, faces_detected = http_assembler(pcap_file)

print "Extracted: %d images" % carved_images
print "Detected: %d faces" % faces_detected
