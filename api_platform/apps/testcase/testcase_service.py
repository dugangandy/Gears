# -*-coding:utf-8 -*-
import json

import jsonschema
import testexecution_service
from api_platform.apps.data_service import httplb_util
from utils import *


# 删除测试用例
def remove(testcase_id):
    if testcase_id == '':
        result = {'code': 1, 'message': 'testcase id不能为空.'}
    else:
        ApiTestcases.objects.filter(id=testcase_id).update(is_delete=1, update_time=datetime.datetime.now())
        result = {'code': 0, 'message': '删除测试用例成功'}

    return result


# 根据测试用例ID获取用例详情
def get_testcase_info(id):
    testcase_info = {}
    testcase = ApiTestcases.objects.get(id=id)
    if testcase:
        api_id = testcase.api_id
        params_id = testcase.params_id

        api_info = ApiList.objects.get(id=api_id)
        if api_info:
            testcase_info['api_name'] = api_info.api_name
            testcase_info['system_alias'] = api_info.system_alias
            testcase_info['method'] = api_info.method
            testcase_info['summary'] = testcase.summary
            testcase_info['case_id'] = testcase.id
            testcase_info['protocol_type'] = api_info.protocol_type
            testcase_info['request_header'] = api_info.request_header

        api_params = ApiParams.objects.get(id=params_id)
        if api_params:
            testcase_info['request_data'] = api_params.request_data
            testcase_info['expect_response_data'] = api_params.response_data
            testcase_info['expect_status_code'] = api_params.status_code
            testcase_info['run_env'] = api_params.run_env

    return testcase_info


def datagrid(testcase_dto):
    system_alias = testcase_dto['system_alias']
    api_name = testcase_dto['api_name']
    api_level = testcase_dto['api_level']
    show_enabled = testcase_dto['show_enabled']
    page_num = testcase_dto['page']
    page_size = testcase_dto['size']
    start_pos = (page_num - 1) * page_size
    end_pos = start_pos + page_size

    api_id_list = []
    api_list = ApiList.objects.filter(system_alias=system_alias)
    if api_name != '':
        api_list = api_list.filter(api_name=api_name)
    if api_level != '':
        api_list = api_list.filter(api_level=api_level)

    if api_list and len(api_list) > 0:
        for api_info in api_list:
            api_id_list.append(api_info.id)

    testcases = ApiTestcases.objects.filter(api_id__in=api_id_list, is_delete=0).order_by("-update_time")
    # 显示已启用
    if show_enabled == 1:
        testcases = testcases.filter(status=1)

    testcase_list = []
    for index in range(start_pos, end_pos):
        if (index + 1) > len(testcases):
            break
        testcase_info = testcases[index]

        params_info = ApiParams.objects.get(id=testcase_info.params_id)
        if params_info:
            # 获取检查点个数
            checkpoint_count = TestcaseCheckpoint.objects.filter(testcase_id=testcase_info.id).count()

            row = {"id": testcase_info.id, "summary": testcase_info.summary, "env": env_dict[params_info.run_env],
                   "api_name": ApiList.objects.get(id=testcase_info.api_id).api_name,
                   "request_data": params_info.request_data, "response_data": params_info.response_data,
                   "status_code": params_info.status_code, "updater": testcase_info.updater,
                   "checkpoint_count": checkpoint_count, "status": testcase_info.status,
                   "update_time": utc2local(testcase_info.update_time).strftime('%Y-%m-%d %H:%M:%S')}
            testcase_list.append(row)

    return {"total": len(testcases), "rows": testcase_list}


