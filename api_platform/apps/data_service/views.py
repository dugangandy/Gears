# -*-coding:utf-8 -*-
import threading
import jsonpath
import threadpool
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from api_platform.apps.data_service import db_service
from api_platform.apps.testcase import testcase_service, testplan_service, testexecution_service, testreport_service
from api_platform.apps.testcase.utils import *
from models import *

reload(sys)
sys.setdefaultencoding('utf8')

logger = logging.getLogger('gears.app')


@csrf_exempt
def get_all_projects(request):
    project_list = []
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        all_projects = cmdb_util.get_all_projects_db()
        for name in all_projects:
            project = {"text": name, "id": all_projects[name]['project_id']}
            project_list.append(project)

    except Exception as e:
        logger.error('loading all projects data error! \n%s' % traceback.format_exc())

    return JsonResponse(project_list, safe=False)


@csrf_exempt
def get_project_list(request):
    project_list = []
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        api_list = ApiList.objects.filter(system_alias__contains=system_alias).order_by('system_alias').values(
            'system_alias').distinct()
        for api in api_list:
            project_list.append(api['system_alias'])

    except Exception as e:
        logger.error('loading project list data error! \n%s' % traceback.format_exc())

    return JsonResponse(project_list, safe=False)


@csrf_exempt
def get_api_list(request):
    api_list = []
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''
        if 'runEnv' in params and params['runEnv'].strip() != '':
            run_env = int(params['runEnv'])
        else:
            run_env = 1
        if 'startTime' in params:
            start_time = params['startTime']
        else:
            start_time = None
        if 'endTime' in params:
            end_time = params['endTime']
        else:
            end_time = None
        api_list = get_api_data(system_alias, run_env, start_time, end_time)
    except Exception as e:
        logger.error('loading api list data error! \n%s' % traceback.format_exc())

    return JsonResponse(api_list, safe=False)


# 同步SOA接口列表
@csrf_exempt
def sync_api_list(request):
    add_count = 0
    update_count = 0
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''
        if 'runEnv' in params:
            run_env = int(params['runEnv'])
        else:
            run_env = 1
        if 'startTime' in params:
            start_time = params['startTime']
        else:
            start_time = None
        if 'endTime' in params:
            end_time = params['endTime']
        else:
            end_time = None
        api_list = get_api_data(system_alias, run_env, start_time, end_time)

        all_projects = cmdb_util.get_all_projects_db()
        # 保存数据库
        count = 0
        for api_info in api_list:
            logger.info(u'发现应用: %s 的接口信息，正在同步...' % api_info['provider'])
            count += 1
            if count % 100 == 0:
                logger.info(u"已同步数据: %s" % count)
            api_name = api_info['topic']
            provider = api_info['provider']
            if provider not in all_projects:
                logger.warn(u'项目名称:%s 在CMDB中不存在! 已跳过...' % provider)
                continue
            # 检查接口是否已存在
            exist_api = ApiList.objects.filter(api_name=api_name)
            if exist_api.count() > 0:
                exist_api.update(updater='System')
                update_count += 1
            else:
                # 新增接口
                api_level = 'P3'
                if str(api_name).startswith('find'):
                    api_level = 'P1'
                ApiList(api_name=api_name, system_alias=provider, api_level=api_level,
                        creator=u'System', updater=u'System').save()
                add_count += 1
        logger.info(u'接口数据同步完成. 新增: %d, 更新: %d' % (add_count, update_count))
    except Exception as e:
        logger.error(u'sync api data error! \n%s' % traceback.format_exc())

    return JsonResponse({"add_count": add_count, "update_count": update_count}, safe=False)


# 自动生成测试计划
@csrf_exempt
def generate_testplan(request):
    try:
        params = request.GET or request.POST
        run_env = 2
        if 'runEnv' in params:
            run_env = int(params['runEnv'])

        t = threading.Thread(target=testplan_service.batch_create_testplan, args=(run_env,))
        t.setDaemon(True)
        t.start()
        result = {"code": 0, "message": '已经开始自动生成测试计划，请稍候查看!'}
    except Exception as e:
        msg = '自动生成测试计划失败！错误信息:\n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result)


# 自动生成接口测试用例
@csrf_exempt
def generate_testcase(request):
    try:
        params = request.GET or request.POST
        user = request.session['username'] if 'username' in request.session else 'System'
        system_alias = ''
        if 'systemAlias' in params and params['systemAlias'].strip() != '':
            system_alias = params['systemAlias']

        # 默认生成测试环境用例
        run_env = 2
        if 'runEnv' in params:
            run_env = int(params['runEnv'])

        result = testcase_service.batch_create(system_alias, run_env, user)
    except Exception as e:
        msg = '自动生成测试用例失败！错误信息:\n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 定时执行测试计划
