# -*-coding:utf-8 -*-
"""api_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.generic.base import RedirectView

from api_platform.views import *

urlpatterns = [
    # ******系统主页******
    url(r'^$', index_v2, name='index_v2'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/img/favicon.ico')),

    url(r'^project/$', project_index, name=u'应用首页'),

    # ******健康检查URL******
    url(r'^check.txt$', health_check, name='HA check'),

    # 获取运行环境列表
    url(r'^common/envlist', get_env_list, name='env list'),

    # 所有产品线
    url(r'^cmdb/productlines$', cmdb_productlines, name='cmdb_productlines'),
    # 所有应用信息
    url(r'^cmdb/projects$', cmdb_projects, name='cmdb_projects'),

    # ********************** data_service app 路由信息 **********************
    url(r'^data/', include('api_platform.apps.data_service.urls')),

    # ********************** testcase app 路由信息 **********************
    url(r'^testcase/', include('api_platform.apps.testcase.urls')),

    # ********************** report app 路由信息 **********************
    url(r'^report/', include('api_platform.apps.report.urls')),
]
