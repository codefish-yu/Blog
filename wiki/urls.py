"""wiki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    #http:127.0.0.1:8000/v1/test/
    url(r'^v1/test',views.test),
    # http://127.0.0.1:8000/v1/user用于用户模块的接口
    url(r'^v1/users',include('user.urls')),
    # http://127.0.0.1:8000/v1/tokens用于登录的路由接口，也是post请求，重复了，所以创建一个新的应用
    url(r'^v1/tokens',include('wtoken.urls')),
    # http://127.0.0.1:8000/v1/topics用于进入博客的接口
    url(r'^v1/topics',include('topic.urls')),
    # http://127.0.0.1:8000/v1/messages用于博客留言的接口
    url(r'^v1/messages',include('message.urls'))

]

#绑定media_url 和　media_root,需要显性操作
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)