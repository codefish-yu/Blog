import json

from django.http import JsonResponse
from topic.models import Topic
from tools.logging_check import logging_check
from .models import Message


from django.shortcuts import render

# Create your views here.

#前提：会从url中传来topic_id



@logging_check('POST')
#留言功能接口
def message(request,topic_id):
    # 发表留言/回复
    if request.method == 'POST':
        #从前端传来用户提交的json串,json串中包含的内容由后端提给前端
        json_str = request.body
        json_obj = json.loads(json_str.decode())
        content = json_obj.get('parent_id',0)
        #parent_id用于区分信息是留言(parent_id=0)还是回复(parent_id指向留言id)，为后面使用大团员数据结构做铺垫，也是之前就和前端约定好
        parent_id = json_obj.get('parent_id',0)
        #TODO 参数检查
        #publisher关联的是userprofile表
        #topic关联的是Topic表

        #可能博主在那边删文章，访客还在那评论，所以得提交时得验证topic是否存在
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            result = {'code':40101,'error':'No topic'}
            return JsonResponse(result)

        #创建对象
        Message.objects.create(content=content,parent_message=parent_id,
                               publisher=request.user,
                               topic = topic)
        #通知前端创建成功，不需要返回啥
        return JsonResponse({'code':200})

    #看留言和回复，从数据表对象中取出需要展示的内容返回给前端
    # /v1/message/topic_id
    if request.method == 'GET':
        all_m  = Message.objects.filter(topic_id=int(topic_id))#all_m是[{..},{...}...]
        all_list = []
        for m in all_m:
            d = {}
            d['id'] = m.id
            d['content'] = m.content
            d['parent_message'] = m.parent_message
            d['publisher'] = m.publisher.username
            d['topic'] = m.topic.id
            all_list.append(d)

        return JsonResponse({'code':200,'data':all_list})