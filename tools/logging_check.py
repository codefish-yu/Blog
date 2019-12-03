
#用于判断是否是PUT请求,有可能传过来是PUT,GET,POST,所以用*methods表示
import jwt
from django.http import JsonResponse
from user.models import UserProfile


TOKEN_KEY = '123456ab'


#检查token
def logging_check(*methods):#此参数程序员决定的请求类型:星号元组形参*args，收集所有位置传参,
    def _logging_check(func):#此参数传入视图函数
        def wrapper(request,*args,**kwargs):#此参数接受用户传来的request类型，真正做事的函数
            #1判断当前请求是否需要校验：
                # ＧＥＴ博客访问用户数据不需要登录也能看
                #ＰＯＳＴ是注册和登录，是用户给出token,不需要校验
                #ＰＵＴ　是用户修改自己的数据，需要检验
            #2需要校验的情况，取出token
            #３校验token:具体是１校验token是否能取出来，２校验用户名　３过期时间
            if not methods:#不进行装饰直接将原函数返回,让原函数的代码自己去判断这个情况
                return func(request,*args,**kwargs)
            else:
                if request.method not in methods:
                    return func(request, *args, **kwargs)

            #２需要检验的情况，取出token
            token = request.META.get('HTTP_AUTHORIZATION')
            if not token:
                result = {'code':20104,'error':'Please login'}
                return JsonResponse(result)
            try:
                res = jwt.decode(token,TOKEN_KEY,algorithms='HS256')
            except Exception as e:
                result = {'code': 20105, 'error': 'Please login'}
                return JsonResponse(result)


            #３到这一步说明能取出token,然后校验token
            # 从解码后的token中取出username，传入到视图函数中和视图函数中的用户名比较
            username = res['username']
            #从数据库中取出这个token对应的用户的信息并付给diango的request对象
            #而且在装饰器中取出user,就省了再视图函数中filter了
            user = UserProfile.objects.get(username=username)
            request.user = user #为啥request对象有user这个属性?

            #将装饰过的视图函数返回回去
            return func(request,*args,**kwargs)
        return wrapper
    return _logging_check

#用于获取发起GET请求的用户的身份(游客，博主，访客)
def get_user_by_request(request):
    #若登录则返回user,没登录返回none
    token = request.META.get('HTTP_AUTHORIZATION')#token从请求头中获取，请求头是访问的用户发出的
    if not token:#用户没登录的情况
        return None
    #用户登录的情况，判断是不是博主本人
    try:
        res = jwt.decode(token,TOKEN_KEY,algorithms='HS256')
    except Exception as e:
        return None

    #如果没报错，则说明是博主，从token中拿出用户名
    username = res['username']
    users = UserProfile.objects.filter(username=username)#这里还是过滤出列表
    if not users:
        return None
    return users[0]