@csrf_exempt
def scheduler_run_testplan(request):
    try:
        t = threading.Thread(target=testexecution_service.auto_run_testcase, args=())
        t.setDaemon(True)
        t.start()
        result = {"code": 0, "message": '已启动测试计划调度执行，请等待任务执行完成!'}
    except Exception as e:
        msg = '测试计划调度执行失败！错误信息:\n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result)


# 定时发送测试报告
@csrf_exempt
def scheduler_send_report(request):
    result = {}
    try:
        params = request.GET or request.POST
        today_str = datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')
        # 今天自动创建，且已启动的测试计划
        api_testplans = ApiTestplan.objects.filter(is_auto=1, is_delete=0, status__in=[1, 2],
                                                   create_time__gte=today_str,
                                                   update_time__gte=today_str)

        # 1. 全部测试报告发送给测试全员
        testplan_ids = ''
        for testplan in api_testplans:
            testplan_ids += '%s,' % testplan.id
        mail_list = ','.join(testreport_service.get_report_mail_list('All'))
        if config_env == 'dev':
            mail_list = 'gang.du@126.com'
        if testplan_ids != '':
            send_email('【接口测试平台邮件】接口每日回归测试报告_%s' % datetime.datetime.now().strftime('%Y年%m月%d日'),
                       testreport_service.get_summary_html(testplan_ids), mail_list, 'Test')
        else:
            logger.error('今天没有运行测试计划，无需发送邮件!')

        # 2. 胖猫云商事业部 测试报告发送
        testplan_ids = ''
        bu_name = '胖猫云商事业部'
        for testplan in api_testplans:
            testplan_info = testplan_service.get_testplan_info(testplan.id)
            if testplan_info['bu_name'] == bu_name:
                testplan_ids += '%s,' % testplan.id
        mail_list = ','.join(testreport_service.get_report_mail_list('胖猫云商事业部'))
        if config_env == 'dev':
            mail_list = 'gang.du@126.com'
        if testplan_ids != '':
            send_email('【接口测试平台邮件】%s_接口每日回归测试报告_%s' % (bu_name, datetime.datetime.now().strftime('%Y年%m月%d日')),
                       testreport_service.get_summary_html(testplan_ids), mail_list, 'Test')
        else:
            logger.warn('今天没有运行测试计划，无需发送邮件!')

        result = {"code": 0, "message": '定时发送测试报告邮件成功！'}

    except Exception, ex:
        msg = '定时发送测试报告邮件失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 备份数据库
@csrf_exempt
def backup_database(request):
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params and params['systemAlias'] != '' and 'testplanId' in params and params[
            'testplanId'] != '':
            system_alias = params['systemAlias'].strip()
            testplan_id = int(params['testplanId'].strip())

            testplans = ApiTestplan.objects.filter(id=testplan_id)
            if len(testplans) > 0:
                result = db_service.backup_database(testplan_id, system_alias)
            else:
                result = {"code": 1, "message": '参数错误：测试计划[%s]不存在!' % testplan_id}
        else:
            result = {"code": 1, "message": '参数testplanId、systemAlias必须输入!'}

    except Exception as e:
        msg = '备份数据表失败！错误信息:\n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result)


# 还原数据库
@csrf_exempt
def restore_database(request):
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params and params['systemAlias'] != '' and 'testplanId' in params and params[
            'testplanId'] != '':
            system_alias = params['systemAlias'].strip()
            testplan_id = int(params['testplanId'].strip())

            testplans = ApiTestplan.objects.filter(id=testplan_id)
            if len(testplans) > 0:
                result = db_service.restore_database(testplan_id, system_alias)
            else:
                result = {"code": 1, "message": '参数错误：测试计划[%s]不存在!' % testplan_id}
        else:
            result = {"code": 1, "message": '参数 systemAlias 必须输入!'}

    except Exception as e:
        msg = '还原数据表失败！错误信息:\n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result)


# 清理数据库
@csrf_exempt
def cleanup_database(request):
    try:
        params = request.GET or request.POST
        if 'systemAlias' in params and params['systemAlias'] != '':
            system_alias = params['systemAlias'].strip()

            result = db_service.cleanup_database(system_alias)
        else:
            result = {"code": 1, "message": '参数systemAlias必须输入!'}

    except Exception as e:
        msg = '清理备份数据表失败！错误信息:\n%s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result)


