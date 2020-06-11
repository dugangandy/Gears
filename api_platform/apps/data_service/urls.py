# -*-coding:utf-8 -*-
"""data_service URL Configuration

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

from django.conf.urls import url

from views import *
from api_platform.apps.testcase.views import *

urlpatterns = [
    url(r'^get_all_projects/$', get_all_projects, name=u'所有应用列表'),

    url(r'^get_project_list/$', get_project_list, name=u'获取应用列表'),

    url(r'^get_api_list/$', get_api_list, name=u'获取接口列表'),

    # 定时任务
    url(r'^generate/testcase/$', generate_testcase, name=u'自动生成测试用例任务'),
    url(r'^generate/testplan/$', generate_testplan, name=u'自动生成测试计划任务'),
    url(r'^scheduler/run_testplan/$', scheduler_run_testplan, name=u'定时调度执行测试计划任务'),
    url(r'^scheduler/send_report/$', scheduler_send_report, name=u'定时发送测试报告'),

    # 备份表
    url(r'^database/backup/$', backup_database, name=u'备份数据库'),
    url(r'^database/restore/$', restore_database, name=u'还原数据库'),
    url(r'^database/cleanup/$', cleanup_database, name=u'清理备份数据表'),

    # 数据库配置
    url(r'^dbConfigPage/$', db_config_page, name=u'数据库配置'),
    url(r'^dbConfig/datagrid/$', db_config_datagrid, name=u'数据库配置列表'),
    url(r'^dbConfig/save/$', save_config, name=u'保存数据库配置'),
    url(r'^dbConfig/remove/$', remove_config, name=u'删除数据库配置'),

    # 数据库配置(for yapi)
    url(r'^yapi/dbConfigPage/$', db_config_page_yapi, name=u'数据库配置_YAPI'),
    url(r'^yapi/dbConnect/$', db_connect, name=u'数据库连接测试'),
    url(r'^api/db/query/$', dbapi_query, name=u'数据库查询'),
    url(r'^api/db/update/$', dbapi_update, name=u'数据库更新'),
    url(r'^api/db/verify/$', dbapi_verify, name=u'数据库验证'),
]
