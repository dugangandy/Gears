# -*-coding:utf-8 -*-
from api_platform.apps.data_service.models import *
from testexecution_service import *
from testplan_service import *


# 根据测试计划获取执行详情
def get_execution_list(testplan_id):
    execution_list = []
    if testplan_id != '':
        api_executions = ApiExecution.objects.filter(testplan_id=testplan_id).order_by('result')
        for execution in api_executions:
            execution_list.append(get_execution_info(execution.id))

    return execution_list


def get_summary_html(testplan_ids):
    id_list = testplan_ids.split(',')
    table_html = '<table border=1 width=98%% cellpadding=0 cellspacing=0 align=center bgcolor=#CCFFFF>' \
                 '<tr><th width=10%% align=center><strong>业务线</strong></th><th width=20%% align=center><strong>测试计划</strong></th><th width=20%% align=center>' \
                 '<strong>描述</strong></th><th width=10%% align=center><strong>测试用例数</strong></th>' \
                 '<th width=8%% align=center><strong>通过率</strong></th><th width=8%% align=center><strong>运行环境</strong></th>' \
                 '<th width=12%% align=center><strong>开始时间</strong></th><th width=12%% align=center><strong>完成时间</strong></th></tr>'
    for id in id_list:
        if id.strip() == '':
            continue
        testplan = get_testplan_info(int(id))
        report_url = 'http://gears.dugang.vip/testcase/reportPage/?testplanId=%s' % testplan['id']
        table_html += '<td>%s</td><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                      % (testplan['bu_name'], report_url, testplan['name'], testplan['desc'], testplan['count'],
                         testplan['success_rate'],
                         testplan['env'], testplan['actual_start_time'], testplan['actual_end_time'])
    table_html += '</table>'
    css_style = '<style type="text/css">th, td {background-color: #CCFFFF; text-align: center; font: normal 12px "Lucida Grande", Helvetica, sans-serif;}</style>'
    report_url = 'http://gears.dugang.vip/testcase/reportPage/?testplanId=%s' % testplan_ids
    foot_div = '<br><div style="float:right;"><span>--------<br>报告生成时间：%s<br>数据来源：<a target="_blank" ' \
               'href="http://gears.dugang.vip/">Gears</a>. </span></div>' % \
               datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message_html = '<html><head>%s</head><body><table>%s</table><div><a href="%s">测试报告详情</a></div>%s<body></html>' % \
                   (css_style, table_html, report_url, foot_div)

    return message_html


def get_report_mail_list(key):
    mail_list = []
    sys_configs = SysConfig.objects.filter(is_delete=0, group='report_mail_list', key=key)
    if len(sys_configs) > 0:
        config_value = sys_configs[0].value
        for item in config_value.split(','):
            mail_list.append('%s@126.com' % item)

    return mail_list
