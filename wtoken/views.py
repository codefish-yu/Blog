import hashlib
import json
import time
from user.models import UserProfile

import jwt
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

def tokens(request):
    #前端请求格式{'username':'xxx','password':'yyy'}
    #后端响应格式{'code':200,'username':'asc','data':{'token':'zzzzzz'}}#他过来登录是他带着token过来，然后我给他发门票啊

    if request.method !='POST':
        result = {'code':20101,'error':'Please use POST'}
        return JsonResponse(request)
    json_str = request.body
    #TODO 检查参数是否存在
    json_obj = json.loads(json_str.decode())
    username = json_obj.get('username')

    password = json_obj.get('password')
    #找用户
    users = UserProfile.objects.filter(username=username)
    if not users:
        result = {'code':20102,'error':'The username or password is error!'}
        return JsonResponse(result)
    user = users[0]

    pm = hashlib.md5()
    pm.update(password.encode())
    if user.password != pm.hexdigest():
        result = {'code':20103,'error':'The username or password is error!!'}
        return JsonResponse(result)

    #发门票token
    token = make_token(username,3600*24)
    result = {'code':200,'username':username,'data':{'token':token.decode()}}
    return JsonResponse(result)



 #生成token的具体函数
def make_token(username,exp):
    #公司给出一个key
    key = '123456ab'
    now_t = time.time()
    #调用jwt包时payload需要手动定义，一般payload会放username和过期时间
    payload = {'username':username,'exp':int(now_t+exp)}
    #阀门票时候的语法：jwt.encode({payload},key,algorithm)
    return jwt.encode(payload,key,algorithm='HS256')