# 新增/修改用例
def edit(params,func_type=None,apis=None):
    if func_type is not None:
        testcase_list = []
        # 测试用例ID
        if apis is not None:
           for index in apis:
            # 新增用例
            if len(index) > 0:
                testcase = ApiTestcases(summary=index['api_name'], params_id=index['params_id'],
                                        api_id=index['api_id'], is_delete=0,status=0,creator='System', updater='System')
                testcase.save()
                logger.info('新增用例成功!')
                testcase_list.append(testcase)
            else:
                logger.warn('API信息有误. %s' % apis)
        return testcase_list

    code = 0
    msg = ''
    # 测试用例ID
    testcase_id = ''
    if 'id' in params and params['id'] != '':
        testcase_id = params['id']

    api_name = params['api_name'] if 'api_name' in params else ''
    if testcase_id == '':
        # 新增用例
        api_list = ApiList.objects.filter(api_name=api_name, is_delete=0)
        if len(api_list) > 0:
            api_id = api_list[0].id
            api_params = ApiParams(request_data=params['request_data'], response_data=params['response_data'],
                                   status_code=200, api_id=api_id, source='user', run_env=config_env_dict[config_env])
            api_params.save()
            param_id = api_params.id

            testcase = ApiTestcases(summary=params['summary'], params_id=param_id, api_id=api_id, is_delete=0)
            testcase.save()
            logger.info('新增用例成功!')
        else:
            logger.warn('获取API信息失败. %s' % api_name)
    else:
        testcase = ApiTestcases.objects.get(id=testcase_id)
        if testcase:
            if 'summary' in params:
                testcase.summary = params['summary']
            params_id = testcase.params_id
            api_params = ApiParams.objects.get(id=params_id)
            if api_params:
                if 'request_data' in params:
                    api_params.request_data = params['request_data']
                if 'response_data' in params:
                    api_params.response_data = params['response_data']
                api_params.save()
            else:
                msg = 'params id： %s 不存在!' % params_id
                code = 1
                logger.error(msg)

            testcase.update_time = datetime.datetime.now()
            testcase.updater = params['user'] if 'user' in params else ''
            testcase.save()
            msg = '保存测试用例成功'
        else:
            msg = 'testcase id: %s 不存在!' % testcase_id
            code = 1

    return {"code": code, "message": msg}


# 根据接口id自动创建测试用例
def create(api_id, run_env, user='System'):
    msg = ''
    code = 0

    api_info = ApiList.objects.get(id=api_id)
    params_list = ApiParams.objects.filter(api_id=api_id, run_env=run_env).order_by('-create_time')
    if len(params_list) > 0:
        # 选择最新的一个参数
        params_info = params_list[0]
        testcase = ApiTestcases.objects.filter(api_id=api_id, params_id=params_info.id, is_delete=0)
        if testcase and len(testcase) > 0:
            # logger.warn(u'用例已存在. %s' % testcase)
            msg = u'用例已存在. 参数id: %s' % params_info.id
        else:
            testcase = ApiTestcases(api_id=api_id, params_id=params_info.id, summary=api_info.api_name,
                                    creator=user, updater=user)
            testcase.save()
    else:
        msg = u'没有找到匹配的参数. api_id: %s, run_env: %s<br>' % (api_id, run_env)
        logger.warn(msg)
        code = 1
    return {"code": code, "message": msg}


def batch_create(system_alias, run_env, user):
    add_count = 0
    fail_count = 0
    code = 0
    err_msg = ''

    logger.info(u'开始自动生成应用[%s]的接口用例...' % system_alias)
    project_list = []
    if system_alias != '':
        project_list.append(system_alias)
    else:
        project_list = [api['system_alias'] for api in
                        ApiList.objects.filter(is_delete=0).values('system_alias').distinct()]
    api_list = []
    for project in project_list:
        api_list.extend(ApiList.objects.filter(is_delete=0, system_alias=project))

    for api_info in api_list:
        result = create(api_info.id, run_env, user)
        if result['code'] == 0:
            add_count += 1
        elif result['code'] == 1:
            fail_count += 0
            err_msg += '<br>%s' % result['message']

    msg = '本次生成用例数： %s， 失败数：%s。<br>%s' % (add_count, fail_count, err_msg)
    logger.info(msg)
    if fail_count > 1:
        code = 1

    return {"code": code, "message": msg}


