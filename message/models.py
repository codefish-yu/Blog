from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import UserProfile


class Message(models.Model):
    content  = models.CharField(max_length=50,verbose_name='内容')
    created_time = models.DateTimeField(auto_now_add=True,
                                        verbose_name='创建时间')
    parent_message = models.IntegerField(default=0,
                                         verbose_name='关联的留言ID')
    topic =models.ForeignKey(Topic)
    publisher = models.ForeignKey(UserProfile)


    class Meta:
        db_table = 'message'
