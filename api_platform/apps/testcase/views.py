# -*-coding:utf-8 -*-
import threading

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import api_service
import databank_service
import project_service
import testcase_service
import testexecution_service
import testplan_service
import testreport_service
from utils import *


logger = logging.getLogger('gears.app')

status_dict = {0: '未执行', 1: '正在执行', 2: '执行完成'}
env_dict = {1: '生产', 2: '测试', 3: 'MIT', 4: 'UAT'}


# Create your views here.
# 接口管理页面
def api_list_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        if 'apiLevel' in params:
            api_level = params['apiLevel']
        else:
            api_level = ''

        context = {
            'systemAlias': system_alias,
            'apiLevel': api_level,
        }

        return render(request, 'api/api_list.html', context)
    except Exception, ex:
        logger.error("加载接口管理页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


@csrf_exempt
def api_datagrid(request):
    params = request.GET or request.POST
    page = 1
    size = 10
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        # 系统别名
        system_alias = ''
        if 'systemAlias' in params and params['systemAlias'] != '':
            system_alias = params['systemAlias']

        # 接口名
        api_name = ''
        if 'apiName' in params and params['apiName'] != '':
            api_name = params['apiName']

        # 接口级别
        api_level = ''
        if 'apiLevel' in params and params['apiLevel'] != '':
            api_level = params['apiLevel']

        result = api_service.api_datagrid(system_alias, api_level, api_name, page, size)
    except:
        msg = '加载接口表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 编辑接口
@csrf_exempt
def edit_api(request):
    try:
        params = request.GET or request.POST
        api_dto = {
            'user': request.session['username'] if 'username' in request.session else 'System',
            'id': params['id'],
            'api_desc': params['api_desc'],
            'api_level': params['api_level'],
            'api_name': params['api_name'],
            'method': params['method'],
            'request_header': params['request_header'],
            'system_alias': params['system_alias'],
        }
        result = api_service.edit(api_dto)
    except Exception, ex:
        msg = '保存接口失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 删除接口
@csrf_exempt
def remove_api(request):
    result = {}
    try:
        params = request.GET or request.POST

        # 接口ID
        api_id = ''
        if 'apiId' in params and params['apiId'] != '':
            api_id = params['apiId']

        result = api_service.remove(api_id)
    except Exception, ex:
        msg = '删除接口失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {'code': 1, "message": msg}

    return MyJsonResponse(result, safe=False)


@csrf_exempt
def get_api_list(request):
    api_list = []
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
            apis = ApiList.objects.filter(is_delete=0, system_alias=system_alias).values('api_name').order_by(
                'api_name')
            # 根据接口级别过滤
            if 'apiLevel' in params and params['apiLevel'] != '':
                apis = apis.filter(api_level=params['apiLevel'])
            for api in apis:
                api_list.append(api['api_name'])
    except Exception as e:
        logger.error('根据应用名获取接口列表失败! 错误信息：\n%s' % traceback.format_exc())
    return MyJsonResponse(api_list, safe=False)


@csrf_exempt
def get_testcase_list(request):
    case_list = []
    try:
        params = request.GET or request.POST
        if 'apiName' in params:
            # 获取apiname 对应的ID
            apiName = params['apiName']
            api_id = ApiList.objects.filter(is_delete=0, api_name=apiName).values('id')

            # 获取对应Id下的所有用例描述
            testcasies = ApiTestcases.objects.filter(api_id=api_id).values_list('id', 'summary')
            print testcasies
            for case in testcasies:
                case_list.append({'testcase_id': case[0], 'testcase_summary': case[1]})
            print case_list
    except Exception as e:
        logger.error('根据应用名获取接口列表失败! 错误信息：\n%s' % traceback.format_exc())
    return MyJsonResponse(case_list, safe=False)


# 测试用例列表页面
def testcase_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        if 'apiName' in params:
            api_name = params['apiName']
        else:
            api_name = ''

        context = {
            'systemAlias': system_alias,
            'apiName': api_name,
        }

        return render(request, 'testcase/testcase.html', context)
    except Exception, ex:
        logger.error("加载测试用例页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


@csrf_exempt
def testcase_datagrid(request):
    params = request.GET or request.POST
    page = 1
    size = 10
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        testcase_dto = {"page": page, "size": size}

        # 系统别名
        system_alias = ''
        if 'systemAlias' in params and params['systemAlias'] != '':
            system_alias = params['systemAlias']
        testcase_dto['system_alias'] = system_alias

        # 接口名
        api_name = ''
        if 'apiName' in params and params['apiName'] != '':
            api_name = params['apiName']
        testcase_dto['api_name'] = api_name

        # 接口级别
        api_level = ''
        if 'apiLevel' in params and params['apiLevel'] != '':
            api_level = params['apiLevel']
        testcase_dto['api_level'] = api_level

        # 显示已启用
        show_enabled = 0
        if 'showEnabled' in params and params['showEnabled'] != '':
            show_enabled = int(params['showEnabled'])
        testcase_dto['show_enabled'] = show_enabled

        result = testcase_service.datagrid(testcase_dto)
    except:
        msg = u'加载测试用例表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 管理页面
def admin_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        run_env = 2
        if 'runEnv' in params and params['runEnv'].strip() != '':
            run_env = params['runEnv']

        topic = ''
        if 'topic' in params:
            topic = params['topic']

        context = {
            'systemAlias': system_alias,
            'runEnv': run_env,
            'topic': topic,
        }

        return render(request, 'admin/admin_page.html', context)
    except Exception, ex:
        logger.error(u"加载后台管理页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 测试执行页面
def test_execution_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        if 'testplanId' in params:
            testplan_id = params['testplanId']
        else:
            testplan_id = ''

        context = {
            'systemAlias': system_alias,
            'testplanId': testplan_id,
            'testplanList': testplan_service.get_testplan_list(system_alias)
        }
        return render(request, 'testcase/testcase_execution.html', context)
    except Exception, ex:
        logger.error(u"加载测试执行页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


@csrf_exempt
def execution_datagrid(request):
    params = request.GET or request.POST

    page = 1
    size = 10
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        # 系统别名
        testplan_id = ''
        if 'testplanId' in params and params['testplanId'] != '':
            testplan_id = params['testplanId']

        execution_dto = {
            "testplan_id": testplan_id,
            "page": page,
            "size": size,
            "sort": params['sortName'] if 'sortName' in params else 'create_time',
            "order": params['sortOrder'] if 'sortOrder' in params else 'desc',
        }
        result = testexecution_service.execution_datagrid(execution_dto)
    except:
        logger.error(u"加载测试执行表格失败！ 错误信息: \n%s" % traceback.format_exc())
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 测试计划页面
def testplan_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        if 'testplanId' in params:
            testplan_id = params['testplanId']
        else:
            testplan_id = ''

        context = {
            'systemAlias': system_alias,
            'testplanId': testplan_id,
        }

        return render(request, 'testcase/testplan.html', context)
    except Exception, ex:
        logger.error(u"加载测试计划页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


@csrf_exempt
def testplan_datagrid(request):
    params = request.GET or request.POST

    page = 1
    size = 10
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        # 系统别名
        system_alias = ''
        if 'systemAlias' in params and params['systemAlias'] != '':
            system_alias = params['systemAlias']

        # 计划状态
        status = ''
        if 'status' in params and params['status'] != '':
            status = params['status']

        result = testplan_service.testplan_datagrid(system_alias, status, page, size)
    except:
        logger.error(u"加载测试计划表格失败！ 错误信息: \n%s" % traceback.format_exc())
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 测试报告_摘要表格
@csrf_exempt
def testplan_summary(request):
    params = request.GET or request.POST
    summary = []
    try:
        # 测试计划ID
        if 'testplanId' in params and params['testplanId'] != '':
            testplan_ids = params['testplanId'].strip().split(',')
            for testplan_id in testplan_ids:
                try:
                    id = int(testplan_id)
                    summary.append(testplan_service.get_testplan_info(id))
                except:
                    logger.warn(u'获取测试计划信息异常! ID: %s, 异常信息:\n%s' % (testplan_id, traceback.format_exc()))
    except:
        logger.error(u"加载测试报告摘要表格失败！ 错误信息: \n%s" % traceback.format_exc())

    return MyJsonResponse({"total": len(summary), "rows": summary}, safe=False)


# 测试报告_用例执行详情
@csrf_exempt
def test_execution_list(request):
    params = request.GET or request.POST
    execution_list = []
    try:
        # 测试计划ID
        if 'testplanId' in params and params['testplanId'] != '':
            testplan_id = int(params['testplanId'])

            execution_list = testreport_service.get_execution_list(testplan_id)
    except:
        logger.error(u"加载测试用例执行详情失败！ 错误信息: \n%s" % traceback.format_exc())

    return MyJsonResponse({"total": len(execution_list), "rows": execution_list}, safe=False)


@csrf_exempt
def remove_testplan(request):
    result = {}
    try:
        params = request.GET or request.POST

        # 系统别名
        testplan_id = ''
        if 'testplanId' in params and params['testplanId'] != '':
            testplan_id = params['testplanId']

        result = testplan_service.remove(testplan_id)

    except Exception, ex:
        msg = u'删除测试计划失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 自动生成接口测试用例
@csrf_exempt
def create_testcase(request):
    try:
        params = request.GET or request.POST
        user = request.session['username'] if 'username' in request.session else 'System'
        system_alias = ''
        if 'systemAlias' in params and params['systemAlias'].strip() != '':
            system_alias = params['systemAlias']

        # 根据配置中心获取当前环境
        run_env = config_env_dict[config_env] if config_env in config_env_dict else 2
        # if 'runEnv' in params:
        #     run_env = int(params['runEnv'])

        if system_alias != '':
            result = testcase_service.batch_create(system_alias, run_env, user)
        else:
            result = {"code": 1, "message": u'必须提供系统别名!'}
    except Exception as e:
        msg = u'创建测试用例失败！错误信息:\n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 创建测试计划
@csrf_exempt
def testplan_create(request):
    try:
        user = 'System'
        session = request.session
        if session and 'username' in session:
            user = request.session['username']
        params = request.GET or request.POST
        if 'username' in params and params['username'] != '':
            user = params['username']
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            return MyJsonResponse(u'params error! systemAlias is required!', safe=False)

        # 根据配置获取当前环境
        run_env = config_env_dict[config_env] if config_env in config_env_dict else 2

        is_auto = 0
        if 'isAuto' in params and params['isAuto'].strip() != '':
            is_auto = int(params['isAuto'])

        result = testplan_service.testplan_create(system_alias, run_env, user, is_auto)

    except Exception as e:
        msg = u'创建测试计划异常! \n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 执行测试计划
@csrf_exempt
def run_testplan(request):
    exec_count = 0
    code = 0
    msg = ''
    try:
        session = request.session
        user = 'System'
        if session and 'username' in session:
            user = session['username']
        params = request.GET or request.POST
        if 'testplanId' in params:
            testplan_id = int(params['testplanId'])
        else:
            return MyJsonResponse(u'params error! testplanId is required!', safe=False)

        server_list = []
        if 'serverIp' in params and params['serverIp'].strip() != '':
            server_ip = params['serverIp']
            server_list.append(server_ip)

        t = threading.Thread(target=testexecution_service.parallel_run_testplan, args=(testplan_id, server_list, user))
        t.setDaemon(True)
        t.start()
        msg = u'测试计划已启动，请稍候查看执行结果!'

    except Exception as e:
        msg = u'执行测试计划失败! 错误信息：\n%s' % traceback.format_exc()
        code = 1
        logger.error(msg)

    return MyJsonResponse({"code": code, "message": msg}, safe=False)


@csrf_exempt
def remove_testcase(request):
    result = {}
    try:
        params = request.GET or request.POST

        # 测试用例ID
        testcase_id = ''
        if 'testcaseId' in params and params['testcaseId'] != '':
            testcase_id = params['testcaseId']

        result = testcase_service.remove(testcase_id)
    except Exception, ex:
        msg = '删除测试用例失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {'code': 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 重新执行测试用例
@csrf_exempt
def run_testcase(request):
    session = request.session
    user_name = session['username'] if 'username' in session else 'System'
    result = {}
    try:
        params = request.GET or request.POST
        if 'executionId' in params:
            execution_id = int(params['executionId'])
            result = testexecution_service.run_testcase(execution_id, user_name)

            # t = threading.Thread(target=testexecution_service.run_testcase, args=(execution_id, user_name))
            # t.setDaemon(True)
            # t.start()
            # msg = '测试用例开始执行，请稍候查看执行结果。'
        else:
            result = {"code": 2, "message": u'params error! executionId is required!'}

    except Exception as e:
        msg = '执行测试用例出错! \n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 编辑测试用例
@csrf_exempt
def edit_testcase(request):
    try:
        params = request.GET or request.POST
        testcase_dto = {
            'user': request.session['username'] if 'username' in request.session else 'System',
            'id': params['id'],
            'api_name': params['api_name'],
            'summary': params['summary'],
            'request_data': params['request_data'],
            'response_data': params['response_data'],
        }
        result = testcase_service.edit(testcase_dto)
    except Exception, ex:
        msg = u'保存测试用例失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 编辑数据脚本
@csrf_exempt
def edit_datascript(request):
    try:
        params = request.GET or request.POST
        testcase_dto = {
            'user': request.session['username'] if 'username' in request.session else 'System',
            'script_id': params['script_id'],
            'dept_name': params['dept_name'],
            'script_bu': params['script_bu'],
            'api_list': params['api_list'],
        }
        print testcase_dto
        result = databank_service.data_script_edit(testcase_dto)
    except Exception, ex:
        msg = u'保存测试用例失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 启用/禁用测试用例
@csrf_exempt
def enable_testcase(request):
    try:
        params = request.GET or request.POST
        if 'id' in params:
            result = testcase_service.enable(int(params['id']))
        else:
            msg = u'传入id为空.'
            logger.warn(msg)
            result = {"code": 1, "message": msg}
    except Exception, ex:
        msg = u'保存测试用例失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 测试报告页面
def test_report_page(request):
    params = request.GET or request.POST
    try:
        if 'testplanId' in params:
            testplan_id = params['testplanId']
        else:
            testplan_id = ''

        context = {
            'testplanId': testplan_id,
            'reportTime': datetime.datetime.now(),
        }
        return render(request, 'testcase/testreport.html', context)
    except Exception, ex:
        logger.error(u"加载测试报告页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 发送测试报告邮件
@csrf_exempt
def send_report_mail(request):
    result = {}
    try:
        params = request.GET or request.POST

        # 系统别名
        testplan_id = ''
        if 'testplanId' in params and params['testplanId'] != '':
            testplan_id = params['testplanId']
            mail_list = 'gang.du@126.com'
            send_email(u'接口测试报告_%s' % datetime.datetime.now().strftime('%Y年%m月%d日'),
                       testreport_service.get_summary_html(testplan_id), mail_list, 'Test')
            result = {"code": 0, "message": u'发送测试报告邮件成功！'}
        else:
            result = {"code": 1, "message": u'testplanId不能为空!'}

    except Exception, ex:
        msg = u'发送测试报告邮件失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 应用列表页面
def project_list_page(request):
    params = request.GET or request.POST
    try:
        if 'buName' in params:
            bu_name = params['buName']
        else:
            bu_name = ''

        context = {
            'buName': bu_name,
        }

        return render(request, 'project/project_list.html', context)
    except Exception, ex:
        logger.error(u"加载应用列表页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 根据业务线查询应用（本地）
def get_cmdb_alians(request):
    params = request.GET or request.POST
    try:
        if 'buName' in params:
            buName = params['buName']
        else:
            buName = ''

        result = project_service.get_project(buName=buName)

        return MyJsonResponse(result, safe=False)
    except Exception, ex:
        logger.error(u"加载测试用例失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 数据银行页
def data_bank_list_page(request):
    params = request.GET or request.POST
    try:
        if 'buName' in params:
            bu_name = params['buName']
        else:
            bu_name = ''

        context = {
            'buName': bu_name,
        }

        return render(request, 'project/data_banks.html', context)
    except Exception, ex:
        logger.error(u"加载数据银行页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 数据脚本表格
@csrf_exempt
def data_bank_script_grid(request):
    params = request.GET or request.POST
    page = 1
    size = 10
    print params
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        if 'buName' in params:
            bu_name = params['buName']
            print params['buName']
        else:
            bu_name = ''

        result = databank_service.databank_grid(bu_name, page, size)
    except:
        msg = u'加载应用表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 数据脚本执行记录
def data_bank_script_records(request):
    params = request.GET or request.POST
    page = 1
    size = 10
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass
    try:
        if 'Sid' in params:
            Sid = params['Sid']
        else:
            Sid = ''
        result = databank_service.databank_records(Sid, page, size)
    except:
        msg = u'加载应用表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 数据池
def data_bank_script_source(request):
    params = request.GET or request.POST
    page = 1
    size = 10
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass
    try:
        if 'Sid' in params:
            Sid = params['Sid']
        else:
            Sid = ''
        result = databank_service.databank_source(Sid, page, size)
    except:
        msg = u'加载应用表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 查询数据脚本参数
@csrf_exempt
def get_data_bank_script(request):
    params = request.GET or request.POST
    try:
        if 'Sid' in params:
            Sid = params['Sid']
        else:
            Sid = ''

        result = databank_service.get_databank_script(Sid=Sid)
    except:
        msg = u'加载应用表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 数据脚本执行参数更新
@csrf_exempt
def data_bank_script_save(request):
    params = request.GET or request.POST
    try:
        if 'Sid' in params:
            Sid = params['Sid']
        else:
            Sid = ''
        if 'run_times' in params:
            run_times = params['run_times']
        else:
            run_times = ''
        if 'run_cron' in params:
            run_cron = params['run_cron']
        else:
            run_cron = ''
        if 'auto_run' in params:
            auto_run = params['auto_run']
        else:
            auto_run = ''
        result = databank_service.databank_script_save(Sid=Sid, run_times=run_times, run_cron=run_cron,
                                                       auto_run=auto_run)
    except:
        msg = u'加载应用表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 执行数据脚本
@csrf_exempt
def data_bank_script_run(request):
    code = 0
    try:
        session = request.session
        user = 'System'
        if session and 'username' in session:
            user = session['username']
        params = request.GET or request.POST
        if 'name' in params:
            script_id = params['name']
        else:
            return MyJsonResponse(u'params error! script_id is required!', safe=False)

        server_list = []
        if 'serverIp' in params and params['serverIp'].strip() != '':
            server_ip = params['serverIp']
            server_list.append(server_ip)

        t = threading.Thread(target=testexecution_service.parallel_creat_datascript, args=(script_id, user))
        t.setDaemon(True)
        t.start()
        msg = u'数据脚本已启动，请稍候查看执行结果!'

    except Exception as e:
        msg = u'运行数据脚本失败! 错误信息：\n%s' % traceback.format_exc()
        code = 1
        logger.error(msg)

    return MyJsonResponse({"code": code, "message": msg}, safe=False)


# 新增数据脚本
@csrf_exempt
def data_bank_add_script(request):
    params = request.GET or request.POST
    try:
        if 'datascript_id' in params:
            datascript_id = params['datascript_id']
        else:
            datascript_id = 'Test' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        context = {
            'datascript_id': datascript_id,
        }

        return render(request, 'project/add_jmx.html', context)
    except Exception, ex:
        logger.error(u"加载数据银行页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 获取脚本关联测试用例
@csrf_exempt
def datascript_testcase(request):
    params = request.GET or request.POST
    try:
        if 'datascript_id' in params:
            datascript_id = params['datascript_id']
        else:
            datascript_id = ''

        result = databank_service.get_datascript_testcase(Sid=datascript_id)

        return MyJsonResponse(result, safe=False)
    except Exception, ex:
        logger.error(u"加载数据银行页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 获取测试用例详情
@csrf_exempt
def get_testcase(request):
    params = request.GET or request.POST
    try:
        if 'testcase_id' in params:
            testcase_id = params['testcase_id']
        else:
            testcase_id = ''

        result = testcase_service.get_testcase_info(id=str(testcase_id))

        return MyJsonResponse(result, safe=False)
    except Exception, ex:
        logger.error(u"加载测试用例失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 回归测试页
def project_regression_test(request):
    params = request.GET or request.POST
    try:
        if 'buName' in params:
            bu_name = params['buName']
        else:
            bu_name = ''

        context = {
            'buName': bu_name,
        }

        return MyJsonResponse(u'施工中，敬请期待')
    except Exception, ex:
        logger.error(u"加载回归测试页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


@csrf_exempt
def project_datagrid(request):
    params = request.GET or request.POST
    page = 1
    size = 10
    try:
        page = int(params['pageNumber'])
        size = int(params['pageSize'])
        if page < 1:
            page = 1
        if size < 10:
            size = 10
    except ValueError:
        pass
    except TypeError:
        pass

    try:
        if 'buName' in params:
            bu_name = params['buName']
            print params['buName']
        else:
            bu_name = ''

        if 'hasApi' in params:
            has_api = int(params['hasApi'])
        else:
            has_api = 0

        result = project_service.project_datagrid(bu_name, page, size, has_api)
    except:
        msg = u'加载应用表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 根据别名获取应用信息
@csrf_exempt
def project_sence(request):
    params = request.GET or request.POST
    try:
        if 'projectName' in params:
            projectName = params['projectName']
        else:
            projectName = ''

        result = project_service.project_sence(projectName)
    except:
        msg = u'加载应用表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


@csrf_exempt
def project_toggle_domain(request):
    params = request.GET or request.POST

    try:
        if 'projectId' in params:
            project_id = params['projectId']
            result = project_service.project_toggle_domain(project_id)
        else:
            result = {"code": 1, "message": u"应用未同步，请先同步!"}
    except:
        msg = u'应用域名访问设置失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


@csrf_exempt
def project_sync(request):
    params = request.GET or request.POST

    try:
        if 'name' in params and params['name'].strip() != '':
            name = params['name']
            result = project_service.project_sync(name)
        else:
            result = project_service.project_sync_all()
    except:
        msg = u'同步应用数据失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 获取测试计划状态
@csrf_exempt
def get_testplan_info(request):
    try:
        params = request.GET or request.POST
        if 'id' in params and params['id'] != '':
            testplan_id = int(params['id'])
        else:
            return MyJsonResponse(u'params error! id is required!', safe=False)

        testplan_info = testplan_service.get_testplan_info(testplan_id)
        if 'status' in testplan_info:
            result = {"code": 0, "message": u"操作成功", "data": testplan_info}
        else:
            result = {"code": 1, "message": u"没有找到ID: %s 的测试计划!" % id}

    except Exception as e:
        msg = u'get testplan status error! \n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 检查点列表页面
def testcase_checkpoint_page(request):
    params = request.GET or request.POST
    try:
        testcase_id = -1
        if 'testcaseId' in params and params['testcaseId'].strip != '':
            testcase_id = int(params['testcaseId'])

        context = {
            'testcaseId': testcase_id,
        }

        return render(request, 'testcase/testcase_checkpoint.html', context)
    except Exception, ex:
        logger.error(u"加载测试用例检查点页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


@csrf_exempt
def checkpoint_datagrid(request):
    params = request.GET or request.POST
    try:
        # 测试用例ID
        testcase_id = ''
        if 'testcaseId' in params and params['testcaseId'] != '':
            testcase_id = params['testcaseId']

        result = testcase_service.checkpoint_datagrid(testcase_id)
    except:
        msg = u'加载测试用例检查点表格失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


@csrf_exempt
def save_checkpoint(request):
    try:
        params = request.GET or request.POST
        checkpoint_dto = {
            'user': request.session['username'] if 'username' in request.session else 'System',
            'id': params['id'], 'testcaseId': params['testcaseId'],
            'check_type': params['check_type'],
            'check_param': params['check_param'],
            'operate': params['operate'],
            'expect_value': params['expect_value'],
        }
        result = testcase_service.edit_checkpoint(checkpoint_dto)
    except Exception, ex:
        msg = u'保存测试用例检查点失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


@csrf_exempt
def remove_checkpoint(request):
    result = {}
    try:
        params = request.GET or request.POST

        # 检查点ID
        if 'checkpointId' in params and params['checkpointId'] != '':
            checkpoint_id = int(params['checkpointId'])
            result = testcase_service.remove_checkpoint(checkpoint_id)
        else:
            result = {"code": 2, "message": u'缺少参数id.'}
    except Exception, ex:
        msg = u'删除测试用例检查点失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {'code': 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 测试测试用例
@csrf_exempt
def test_testcase(request):
    session = request.session
    user_name = session['username'] if 'username' in session else 'System'
    result = {}
    try:
        params = request.GET or request.POST
        if 'testcaseId' in params:
            testcase_id = int(params['testcaseId'])
            result = testcase_service.test_testcase(testcase_id)

        else:
            result = {"code": 2, "message": u'缺少参数testcaseId is required!'}

    except Exception as e:
        msg = u'测试出错! \n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 测试用例执行结果页面
def testresult_page(request):
    params = request.GET or request.POST
    try:
        if 'testcaseId' in params:
            testcase_id = params['testcaseId']
        else:
            testcase_id = ''

        context = {
            'testcaseId': testcase_id,
        }

        return render(request, 'testcase/testresult.html', context)
    except Exception, ex:
        logger.error(u"加载测试用例执行结果页面失败! \n%s" % traceback.format_exc())
        return redirect('/')
