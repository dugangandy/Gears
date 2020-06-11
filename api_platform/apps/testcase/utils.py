# -*-coding:utf-8 -*-
import sys
from django.http import JsonResponse
from api_platform.libs import config
from django.core.mail import send_mail
from django.conf import settings

from api_platform.apps.data_service import cmdb_util
from api_platform.apps.data_service.date_util import *
from api_platform.apps.data_service.models import *

logger = logging.getLogger('gears.app')
status_dict = {0: '未执行', 1: '正在执行', 2: '执行完成'}
env_dict = {1: '生产', 2: '测试', 3: 'MIT', 4: 'UAT'}
check_type_dict = {'json': 'JSON匹配', 'whole': '完全匹配', 'fuzzy': '模糊匹配'}

# 从配置中心取出当前环境
config_env = config.get('runtime', 'env')
config_env_dict = {"dev": 2, "test": 2, "uat": 4, "prd": 1}
config_env_code = config_env_dict[config_env]

project_count = Projects.objects.count()
logger.info(u'应用总数: %d' % project_count)


# 覆盖json response
def MyJsonResponse(result, safe=False):
    return JsonResponse(result, safe=safe, json_dumps_params={"ensure_ascii": False})


def get_jsonschema(json_object):
    jsonschema = {
        "$id": "http://example.com/example.json",
        "type": "object",
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#"
    }
    try:
        jsonschema["properties"] = prase_jsonschema_prop(json_object)
    except:
        logger.warn("get jsonschema failed! %s" % traceback.format_exc())

    return jsonschema


# 根据json对象生成jsonschema
def prase_jsonschema_prop(json_object):
    properties = {}
    if isinstance(json_object, dict):
        for n1 in json_object:
            value = json_object[n1]
            if isinstance(value, dict):
                properties[n1] = {
                    "type": "object",
                    "properties": prase_jsonschema_prop(value)
                }

            # 处理list
            elif isinstance(value, list):
                properties[n1] = {
                    "type": "array",
                }
                # list元素是dict or list
                if len(value) > 0:
                    if isinstance(value[0], (dict, list)):
                        properties[n1]["items"] = {
                            "type": "object",
                            "properties": prase_jsonschema_prop(value[0])
                        }
                    elif isinstance(value[0], basestring):
                        properties[n1]["items"] = {"type": "string"}
                    elif isinstance(value[0], float):
                        properties[n1]["items"] = {"type": "number"}
                    elif isinstance(value[0], bool):
                        properties[n1]["items"] = {"type": "boolean"}
                    elif isinstance(value[0], int):
                        properties[n1]["items"] = {"type": ["number", "integer"]}
                    elif isinstance(value, None):
                        properties[n1] = {"type": "null"}
                    else:
                        properties[n1]["items"] = {"type": "string"}

            elif isinstance(value, basestring):
                properties[n1] = {"type": "string"}
            elif isinstance(value, float):
                properties[n1] = {"type": "number"}
            elif isinstance(value, bool):
                properties[n1] = {"type": "boolean"}
            elif isinstance(value, int):
                properties[n1] = {"type": ["number", "integer"]}
            elif isinstance(value, None):
                properties[n1] = {"type": "null"}
            else:
                properties[n1] = {
                    "type": "string"
                }
    else:
        logger.warn("%s 数据类型未知!" % json_object)
        properties = {
            "type": "string"
        }
    return properties


def mail_notify(subject, message, to_maillist):
    # send_mail的参数分别是  邮件标题，邮件内容，发件箱(settings.py中设置过的那个)，收件箱列表(可以发送给多个人),失败静默(若发送失败，报错提示我们)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to_maillist, fail_silently=False)
