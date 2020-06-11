# -*-coding:utf-8 -*-

from api_platform.apps.data_service.models import *
from utils import *


def api_datagrid(system_alias, api_level, api_name, page_num, page_size):
    start_pos = (page_num - 1) * page_size
    end_pos = start_pos + page_size

    api_id_list = []
    api_list = ApiList.objects.filter(is_delete=0).order_by('-update_time')
    if system_alias != '':
        api_list = api_list.filter(system_alias=system_alias)

    if api_level in ['P1', 'P2', 'P3', 'P4']:
        api_list = api_list.filter(api_level=api_level)

    if api_name != '':
        api_list = api_list.filter(api_name__icontains=api_name)

    rows = []
    for index in range(start_pos, end_pos):
        if (index + 1) > len(api_list):
            break
        api_info = api_list[index]

        if api_info:
            row = {"id": api_info.id, "api_name": api_info.api_name, "system_alias": api_info.system_alias,
                   "updater": api_info.updater, "api_level": api_info.api_level, "method": api_info.method,
                   "api_desc": api_info.api_desc, "request_header": api_info.request_header,
                   "update_time": utc2local(api_info.update_time).strftime('%Y-%m-%d %H:%M:%S')}
            rows.append(row)

    return {"total": len(api_list), "rows": rows}


# 新增/修改接口
def edit(params):
    code = 0
    msg = ''
    # API ID
    api_id = ''
    if 'id' in params and params['id'] != '':
        api_id = params['id']

    user = params['user'] if 'user' in params else ''
    api_name = str(params['api_name'])
    # 新增接口
    if api_id == '':
        try:
            api_info = ApiList.objects.filter(is_delete=0, api_name=api_name,system_alias=params['system_alias'])
            if len(api_info) > 0:
                raise Exception('接口[%s]已存在.' % api_name)
            api_info = ApiList(api_name=api_name, api_desc=params['api_desc'], method=params['method'],
                               system_alias=params['system_alias'], api_level=params['api_level'],
                               creator=user, updater=user, request_header=params['request_header'])
            api_info.save()
            msg = u'新增接口成功. %s' % api_info.api_name
        except Exception, ex:
            code = 1
            msg = u'新增接口失败! 报错信息:<br>%s' % ex.message
            logger.error(msg)

    else:
        api_info = ApiList.objects.get(id=api_id)
        if api_info:
            api_info.api_desc = params['api_desc']
            api_info.api_level = params['api_level']
            api_info.method = params['method']
            api_info.request_header = params['request_header']
            api_info.update_time = datetime.datetime.now()
            api_info.updater = user
            api_info.api_name = api_name
            api_info.save()
            msg = u'保存接口成功'
        else:
            msg = u'api id: %s 不存在!' % api_id
            code = 1

    return {"code": code, "message": msg}


# 删除接口
def remove(id):
    code = 0
    msg = ''
    api_info = ApiList.objects.get(id=id)
    if api_info:
        api_info.is_delete = 1
        api_info.save()
        msg = u'删除接口成功'
    else:
        msg = u'api id: %s 不存在!' % id
        code = 1
    return {"code": code, "message": msg}
