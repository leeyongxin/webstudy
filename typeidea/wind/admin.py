'''
@Author: Yongxin
@Date: 2019-08-14 01:45:49
@LastEditors: Yongxin
@LastEditTime: 2019-08-14 01:56:13
@Description: 
'''
from django.contrib import admin

# Register your models here.
from .models import Database, Turbine, DbTable

admin.site.register(Database)
admin.site.register(Turbine)
admin.site.register(DbTable)

from typeidea.custom_site import custom_site
# Register your models here.


@admin.register(Turbine, site=custom_site)
class Turbineadmin(admin.ModelAdmin):
    pass

@admin.register(DbTable, site=custom_site)
class Dbadmin(admin.ModelAdmin):
    pass