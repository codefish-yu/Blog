# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-11-04 08:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('username', models.CharField(max_length=11, primary_key=True, serialize=False, verbose_name='用户名')),
                ('nickname', models.CharField(max_length=30, verbose_name='昵称')),
                ('email', models.EmailField(max_length=254, verbose_name='邮箱')),
                ('password', models.CharField(default='', max_length=32, verbose_name='个人描述')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now_add=True, verbose_name='更新时间')),
            ],
            options={
                'db_table': 'user_profile',
            },
        ),
    ]