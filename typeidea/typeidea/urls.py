"""typeidea URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, re_path, include

from .custom_site import custom_site
from blog.views import post_list, post_detail
from config.views import links
import wind.views.cbsview1 as wv
import wind.views.cbsview2 as wv2
import wind.views.fbsview as fv

urlpatterns = [
    url(r'^$', post_list, name='home'),
    url(r'^category/(?P<category_id>\d+)/$', post_list),
    url(r'^tag/(?P<tag_id>\d+)/$', post_list),
    url(r'^post/(?P<post_id>\d+).htmls/$', post_detail),
    url(r'^links/$', links),

    url(r'^wind/$', wv.DbListView.as_view(), name='wind_home'),
    url(r'^wind/form/$', wv2.MapeView.as_view(), name='wind_form'),
    url(r'^js/$', wv.JS.as_view(), name='js'),
    url(r'^js_d(?P<pk>[0-9])/$', fv.getimage1, name='jsd'),
    url(r'^wind/(?P<slug>[a-zA-Z0-9_-]*).html/$',
        wv.TableListView.as_view(), name='db_view'),
    url(r'^wind/(?P<db>[a-zA-Z0-9_-]*)/(?P<table>[a-zA-Z0-9_-]*).html/$',
        wv.TableDetailView.as_view(), name='table_view'),
    url(r'^wind/(?P<db>[a-zA-Z0-9_-]*)/(?P<table>[a-zA-Z0-9_-]*)/pic/$',
        wv.ImageView.as_view(), name='pic_view'),
    url(r'^wind/(?P<db>[a-zA-Z0-9_-]*)/(?P<table>[a-zA-Z0-9_-]*)/selected/$',
        wv.SelectedView.as_view(), name='sel_view'),
    url('^super_admin/', admin.site.urls),
    url('^admin/', custom_site.urls),
]
