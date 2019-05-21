#coding:utf-8
#!/usr/bin/env python
""""
********************************************
Program:
Description:
Author: Yongxin
Date: 2019-04-28 04:33:15
Last modified: 2019-04-28 04:33:15
********************************************
"""

from django.contrib import admin



class BaseOwnerAdmin(admin.ModelAdmin):
    '''
    1. model owner field handle
    2. queryset filter
    '''

    exclude =('owner', )

    def get_queryset(self, request):
        qs = super(BaseOwnerAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(BaseOwnerAdmin, self).save_model(self, request, obj, form, change)
