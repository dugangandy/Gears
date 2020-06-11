# -*-coding:utf-8 -*-
"""testcase URL Configuration

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

urlpatterns = [
    # 应用管理
    url(r'^projectListPage/$', project_list_page, name=u'应用列表页面'),
    url(r'^projectDatagrid/$', project_datagrid, name=u'应用表格'),
    url(r'^projectSence/$', project_sence, name=u'应用信息'),
    url(r'^projectToggleDomain/$', project_toggle_domain, name=u'切换域名访问'),
    # url(r'^projectSync/$', project_sync, name=u'同步应用数据'),

    # 数据银行
    url(r'^DataBanks/$', data_bank_list_page, name=u'数据银行页'),
    url(r'^DataBanksgrid/$', data_bank_script_grid, name=u'数据银行脚本列表页'),
    url(r'^DataScriptRecords/$', data_bank_script_records, name=u'数据脚本执行记录'),
    url(r'^DataScriptRun/$', data_bank_script_run, name=u'数据脚本执行'),
    url(r'^DataScriptUpdate/$', data_bank_script_save, name=u'数据脚本保存'),
    url(r'^DatabankSource/$', data_bank_script_source, name=u'数据池'),
    url(r'^add_script/$',data_bank_add_script,name = u'新增数据脚本'),
    url(r'^get_script_data/$',get_data_bank_script,name = u'查询数据脚本参数'),
    url(r'^get_script_testcase/$', datascript_testcase, name=u'查询数据脚本关联用例'),
    url(r'^script_edit/$', edit_datascript, name=u'新增编辑数据脚本'),
    url(r'^get_alians/$', get_cmdb_alians, name=u'按业务线获取应用名列表'),

    # 自动化回归测试
    url(r'^regressionTest/$', project_regression_test, name=u'自动化回归测试页'),

    # 接口管理
    url(r'^apiListPage/$', api_list_page, name=u'接口列表页面'),
    url(r'^apiDatagrid/$', api_datagrid, name=u'接口表格'),
    url(r'^editApi/$', edit_api, name=u'编辑接口'),
    url(r'^removeApi/$', remove_api, name=u'删除接口'),
    url(r'^getApiList/$', get_api_list, name=u'根据项目名称获取接口列表'),

    # 测试用例管理
    url(r'^getTestcase/$', get_testcase, name=u'测试用例详情'),
    url(r'^listPage/$', testcase_page, name=u'测试用例列表页'),
    url(r'^datagrid/$', testcase_datagrid, name=u'测试用例表格'),
    url(r'^generate/$', create_testcase, name=u'自动生成接口测试用例'),
    url(r'^removeTestcase/$', remove_testcase, name=u'删除测试用例'),
    url(r'^editTestcase/$', edit_testcase, name=u'编辑测试用例'),
    url(r'^testTestcase/$', test_testcase, name=u'测试测试用例'),
    url(r'^enable/$', enable_testcase, name=u'启用/禁用测试用例'),
    url(r'^testresultPage/$', testresult_page, name=u'测试用例执行页面'),
    url(r'^getTestcaseList/$',get_testcase_list,name = u'根据接口名获取测试用例列表'),

    # 测试用例检查点
    url(r'^checkpointPage/$', testcase_checkpoint_page, name=u'检查点列表页'),
    url(r'^checkpoint/datagrid/$', checkpoint_datagrid, name=u'检查点表格'),
    url(r'^checkpoint/save/$', save_checkpoint, name=u'保存检查点'),
    url(r'^checkpoint/remove/$', remove_checkpoint, name=u'删除检查点'),

    # 测试计划管理
    url(r'^testplanPage/$', testplan_page, name=u'测试计划页面'),
    url(r'^testplanDatagrid/$', testplan_datagrid, name=u'测试计划表格'),
    url(r'^removeTestplan/$', remove_testplan, name=u'删除测试计划'),
    url(r'^testplanCreate/$', testplan_create, name=u'自动创建测试计划'),
    url(r'^getTestplanInfo/$', get_testplan_info, name=u'获取测试计划状态'),

    # 测试计划执行
    url(r'^testExecutionPage/$', test_execution_page, name=u'测试执行页面'),
    url(r'^executionDatagrid/$', execution_datagrid, name=u'测试用例执行表格'),
    url(r'^testplanExecute/$', run_testplan, name=u'执行测试计划'),
    url(r'^runTestcase/$', run_testcase, name=u'执行测试用例'),

    # 测试报告
    url(r'^reportPage/$', test_report_page, name=u'测试报告页面'),
    url(r'^report/testplanSummary/$', testplan_summary, name=u'测试计划摘要表格'),
    url(r'^report/testExecutionList/$', test_execution_list, name=u'测试计划执行详情'),
    url(r'^report/sendMail/$', send_report_mail, name=u'发送测试报告邮件'),

    # 后台管理页面
    url(r'^adminPage/$', admin_page, name=u'后台管理页面'),
]