# 检查点表格
def checkpoint_datagrid(testcase_id):
    checkpoints = TestcaseCheckpoint.objects.filter(testcase_id=testcase_id).order_by("-weight")

    checkpoint_list = []
    for checkpoint in checkpoints:
        check_type_str = 'NA'
        if checkpoint.check_type in check_type_dict:
            check_type_str = check_type_dict[checkpoint.check_type]
        row = {"id": checkpoint.id, "check_type": checkpoint.check_type, "check_type_str": check_type_str,
               "check_param": checkpoint.check_param,
               "operate": checkpoint.operate, "expect_value": checkpoint.expect_value, "updater": checkpoint.updater,
               "update_time": utc2local(checkpoint.update_time).strftime('%Y-%m-%d %H:%M:%S')}
        checkpoint_list.append(row)

    return {"total": len(checkpoints), "rows": checkpoint_list}


# 删除检查点
def remove_checkpoint(id):
    if id == '':
        result = {'code': 1, 'message': '检查点id不能为空.'}
    else:
        testcase_checkpoint = TestcaseCheckpoint.objects.filter(id=id)
        testcase_checkpoint.delete()
        result = {'code': 0, 'message': '删除测试用例检查点成功'}

    return result


# 新增/修改用例检查点
def edit_checkpoint(params):
    code = 0
    msg = ''
    # 检查点点ID
    checkpoint_id = ''
    if 'id' in params and params['id'] != '':
        checkpoint_id = params['id']

    if checkpoint_id == '':
        # 新增检查点
        check_type = params['check_type']
        TestcaseCheckpoint(testcase_id=params['testcaseId'], check_type=check_type, check_param=params['check_param'],
                           operate=params['operate'] if check_type == 'json' else '',
                           expect_value=params['expect_value'] if check_type == 'json' else '', weight=100,
                           ).save()
        logger.info('新增用例检查点成功!')
    else:
        checkpoint = TestcaseCheckpoint.objects.get(id=checkpoint_id)
        if checkpoint:
            checkpoint.check_type = params['check_type']
            checkpoint.check_param = params['check_param']
            if params['check_type'] == 'json':
                checkpoint.operate = params['operate']
                checkpoint.expect_value = params['expect_value']
            else:
                checkpoint.operate = ''
                checkpoint.expect_value = ''

            checkpoint.update_time = datetime.datetime.now()
            checkpoint.updater = params['user'] if 'user' in params else ''
            checkpoint.save()
            msg = '保存用例检查点成功'
        else:
            msg = '检查点: %s 不存在!' % checkpoint_id
            code = 1

    return {"code": code, "message": msg}


