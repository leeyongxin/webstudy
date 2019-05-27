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

from .custom_site import custom_site
from blog.views import post_list, post_detail
from config.views import links
from wind import views as wv

urlpatterns = [
    url(r'^$', post_list, name='home'),
    url(r'^category/(?P<category_id>\d+)/$', post_list),
    url(r'^tag/(?P<tag_id>\d+)/$', post_list),
    url(r'^post/(?P<post_id>\d+).htmls/$', post_detail),
    url(r'^links/$', links),
    url(r'^wind/$', wv.DbListView.as_view(), name='wind_base'),
    url(r'^wind/ubdate/$', wv.read_db_name, name='read_db'),
    url(r'^wind/read_col/$', wv.TableListView.as_view(), name='read_table'),
    url('^super_admin/', admin.site.urls),
    url('^admin/', custom_site.urls),
]