# 数据库配置页面
def db_config_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        context = {
            'systemAlias': system_alias,
        }

        return render(request, 'admin/db_config.html', context)
    except Exception, ex:
        logger.error("加载数据库配置页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


@csrf_exempt
def db_config_datagrid(request):
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

        result = db_service.config_datagrid(system_alias, page, size)
    except:
        logger.error("加载数据库配置表格失败！ 错误信息: \n%s" % traceback.format_exc())
        result = {"total": 0, "rows": []}

    return MyJsonResponse(result, safe=False)


# 保存配置
@csrf_exempt
def save_config(request):
    try:
        params = request.GET or request.POST
        config_dto = {
            'user': request.session['username'] if 'username' in request.session else 'System',
            'id': params['id'], 'run_env': params['run_env'],
            'system_alias': params['system_alias'] if 'system_alias' in params else '',
            'db_host': params['db_host'], 'db_port': params['db_port'], 'db_name': params['db_name'],
            'db_user': params['db_user'], 'db_pwd': params['db_pwd'],
        }
        result = db_service.edit(config_dto)
    except Exception, ex:
        msg = '保存数据库配置失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 删除配置
@csrf_exempt
def remove_config(request):
    result = {}
    try:
        params = request.GET or request.POST

        id = ''
        if 'id' in params and params['id'] != '':
            id = params['id']

        result = db_service.remove(id)
        logger.info('删除数据库配置成功！')
    except Exception, ex:
        msg = '删除数据库配置失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {'code': 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 数据库配置页面
def db_config_page_yapi(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        context = {
            'systemAlias': system_alias,
        }

        return render(request, 'yapi/db_config.html', context)
    except Exception, ex:
        logger.error("加载数据库配置页面失败! \n%s" % traceback.format_exc())
        return redirect('/')


# 数据库查询API
@csrf_exempt
def dbapi_query(request):
    try:
        params = request.POST

        db_key = ''
        if 'key' in params and params['key'] != '':
            db_key = int(params['key'])

        sql = ''
        if 'sql' in params and params['sql'] != '':
            sql = params['sql']
        if db_key and sql:
            result = mysql_util.query_db(db_key, sql)
        else:
            result = {'code': 1, "message": u'参数错误. 参数key和sql的值不能为空！'}

        logger.info('调用数据库API查询成功！%s' % json.dumps(sql))
    except Exception, ex:
        msg = '调用数据库API查询失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {'code': 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 数据库更新API
@csrf_exempt
def dbapi_update(request):
    try:
        params = request.POST

        db_key = ''
        if 'key' in params and params['key'] != '':
            db_key = int(params['key'])

        sql = ''
        if 'sql' in params and params['sql'] != '':
            sql = params['sql']
        if db_key and sql:
            result = mysql_util.update_db(db_key, sql)
        else:
            result = {'code': 1, "message": u'参数错误. 参数key和sql的值不能为空！'}

        logger.info('调用数据库更新API成功！%s' % json.dumps(sql))
    except Exception, ex:
        msg = '调用数据库更新API失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {'code': 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 数据库连接测试
@csrf_exempt
def db_connect(request):
    try:
        params = request.POST
        db_host = params['db_host']
        db_port = params['db_port']
        db_user = params['db_user']
        db_pwd = params['db_pwd']
        db_name = params['db_name']

        result = mysql_util.conn_db(db_host, db_port, db_user, db_pwd, db_name, 'select 1')
    except Exception, ex:
        msg = '连接数据库失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {"code": 1, "message": msg}

    return MyJsonResponse(result, safe=False)


# 数据库验证API
@csrf_exempt
def dbapi_verify(request):
    try:
        params = request.POST

        db_key = ''
        if 'key' in params and params['key'] != '':
            db_key = int(params['key'])

        sql = ''
        if 'sql' in params and params['sql'] != '':
            sql = params['sql']

        expected_value = {}
        if 'value' in params and params['value'] != '':
            expected_value = params['value']
        if db_key and sql and expected_value:
            result = mysql_util.query_db(db_key, sql)
            if type(expected_value) != dict:
                expected_value = json.loads(expected_value)
            for item in expected_value:
                value = jsonpath.jsonpath(result, item)
                if type(value) == list:
                    value = value[0]
                if str(expected_value[item]) == str(value):
                    result = {"code": 0, "message": u'数据库验证成功'}
                    continue
                else:
                    result = {"code": 1, "message": u'数据库验证失败. 期望值: %s, 实际值: %s' % (expected_value[item], value)}
                    break
        else:
            result = {'code': 1, "message": u'参数错误. 参数key和sql的值不能为空！'}

        logger.info('调用数据库验证API成功！%s' % json.dumps(sql))
    except Exception, ex:
        msg = '调用数据库验证API失败! %s' % traceback.format_exc()
        logger.error(msg)
        result = {'code': 1, "message": msg}

    return MyJsonResponse(result, safe=False)