# 测试运行
def test_testcase(testcase_id):
    try:
        code = 0
        message = ''
        data = {}
        diff_result = ''

        testcase_info = get_testcase_info(testcase_id)
        url = testcase_info['api_name']
        request_data = testcase_info['request_data']

        data['id'] = testcase_id
        data['api_name'] = url
        data['request_data'] = request_data
        data['method'] = testcase_info['method']
        data['client_ip'] = testexecution_service.client_ip
        data['execute_time'] = datetime.datetime.now()

        request_header = {}
        try:
            if str(testcase_info['request_header']) != '':
                request_header = json.loads(str(testcase_info['request_header']))
        except:
            logger.warn(u'解析请求头数据失败！ %s' % testcase_info['request_header'])

        response_data = ''
        server_ip = ''
        domain = testexecution_service.get_project_domain(testcase_info['system_alias'], testcase_info['run_env'])
        if domain:
            if domain.find('http://') == -1:
                domain = "http://%s" % domain

            host_list = [domain]

            response = httplb_util.ha_request(method=testcase_info['method'], server_list=host_list,
                                              url=url, data=str(request_data), request_header=request_header)

            if response is not None:
                status_code = response.status_code
                response_data = str(response.content)
                data['status_code'] = status_code
                data['response_data'] = response_data

                if status_code == testcase_info['expect_status_code']:
                    code = 0
                else:
                    code = 1
                    message = u'status code 与期望值不同!'

                if status_code == 200:
                    # 判断是否json
                    try:
                        response_data_json = json.loads(response_data)
                        expect_response_data = {}
                        try:
                            expect_response_data = json.loads(str(testcase_info['expect_response_data']))
                        except:
                            pass

                        data['expect_response_data'] = expect_response_data
                        try:
                            # 检查json schema是否一致
                            jsonschema_json = get_jsonschema(expect_response_data)
                            # logger.info(jsonschema_json)
                            jsonschema.validate(response_data_json, jsonschema_json)
                            jsonschema_result = u'jsonschema校验通过.'
                        except Exception, ex:
                            jsonschema_result = u'jsonschema校验不通过! %s' % traceback.format_exc()
                            logger.warn(jsonschema_result)
                            message += jsonschema_result
                            code = 1
                        data['jsonschema_result'] = jsonschema_result

                        # 判断检查点
                        checkpoint_result = ''
                        checkpoints = TestcaseCheckpoint.objects.filter(testcase_id=testcase_id)
                        for checkpoint in checkpoints:
                            if checkpoint.check_type == 'json' and \
                                    testexecution_service.json_validate(response_data, checkpoint.check_param,
                                                                        checkpoint.operate, checkpoint.expect_value):
                                checkpoint_msg = u"json校验成功！[%s %s %s]" % (
                                    checkpoint.check_param, checkpoint.operate, checkpoint.expect_value)
                                logger.info(checkpoint_msg)
                            else:
                                checkpoint_msg = u"json校验失败！[%s %s %s]" % (
                                    checkpoint.check_param, checkpoint.operate, checkpoint.expect_value)
                                logger.warn(checkpoint_msg)
                                message += checkpoint_msg
                                code = 1
                            # 记录检查点结果
                            checkpoint_result += checkpoint_msg + '<br>'

                        data['checkpoint_result'] = checkpoint_result if checkpoint_result != '' else u'无检查点.'
                        # message += json.dumps(checkpoint_result, ensure_ascii=False)

                        # 得出完全diff结果
                        diff_result = ''
                        try:
                            diff_result = testexecution_service.diff_response_data(json.loads(response_data), expect_response_data)
                        except Exception:
                            logger.error('比对结果出现错误! %s' % traceback.format_exc())
                        data['diff'] = diff_result

                    except:
                        logger.warn(traceback.format_exc())
                        # 按字符串比对
                        expect_response_data = str(testcase_info['expect_response_data'])
                        if response_data == expect_response_data or response_data.find(expect_response_data) > -1:
                            code = 0
                            logger.info(u'返回值与预期值相同!')
                        else:
                            code = 1
                            logger.warn(u'返回值与预期值不同!')

                else:
                    message = u"返回状态码: %s" % status_code
            else:
                code = 1
                message = u'服务器无响应数据'
        else:
            logger.warn(u'执行测试用例失败! 原因：项目域名为空')
            code = 1
            message = u'项目域名为空'

        logger.info(u"测试返回值：%s, 信息: %s" % (code, message))
    except:
        code = 1
        logger.error(u'执行测试用例出错！ %s' % traceback.format_exc())

    data['message'] = message
    if code == 0:
        data['result'] = 'success'
    else:
        data['result'] = 'fail'
    return {"code": code, "message": message, "data": data}


# 启用/禁用测试用例
def enable(id):
    code = 0
    message = ''
    testcase = ApiTestcases.objects.get(id=id)
    if testcase:
        status = testcase.status
        testcase.status = 1 if not status else 0
        testcase.save()
        if testcase.status == 1:
            message = '测试用例已启用！'
        else:
            message = '测试用例已禁用。'
        logger.info(message)
    else:
        code = 1
        message = '测试用例不存在，请检查数据! ID: %s' % id
        logger.error(message)

    return {"code": code, "message": message}
