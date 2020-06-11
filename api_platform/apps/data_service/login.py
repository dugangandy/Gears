# coding=utf-8
import json
import logging
import time
import traceback

import requests
from django.http import HttpResponseRedirect
from api_platform.libs import config

from api_platform.apps.data_service.models import UserLog

logger = logging.getLogger('gears.app')

loginUrl = config.get('others', 'zg_sso_url')
env = config.get('runtime', 'env')
debug_mode = config.getboolean('runtime', 'debug')


class SessionCheck(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(SessionCheck, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

    def put_sso_user(self, token, request):
        content = self.get_sso_user(token)
        if 'operatorVo' in content:
            session = request.session
            session['token'] = token
            op_info = content['operatorVo']
            session['ip'] = op_info['ip']
            session['lat_name'] = op_info['operatorName']
            session['username'] = op_info['operatorLoginName']
            if 'jobName' in op_info:
                session['job_name'] = op_info['jobName']
            if 'mobile' in op_info:
                session['mobile'] = op_info['mobile']
            if 'operatorEmail' in op_info:
                session['email'] = op_info['operatorEmail']
            if 'departmentName' in op_info:
                session['dept'] = op_info['departmentName']
            session.save()

    def get_sso_user(self, token):
        headers = {'Content-type': 'application/json', 'charset': 'utf-8'}
        data = {'zg_sso_token': token}
        result = requests.post(loginUrl + '/platform.information.sso.ui/sso/getOperatorBySsoKey',
                               data=json.dumps(data), headers=headers, timeout=10)
        logger.info(result.json())
        return json.loads(result.content)

    def process_request(self, request):
        try:
            if env == 'test':
                return None
            session = request.session
            params = request.GET or request.POST
            if 'zg_sso_token' in params:
                self.put_sso_user(params['zg_sso_token'], request)
            if 'lat_name' in session:
                # 保存数据库日志
                self.save_log(request)
                return None
            abs_url = request.build_absolute_uri()
            # logger.info(abs_url)
            # 不检查登录session
            if abs_url.find('/check.txt') != -1 or abs_url.find('/report') != -1 or abs_url.find('/cmdb') != -1 \
                    or abs_url.find('/data/') != -1 or abs_url.find('/ui/') != -1:
                return None
            # 模拟环境
            if env == 'pre':
                session['username'] = 'mock_user'
                session['lat_name'] = u'模拟环境用户'
                return None

            # if debug_mode:
            #     return None
            logger.debug(loginUrl)

            return HttpResponseRedirect(loginUrl + '/login?redirectUrl=' + abs_url)
        except:
            logger.error('exception. %s' % traceback.format_exc())
            return None

    # 记录访问日志
    def save_log(self, request):
        try:
            session = request.session
            user_log = UserLog(user_name=session['lat_name'], login_name=session['username'], client_ip=session['ip'],
                               user_token=session['token'], access_url=request.build_absolute_uri()[0:1024])
            user_log.save()

            logger.info(u'用户名: %s, 客户端IP: %s, 访问URL: %s, 参数: %s, Token: %s, 操作时间: %s}' %
                        (session['lat_name'], session['ip'], request.build_absolute_uri(), request.GET or request.POST,
                         session['token'], time.strftime('%Y-%m-%d %H:%M:%S')))
        except Exception, e:
            logger.info(session)
            logger.error(u"写入日志失败.\n%s" % traceback.format_exc())
