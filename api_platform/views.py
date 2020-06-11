# -*-coding:utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt

from api_platform.apps.data_service.global_var import *
from api_platform.apps.testcase.utils import *

reload(sys)
sys.setdefaultencoding('utf8')

logger = logging.getLogger('gears.app')
env = config.get('runtime', 'env')
logOutURL = '/logout'

mailFrom = config.get('others', 'default_from_mail')
cacheEnable = int(config.get('cache', 'enable'))

debug_mode = json.loads(config.get('runtime', 'debug'))


@csrf_exempt
def health_check(request):
    return JsonResponse("OK!", safe=False)


# Create your views here.
# 退出系统
def logout(request):
    session = request.session
    if session and 'username' in session:
        session.delete()
    return HttpResponseRedirect("/")


# 基于标签页的首页
def index_v2(request):
    session = request.session
    if 'lat_name' in session:
        username = session['lat_name']
        if username in [u'杜刚', u'王杰', u'廖茜']:
            role = u'超级管理员'
        else:
            role = u'授权用户'
    else:
        username = u'访客'
        role = u''

    context = {
        'username': username,
        'role': role
    }
    return render(request, 'portal.html', context)


# 应用首页
def project_index(request):
    session = request.session
    params = request.GET
    if 'name' in params and params['name'] != '':
        system_alias = params['name']
    else:
        return render(request, 'portal.html', context)

    if 'lat_name' in session:
        username = session['lat_name']
        if username in [u'杜刚', u'王培安', u'彭海平']:
            role = u'超级管理员'
        else:
            role = u'授权用户'
    else:
        username = u'访客'
        role = u''

    context = {
        'username': username,
        'role': role,
        'systemAlias': system_alias,
    }
    return render(request, 'project/index.html', context)


def skin_config(request):
    return render_to_response('skin_config.html')


@csrf_exempt
def cmdb_projects(request):
    projects = cmdb_util.get_all_projects_db()
    return JsonResponse({"total": len(projects), "rows": projects}, safe=False)


@csrf_exempt
def cmdb_productlines(request):
    bu_list = []
    try:
        productlines = cmdb_util.getAllProductlines()
        for bu in productlines:
            if bu['bu_name'] not in exclude_bu_list:
                bu_list.append(bu)
    except:
        logger.error("加载业务线失败! %s" % traceback.format_exc())

    return JsonResponse({"total": len(bu_list), "rows": bu_list}, safe=False)


# 获取运行环境列表
@csrf_exempt
def get_env_list(request):
    env_list = [{"value": '1', "text": '生产'},
                {"value": '2', "text": '测试'},
                {"value": '4', "text": 'UAT'},
                {"value": '3', "text": 'MIT'},
                {"value": '8', "text": 'STG'}]

    return JsonResponse(env_list, safe=False)
