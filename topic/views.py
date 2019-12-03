import json

from django.http import JsonResponse
from django.shortcuts import render
from tools.logging_check import logging_check, get_user_by_request
from .models import Topic
from user.models import UserProfile
from .models import Topic
from message.models import Message



# Create your views here.

#发表博客必须是登录状态，用装饰器验证
@logging_check('POST','DELETE')
def topics(request,author_id):#author_id从url传进来的，url是前端给过来的
    # 创建博客的代码段
    if request.method == 'POST':
        #发表博客(属于创建资源，使用POST)
        #在装饰器中封装了将token中取出的user的数据行赋值到request.user中的代码
        #既然调用了装饰器，在装饰器返回被装饰函数成功的情况下，可做以下操作
        #用author变量绑定该登录用户对象
        author = request.user
        if author.username != author_id:
            result = {'code':30101,'error':'The author is error !'}
            return JsonResponse(result)
        #从请求提中取出前端传过来的json_str
        json_str = request.body
        json_obj = json.loads(json_str.decode())#因为传来的是json_str,需要转成json对象
        #从json对象中取出
        title = json_obj.get('title')
        #注意xss攻击,前端(用户)可以传过来带css标签的title（这种现象只存在于title中)
        import html
        title = html.escape(title)

        category = json_obj.get('category')
        if category not in ['tec','no-tec']:
            result = {'code':30102,'error':'Thanks,your category is error !!'}
            return JsonResponse(result)
        limit = json_obj.get('limit')
        if limit not in ['private','public']:
            result = {'code':30103,'error':'Thanks,your limit is error !!'}
            return  JsonResponse(result)
        #带样式的文章内容
        content = json_obj.get('content')
        #纯文本的文章内容，用于做文章简介的切片
        content_text = json_obj.get('content_text')
        introduce = content_text[:30]
        #创建topic
        #author是个外键，关联着userprofile表，创建对象时补充上author有啥用?
        Topic.objects.create(title=title,limit=limit,category=category,content=content,
                             introduce=introduce,author=author)

        result = {'code':200,'username':author.username}
        return JsonResponse(result)

    #获取博客文章(有分为根据category获取和全量获取) 和从列表页进入文章详情页　的代码段
    #127.0.0.1:8000/v1/topics/yutaixin或
    #127.0.0.1:8000/v1/topics/yutaixin/category=tec|no-tec或
    #127.0.0.1:8000/v1/topics/yutaixin/t_id=3
    if request.method =='GET':
        # 从数据库拿出前端需要的author对象
        authors = UserProfile.objects.filter(username=author_id)

        # 没有传用户
        if not authors:
            result = {'code': 30107, 'error': 'The author is not existed !'}
            return JsonResponse(result)

        # 当前被访问的博主
        # 一定要记住，过滤出来的是一个queryset列表形式套着字典，要将这个字典取出来
        author = authors[0]

        # 访问者,可能登录了也可能未登录
        # 用一个函数确认访问者的身份，该函数需要返回访客身份，这可以封装成装饰器过滤以下写在loggingcheck.py中
        visitor = get_user_by_request(request)  # 接受NONE或者该用户字典
        visitor_username = None

        # 判断用户是获取博客文章还是从列表也进入文章详情页
        #获取博客文章的url是没有查询字符串的，从列表页进入文章详情页有t_id这个查询字符串
        t_id = request.GET.get('t_id')
        # 有querystring,是进详情页时
        if t_id:#
            t_id = int(t_id)
            # 这时前端会传过来一个url(你和他约定好的),然后你跟据这个url来拿数据，返回给前端
            is_self = False
            # 如果博主
            if author_id == visitor.username:
                is_self = True
                #从Topic数据库中取该博主的该文章
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    print('----get t_id error-----')
                    print(e)
                    result = {'code':30108,'error':'get t_id error'}
                    return JsonResponse(result)

            # 如果是游客或访客
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id,limit='public')
                except Exception as e:
                    print('----get t_id error-----')
                    print(e)
                    result = {'code': 30109, 'error': 'No topic visitor'}
                    return JsonResponse(result)

            res = make_topic_res(author, author_topic,is_self)
            return JsonResponse(res)

        # 无querystring,获取用户文章列表数据
        else:
            #/v1/topic/guoxiaonao - 拿guoxiaonao的所有文章(分出访客和博主的权限)
            #1.访问当前博客的访问者visitor
            #2.当前被访问的博客的博主author，用token辨别身份
            #在做一个功能时，前提你需要知道哪些参数？１路由２返回给前端的格式３

            #如果博主
            if visitor:
                visitor_username = visitor.username

            # 按种类筛选,url:/v1/topics/yutaixin?category=tec|no-tec
            category = request.GET.get('category')
            if category in ['tec','no-tec']:
                if author_id == visitor_username:#避免有人搞我
                    author_topics = Topic.objects.filter(author_id=author_id,category=category)
                else:
                    # 访客访问他人博客，只返回公开权限和对应category的文章
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public',category=category)
                    # 抽象个方法，生成大字典
            # 全量不分种类筛选
            else:
                # 如果是博主访问自己的博客,文章全都返回
                #先判断访问者是否是博主本人,看前端传过来的author_id是否和token中取出来的username是否相等
                if author_id == visitor_username:#避免有人搞我
                    author_topics = Topic.objects.filter(author_id=author_id)
                else:
                    #访客访问他人博客，只返回公开权限的文章
                    author_topics = Topic.objects.filter(author_id=author_id,limit='public')
                    #抽象个方法，生成大字典
            res = make_topics_res(author,author_topics)
            return JsonResponse(res)

    #删除博主自己的文章,真删除
    #只有博主才能删，所以要验证身份
    if request.method =='DELETE':

        # 检查这个人带过来的token是不是自己的，防止有人想搞我
        user = request.user
        if user.username != author_id:
            result = {'code':30105,'error':'Your author_id is error !!'}
            return JsonResponse(result)

        # url传过来的查询字符串为topic_id=3,响应{'code':200}
        topics_id = request.GET.get('topic_id')
        if not topics_id:
            result  = {'code':30106,'error':'The Topics_id is not existed !!'}
            return JsonResponse(result)

        #因为表的主键是Int型，而传过来的querystring值是string
        topics_id = int(topics_id)
        try:
            topic = Topic.objects.get(id=topics_id)
        except Exception as e:
            print('-----topic----delete---error')
            print(e)
        topic.delete()
        res = {'code':200}
        return JsonResponse(res)

