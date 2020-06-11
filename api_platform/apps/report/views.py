# -*-coding:utf-8 -*-
from django.shortcuts import render

from api_platform.apps.testcase.utils import *

# reload(sys)
# sys.setdefaultencoding('utf8')

logger = logging.getLogger('gears.app')

ENV_DICT = {'prod': 1, "sit": 2, "mit": 3, "uat": 4, "dev": 5}
env_txt_dict = {'prod': u'生产', "sit": 'SIT', "mit": 'MIT', "uat": 'UAT', "dev": u'开发'}


# 测试大盘
def dashboard_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        # 设置运行环境
        env = 'prod'
        if 'env' in params and params['env'].strip() != '':
            env = params['env']

        # 计算前一天数据
        start_time = "%s 00:00:00" % (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        end_time = "%s 00:00:00" % datetime.datetime.now().strftime('%Y-%m-%d')
        # 接入应用数
        alias_sum = ApiList.objects.filter(is_delete=0).values('system_alias').distinct().count()
        alias_old_count = ApiList.objects.filter(is_delete=0, create_time__lt=start_time).values(
            'system_alias').distinct().count()
        alias_add_count = alias_sum - alias_old_count

        # 接口数
        api_sum = ApiList.objects.filter(is_delete=0).values('api_name').distinct().count()
        api_add_count = ApiList.objects.filter(is_delete=0, create_time__range=(start_time, end_time)).values(
            'api_name').distinct().count()

        # 测试用例数
        testcase_sum = ApiTestcases.objects.filter(is_delete=0).count()
        testcase_add_count = ApiTestcases.objects.filter(is_delete=0, create_time__range=(start_time, end_time)).count()

        # 测试执行次数
        execution_sum = ApiExecution.objects.filter(status=2).count()
        execution_add_count = ApiExecution.objects.filter(status=2, create_time__range=(start_time, end_time)).count()

        statics_data = {
            'alias_sum': alias_sum,
            'alias_add_count': alias_add_count,
            'api_sum': api_sum,
            'api_add_count': api_add_count,
            'testcase_sum': testcase_sum,
            'testcase_add_count': testcase_add_count,
            'execution_sum': execution_sum,
            'execution_add_count': execution_add_count,
        }

        context = {
            'systemAlias': system_alias,
            'staticsData': statics_data,
        }

        return render(request, 'report/dashboard.html', context)
    except Exception, ex:
        logger.error("加载接口测试大盘失败! \n%s" % traceback.format_exc())
        return render(request, '404.html', context)


# 应用接口大盘
def dashboard_project_page(request):
    params = request.GET or request.POST
    try:
        if 'systemAlias' in params:
            system_alias = params['systemAlias']
        else:
            system_alias = ''

        # 设置运行环境
        env = 'prod'
        if 'env' in params and params['env'].strip() != '':
            env = params['env']

        # 计算前一天数据
        start_time = "%s 00:00:00" % (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        end_time = "%s 00:00:00" % datetime.datetime.now().strftime('%Y-%m-%d')

        # 接口数
        api_sum = ApiList.objects.filter(is_delete=0, system_alias=system_alias).values('api_name').distinct().count()
        api_add_count = ApiList.objects.filter(is_delete=0, system_alias=system_alias,
                                               create_time__range=(start_time, end_time)).values(
            'api_name').distinct().count()

        # 测试用例数
        api_id_list = [api['id'] for api in ApiList.objects.filter(is_delete=0, system_alias=system_alias).values('id')]
        testcase_sum = ApiTestcases.objects.filter(is_delete=0, api_id__in=api_id_list).count()
        testcase_add_count = ApiTestcases.objects.filter(is_delete=0, api_id__in=api_id_list,
                                                         create_time__range=(start_time, end_time)).count()

        # 测试执行次数
        testcase_id_list = [testcase['id'] for testcase in
                            ApiTestcases.objects.filter(is_delete=0, api_id__in=api_id_list).values('id')]
        execution_sum = ApiExecution.objects.filter(status=2, testcase_id__in=testcase_id_list).count()
        execution_add_count = ApiExecution.objects.filter(status=2, testcase_id__in=testcase_id_list,
                                                          create_time__range=(start_time, end_time)).count()

        statics_data = {
            'api_sum': api_sum,
            'api_add_count': api_add_count,
            'testcase_sum': testcase_sum,
            'testcase_add_count': testcase_add_count,
            'execution_sum': execution_sum,
            'execution_add_count': execution_add_count,
        }

        context = {
            'systemAlias': system_alias,
            'staticsData': statics_data,
        }

        return render(request, 'report/dashboard_project.html', context)
    except Exception, ex:
        logger.error("加载应用接口测试大盘失败! \n%s" % traceback.format_exc())
        return render(request, '404.html', context)
