import random

from django.db import models

def default_sign():
    signs = ['地表最强','和平主义','我爱我家']
    return random.choice(signs)


# Create your models here.
class UserProfile(models.Model):

    username = models.CharField(max_length=11,verbose_name='用户名',primary_key=True)
    nickname = models.CharField(max_length=30,verbose_name='昵称')
    email = models.EmailField(verbose_name='邮箱')
    password = models.CharField(max_length=32,verbose_name='密码')
    sign = models.CharField(max_length=50, verbose_name='个人描述', default=default_sign)
    info = models.CharField(max_length=150,verbose_name='个人描述',default='')
    created_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now_add=True,verbose_name='更新时间')
    #upload_to 指定存储位置MEDIA_ROOT + upload_to的值
    #wiki/meida/avatar
    avatar = models.ImageField(upload_to='avatar',default='',verbose_name='头像')#upload_to:制定存储位置的参数

    #添加测试字段
    score = models.IntegerField(verbose_name='分数',null=True,default=0)

    class Meta:
        db_table = 'user_profile'
