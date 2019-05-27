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
from django.shortcuts import HttpResponse

# Create your views here.
def post_list(request, category_id=None, tag_id=None):
    content = 'post_list category_id={category_id}, tag_id={tag_id}'.format(category_id=category_id, tag_id=tag_id)
    return HttpResponse(content)

def post_detail(request, post_id):
    return HttpResponse('detail')
