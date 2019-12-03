from django.conf.urls import url
from . import views

urlpatterns = [
    #http://127.0.0.1:8000/v1/users用于注册的路由接口，post请求
    url(r'^$',views.users),
    # http://127.0.0.1:8000/v1/users/<username> 用于获取单个用户的数据
    url(r'^/(?P<username>\w{1,11})$',views.users),
    # http://127.0.0.1:8000/v1/users/<username>/avatar#标准的restfullapi
    url(r'^/(?P<username>\w{1,11})/avatar$',views.users_avatar)


]