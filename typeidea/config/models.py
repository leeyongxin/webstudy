#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-04-26 04:10:16
Last modified: 2019-04-26 04:10:16
********************************************
"""

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Link(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, 'normal'),
        (STATUS_DELETE, 'delete'),
            )

    title = models.CharField(max_length=50, verbose_name='tile')
    href = models.URLField(verbose_name='link')
    status = models.PositiveIntegerField(default=STATUS_NORMAL,
                                         choices=STATUS_ITEMS,
                                         verbose_name='status')
    weight = models.PositiveIntegerField(default=1,
                                         choices=zip(range(1,6),range(1,6)),
                                         verbose_name='weight',
                                         help_text='weight desend order')

    owner = models.ForeignKey(User, verbose_name='author', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')

    class Meta:
        verbose_name = verbose_name_plural = 'link'

class SideBar(models.Model):
    STATUS_SHOW = 1
    STATUS_HIDE = 0
    STATUS_ITEMS = (
        (STATUS_SHOW, 'show'),
        (STATUS_HIDE, 'hide'),
            )
    SIDE_TYPE = (
           (1, 'HTML'),
           (2, 'new article'),
           (3, 'hot article'),
           (4, 'new comments'),
            )

    title = models.CharField(max_length=50, verbose_name='tile')
    display_type = models.PositiveIntegerField(default=1,
                                         choices=SIDE_TYPE,
                                         verbose_name='display type')
    content = models.CharField(max_length=500, blank=True,
                                         verbose_name='content',
                                         help_text='can be blank if not HTML type')

    status = models.PositiveIntegerField(default=STATUS_SHOW,
                                         choices=STATUS_ITEMS,
                                         verbose_name='status')
    owner = models.ForeignKey(User, verbose_name='author', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='create_time')

    class Meta:
        verbose_name = verbose_name_plural = 'side bar'
