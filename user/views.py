import hashlib
import json
from django.http import JsonResponse
from django.shortcuts import render
from wtoken.views import make_token
from tools.logging_check import logging_check
from .models import UserProfile

# Create your views here.

@logging_check('PUT')#将过滤传过来的请求类型的函数写成装饰器，避免重复书写
def users(request,username=None):#传过来的username是POST/PUT请求时要求前端从url中传过来的

    if request.method == 'GET':
        # 拿数据
        # 拿单个用户数据
        users = UserProfile.objects.filter(username=username)

        if username:
            # 如果有querystring[?nickname=1]传进来
            #先判断前端传过来的querystring的字段在我的数据范围内(因为他可以随意传)
            # 因为username是这个表的主键，有且只有一个，而且拿出来的queryset数据外面是列表
            user = users[0]
            if request.GET.keys():#如果有querystring,拿这个用户的自定数据
                data = {}
                for k in request.GET.keys():
                    if hasattr(user,k):
                        #过滤字段，密码肯定是不能给的
                        if k == 'password':
                            continue
                        #拿querystring对应的字段的值
                        v = getattr(user,k)
                        data[k] = v
                res = {'code':200,'username':username,'data':data}
            else:#如果无querystring,拿这个用户的所有数据

                res = {'code':200,
                       'username':username,
                       'data':{'nickname':user.nickname,'sign':user.sign,'info':user.info,'avatar':str(user.avatar)}}
            return JsonResponse(res)

        else:#前端的url中没有用户名传进来,拿所有用户数据
            # 定义返回的数据格式:user = {'code': 200,'data': {'nickname': nickname, 'sign': sign, 'info': info}}
            all_users = UserProfile.objects.all()#返回的是类字典对象
            #将单个用户的字典类型数据放到这个大列表容器中
            users_data = []
            for user in all_users:
                #用字典装每个用户的数据
                dic = {}
                dic['nickname'] = user.nickname
                dic['username'] = user.username
                dic['sign'] = user.sign
                dic['info'] = user.info
                users_data.append(dic)

            res = {'code':200,'data':users_data}
            return JsonResponse(res)


    elif request.method == 'POST':
        # 创建用户
        #创建用户需要做的事情:1取出浏览器发过来的信息２验证用户名是否存在等用户相关３信息正确后创建用户４给用户发门票token让他下次来不用在验证
        #前端设置的content_type=json,此时不能从表单中拿数据(form中是form)，需要用request.body拿数据
        json_str = request.body
        if not json_str:
            #code的编码的意义都是团队内部自己定
            result = {'code': 10102, 'error': 'Please give me data~'}
            return JsonResponse(result)
        # 将json串(是字节串)先转为字符串，再转为Python对象
        json_obj = json.loads(json_str.decode())
        # get()方法取字典值
        username = json_obj.get('username')
        email = json_obj.get('email')
        if not username:
            # 返回给一个异常
            result = {'code': 10101, 'error': 'Please give me username~'}
            return JsonResponse(result)
            # 注册成功发个门票token
        # TODO 检查Json dict 中的key 是否存在
        #取出浏览器传过来的两个密码
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if password_1 != password_2:
            result = {'code': 10103, 'error': 'The password id error !'}
            return JsonResponse(result)
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10104, 'error': 'The username is already existed!'}
            return JsonResponse(result)


        # 生成散列密码
        # 用md5生成散列密码,生成散列密码的语法
        # import hashlib
        #１．从前端或者浏览器传过来的数据中取密码
        # password = request.POST.get('password') / password = json_obj.get('password')
        # password += 'salt'  #加盐
        # #2.创建md5对象
        # m5 = hashlib.md5()
        # m5.update(password.encode())
        # pw_md5 = m5.hexdigest()
        pm = hashlib.md5()
        pm.update(password_1.encode())

        # 创建用户
        #由于username是主键，有可能别人注册时别人比你跑的快在你之前注册了这个用户名，会报错，所以一定要try一下
        try:
            UserProfile.objects.create(username=username, password=pm.hexdigest(), nickname=username, email=email)
        except Exception as e:
            print('---create error---')
            #自己捕获了一场，要打印出来告诉自己
            print(e)
            result = {'code': 10105, 'error': 'The username is already existed !!'}
            return JsonResponse(result)

            #后端发门票（生成token）,需要传入用户名和过期时间，token的函数单独定义
        token = make_token(username,3600*24)
        result = {'code':200,'data':{'token':token.decode()},
                  'username':username}
        #通过装饰器从token中取出来的username需要和传进来的username一致，才真正是本人
        return JsonResponse(result)


    elif request.method == 'PUT':
        # 更新    http://127.0.0.1:8000/v1/users/username
        #put是更新用户信息，肯定只能更新单个用户的信息，全两更新就乱套了，所以必须得传入username
        if not username:
            res = {'code':10108,'error':'Must be give me username !!'}
            return JsonResponse(res)

        json_str = request.body
        #TODO　空body判断
        json_obj = json.loads(json_str.decode())
        nickname = json_obj.get('nickname')
        sign = json_obj.get('sign')
        info = json_obj.get('info')
        #更新
        #将原先的查询用户这一段取代掉，取而代之的使用装饰器从门票token中取出的，通过request这个参数传过来的username
        # users = UserProfile.objects.filter(username=username)
        # #主键，肯定只有一个
        # user = users[0]

        #从装饰器中传过来的request中取出token对应的user
        user = request.user#这个用户也是个数据行
        #当前请求，token用户　修改自己的数据
        if user.username != username:#后面的username是url中传过来的
            result = {'code':10109,'error':'The username is error !'}
            return JsonResponse(result)

        #校验下用户传过来的东西和原来是有变化的，不然不触发更新，这样会少很多无效的update
        to_update = False
        if user.nickname != nickname:
            to_update = True
        if user.info != info:
            to_update = True
        if user.sign != sign:
            to_update = True

        if to_update:
            #做更新
            # 方法１：
            #1.查：通过get()/filter()[索引]得到要修改的实例对象；
            #2.改：通过对象.属性的方式修改数据
            #3.保存：对象.save()

            # 方法２：
            # 1.查：books = Books.objects.filter(id__gt=3)
            # 2.更新: books.update(属性=值)
            user.sign = sign
            user.nickname = nickname
            user.info = info
            user.save()
        return JsonResponse({'code':200,'username':username})


#由于django的原因，处理头像上传(media文件)这个更新操作不能放在PUT中,需要用POST，这里前端其实也是拿表单提的
#用一个新的视图函数专门负责头像的上传
#上传头像也需要用装饰器判断token和请求类型是否符合
@logging_check('POST')
def users_avatar(request,username):#这个username用于给谁传头像
    if request.method != 'POST':
        result = {'code':10110,'error':'Please use POST'}
        return JsonResponse(result)

    user = request.user
    if user.username != username:#很显然有不法之徒来搞我们,a的门票不恩嗯改b的头像
        result = {'code':10109,'error':'The username is error !'}
        return JsonResponse(result)

    #图片存之前不做比较，直接存，因为要调原来的数据还得用open一下原来的磁盘路径
    #前端收到avatar之后传输给后端，这里不是用json或url的方式，而是通过HTTPREQUEST.FILES的方式拿
    user.avatar = request.FILES['avatar']
    user.sava()
    return JsonResponse({'code':200,'username':username})


    #
    # return JsonResponse({'code': 200, 'data': {}})















