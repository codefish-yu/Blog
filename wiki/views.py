from django.http import JsonResponse
from user.models import UserProfile
import requests
import redis

def test(request):
    r = redis.Redis(host='127.0.0.1',port=6379,db=0)
    while True:
        try:
            with r.lock('123',blocking_timeout=3) as lock:
                #m每次打开浏览器(相当于有个用户请求)对score字段进行+1操作
                u = UserProfile.objects.get(username='123')
                u.score += 1
                u.save()
            break
        except Exception as e:
            print('Lock failed')

    return JsonResponse({'code':200,'data':{}})
