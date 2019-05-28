#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-05-21 11:12:20
Last modified: 2019-05-21 11:12:20
********************************************
"""
from django.shortcuts import render

# Create your views here.
def post_list(request, category_id=None, tag_id=None):
    return render(request, 'blog/list.html', context={'name':'post_list'})

def post_detail(request, post_id):
    return render(request, 'blog/detail.html', context={'name':'post_detail'})
