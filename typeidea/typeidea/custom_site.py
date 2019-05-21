#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-04-27 23:55:25
Last modified: 2019-04-27 23:55:25
********************************************
"""
from django.contrib.admin import AdminSite


class CustomSite(AdminSite):
    site_header = ' Typeidea-yx'
    site_title = 'Typeidea-admin'
    index_title = 'home page'


custom_site = CustomSite(name='cus_admin')