#生成文章列表返回值,返回值的格式是之前就约定好的,
# {‘code’:200,’data’:{‘nickname’:’abc’, ’topics’:[{‘id’:1,’title’:’a’,
# ‘category’: ‘tec’, ‘created_time’: ‘2018-09-03 10:30:20’, ‘introduce’:
# ‘aaa’, ‘author’:’abc’}]}}
def make_topics_res(author,author_topics):
    res = {'code':200,'data':{}}
    res['data']['nickname'] = author.nickname
    res['data']['topics'] = []
    for topic in author_topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['introduce'] = topic.introduce
        d['category'] = topic.category
        #datetimefielddjango对象不能被json识别，得用下面的方式转化一下
        d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')#ceated_time是个datatime对象，json转化不了
        d['author'] = author.nickname
        res['data']['topics'].append(d)
    return res

# 要返回的数据格式:{"code": 200,"data": {"nickname": "guoxiaonao",
    # "title": "我的第一次","category": "tec",
    # "created_time": "2019-06-03","content": "<p>我的第一次,哈哈哈哈哈<br></p>",
    # "introduce": "我的第一次,哈哈哈哈哈","author": "guoxiaonao",
    # "next_id": 2,"next_title": "我的第二次","last_id": null,
    # "last_title": null,
    # "messages": [...
def make_topic_res(author,author_topic,is_self):
    #传进来的author代表UserFILE表的实例，author_topic代表TOPIC表的实例,xxx代表Ｍessage表的实例
    # 通过加的is_self这个参数来代表权限

    #获取上下篇文章的id和title
    #博主访问自己的博客
    if is_self:
        #大于当前文章id的第一个
        next_topic = Topic.objects.filter(id__gt=author_topic.id,author=author).first()#author是topic表的外键，绑定的是userprofile表的一个实例
        #小于当前文章id的最后一个
        last_topic = Topic.objects.filter(id__lt=author_topic.id,author=author).last()
    #访客访问博主博客,只能拿公开文章
    else:
        # 大于当前文章id的第一个
        next_topic = Topic.objects.filter(id__gt=author_topic.id,author=author,limit='public').first()
        # 小于当前文章id的最后一个
        last_topic = Topic.objects.filter(id__lt=author_topic.id,author=author,limit='public').last()

    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None
    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None

    res = {'code':200,'data':{}}
    res['data']['title'] = author_topic.title
    res['data']['nickname'] = author.nickname
    res['data']['category'] = author_topic.category
    res['data']['content'] = author_topic.content
    res['data']['introduce'] = author_topic.introduce
    res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M%S')
    res['data']['author'] = author.nickname
    res['data']['next_id'] = next_id
    res['data']['next_title'] = next_title
    res['data']['last_id'] = last_id
    res['data']['last_title'] = last_title

    #留言返回
    #获取当前文章的所有留言
    all_message = Message.objects.filter(publisher=author).order_by('-created_time')
    m_count = 0#这里留言中回复也算＋１
    #引入大团员数据结构模型
    #将所有留言放到一个容器中
    msg_list = []
    #将回复放到一个容器中
    reply_home = {}
    for message in all_message:#在数据表中不分回复和留言
        #messages计数
        m_count += 1
        #判断是留言还是回复,分别放入不同的容器
        #如果当前信息有parent_message的值，说明是回复
        if message.parent_message:
            reply_home.setdefault(message.parent_message,[])#构建字典,如果已经有这个键，则不构建
            reply_home[message.parent_message].append({'msg_id':message.id,#回复的id
                                                       'content':message.content,
                                                       'publisher':message.publisher.nickname,#访客昵称
                                                       'publisher_avatar':str(message.publisher.avatar),#访客头像
                                                       'created_time':message.created_time.strftime('%Y-%m-%d %H:%M:%S')
                                                       })



        #否则是留言
        else:
            msg_list.append({'id':message.id,
                             'content':message.content,
                             'publisher':message.publisher.nickname,
                             'publisher_avatar':str(message.publisher.avatar),
                             'created_time':message.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                             'reply':[]
                             })

    #关联留言和回复,如果留言id在装回复的这个字典的键中,则将这个键对应的值(孩子队伍)放到留言的字典中
    for m in msg_list:
        if m['id'] in reply_home:
            m['reply']= reply_home[m['id']]

    res['data']['message'] = msg_list
    res['data']['message_count'] = m_count
    return res









