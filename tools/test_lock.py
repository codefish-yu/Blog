'''
模拟３０个请求，发给：http://127.0.0.1:8000/test/
                  http://127.0.0.1:8001/test/
'''

import random
from threading import Thread
#向网站发请求的模块
import requests

#线程事件函数,随机向８０００或８００１发请求
def get_request():
    url = 'http://127.0.0.1:8000/v1/test/'
    url2 = 'http://127.0.0.1:8001/v1/test/'
    get_url = random.choice([url,url2])
    #模拟向服务器请求url资源
    requests.get(get_url)

t_list = []
for i in range(30):
    t = Thread(target=get_request)
    t_list.append(t)
    #让线程同时启动
    t.start()

#同时回收
for t in t_list:
    t.join()


