# -*-coding:utf-8 -*-

import jsonpath
import jsonschema
import requests
import threadpool

import project_service
import testcase_service
import testplan_service
from api_platform.apps.data_service import db_service
from api_platform.apps.data_service import httplb_util, ip_utils
from func_api import *
from utils import *

client_ip = ip_utils.get_host_ip()
status_dict = {0: '未执行', 1: '正在执行', 2: '执行完成'}
parallel_tesptlan_count = 4
parallel_testcase_count = 4
task_pool = threadpool.ThreadPool(parallel_tesptlan_count)


# 测试用例执行表格
def execution_datagrid(execution_dto):
    result = {"total": 0, "rows": []}
    testplan_id = execution_dto['testplan_id']
    page = execution_dto['page']
    size = execution_dto['size']
    order_by = execution_dto['sort']
    if execution_dto['order'] == 'desc':
        order_by = '-' + order_by

    if testplan_id != '':
        api_executions = ApiExecution.objects.filter(testplan_id=testplan_id).order_by(order_by)
        start_pos = (page - 1) * size
        end_pos = start_pos + size

        execution_list = []
        for index in range(start_pos, end_pos):
            if (index + 1) > len(api_executions):
                break
            execution = api_executions[index]
            execution_list.append(get_execution_info(execution.id))

        result = {"total": len(api_executions), "rows": execution_list}
    return result


# 执行单个测试用例
def run_execution(execution, host_domain, func_type=None, req_data=None, req=None):
    try:
        message = ''
        diff_result = ''
        # 保存状态、执行人
        execution.status = 1
        execution.save()
        testcase_id = execution.testcase_id
        testcase_info = testcase_service.get_testcase_info(testcase_id)

        url = testcase_info['api_name']
        # 判断是表单还是json格式的请求
        if '=' in str(testcase_info['request_data']):
            request_data = str(testcase_info['request_data'])

        else:
            try:
                request_data = eval(
                    str(testcase_info['request_data']).replace('null', 'None').replace('true', 'True').replace('false',
                                                                                                               'False'))
            except:
                request_data = testcase_info['request_data']
                logger.info(traceback.format_exc() + request_data)

            # request_data = eval(str(testcase_info['request_data']))

        if req_data is not None and len(req_data) >= 0 and '=' not in str(testcase_info['request_data']):
            for data in request_data:
                try:
                    request_data[data] = eval(str(request_data[data]))
                except:
                    pass
            request_data = json.dumps(request_data)
        request_header = {}
        try:
            if str(testcase_info['request_header']) != '':
                request_header = json.loads(str(testcase_info['request_header']))
        except:
            logger.warn('解析请求头数据失败！ %s' % testcase_info['request_header'])

        response_data = ''
        if host_domain:
            if host_domain.find("http://") == -1:
                host_domain = "http://%s" % host_domain
            host_list = [host_domain]

            response = httplb_util.ha_request(str(testcase_info['method']), host_list, url, str(request_data),
                                              request_header, func_type=func_type, req=req)

            if response is not None:
                status_code = response.status_code
                response_data = str(response.content)
                if status_code == testcase_info['expect_status_code']:
                    result = 'success'
                else:
                    result = 'fail'
                    message = 'status code 与期望值不同!'

                if 'html' in response.text or 'div' in response.text:
                    result = 'success'
                    message = '返回内容为网页，请查看测试报告'
                else:
                    if status_code == 200:
                        # 判断是否json
                        try:
                            response_data_json = json.loads(response_data)
                            # 检查业务状态码
                            if not check_response_message(response_data_json):
                                result = 'fail'
                                message = u'业务状态码错误! <br>%s' % \
                                          json.dumps(response_data_json['message'], ensure_ascii=False)
                            else:
                                # json校验
                                expect_response_data = {}
                                try:
                                    expect_response_data = json.loads(str(testcase_info['expect_response_data']))
                                except:
                                    pass

                                try:
                                    # 检查json schema是否一致
                                    jsonschema_json = get_jsonschema(expect_response_data)
                                    # logger.info(jsonschema_json)
                                    jsonschema.validate(response_data_json, jsonschema_json)
                                except Exception, ex:
                                    message = 'jsonschema校验不通过! %s' % traceback.format_exc()
                                    logger.warn(message)
                                    # result = 'fail'

                                # 检查点
                                checkpoints = TestcaseCheckpoint.objects.filter(testcase_id=testcase_id)
                                for checkpoint in checkpoints:
                                    if checkpoint.check_type == 'json' \
                                            and json_validate(response_data, checkpoint.check_param, checkpoint.operate,
                                                              checkpoint.expect_value):
                                        logger.info("json校验成功！[%s %s %s]" % (
                                            checkpoint.check_param, checkpoint.operate, checkpoint.expect_value))
                                    else:
                                        pass

                                # 得出完全diff结果
                                try:
                                    diff_result = diff_response_data(json.loads(response_data), expect_response_data)
                                except Exception:
                                    logger.error('比对结果出现错误! %s' % traceback.format_exc())
                        except:
                            # 按字符串比对
                            expect_response_data = str(testcase_info['expect_response_data'])
                            if response_data == expect_response_data or response_data.find(expect_response_data) > -1:
                                result = 'success'
                            else:
                                result = 'fail'

                    else:
                        message = u"返回状态码: %s" % status_code
            else:
                result = 'fail'
                status_code = -1
                message = '服务器无响应数据'
        else:
            logger.warn('执行测试用例失败! 原因：项目域名为空')
            result = 'fail'
            status_code = -1
            message = '项目域名为空'

        ApiExecution.objects. \
            filter(id=execution.id).update(request_data=request_data, response_data=response_data,
                                           status_code=status_code,
                                           result=result, diff=json.dumps(diff_result, ensure_ascii=False),
                                           execute_time=datetime.datetime.now(), status=2, server_ip=host_domain,
                                           client_ip=client_ip, message=message)

        logger.info("测试用例[id：%s]执行结果: %s" % (execution.testcase_id, result))
    except:
        result = 'fail'
        logger.error('执行测试用例出错！ %s' % traceback.format_exc())

    if func_type is None:  # 保留原有直接执行逻辑，增加分支逻辑，根据返回值的状态做相应处理
        return result
    elif "html" in response_data or 'div' in response_data:
        return {"result": '当前接口返回为网页内容，请查看测试报告', "code": result}
    else:
        try:
            response_data = response_data.replace('null', 'None').replace('true', 'True').replace('false', 'False')
            return {"result": eval(str(response_data)), "code": result}
        except:
            logger.info(response_data + traceback.format_exc())
            return {"result": response_data, "code": result}


def diff_response_data(response_data={}, expect_response={}):
    diff_detail = {}
    if isinstance(response_data, dict) and isinstance(expect_response, dict):
        # 期望值是否为空的dict
        if expect_response == {} and response_data != {}:
            return 'expect {} but found %s' % response_data

        for n1 in expect_response:
            # logger.info("n1: %s" % n1)
            if isinstance(expect_response[n1], dict):
                # logger.debug('dict')
                if n1 in response_data:
                    diff_detail[n1] = diff_response_data(response_data[n1], expect_response[n1])
                else:
                    diff_detail[n1] = 'expect exist but not found!'

            elif isinstance(expect_response[n1], list):
                # 实际结果没有key，或者value不是list
                if n1 not in response_data or not isinstance(response_data[n1], list):
                    diff_detail[n1] = 'expect list but not found!'

                # 比较list长度是否一致
                elif len(expect_response[n1]) != len(response_data[n1]):
                    diff_detail[n1] = 'list length not equal! response: %s, expect: %s' % (len(response_data[n1]),
                                                                                           len(expect_response[n1]))
                else:
                    for expect_index, expect_value in enumerate(expect_response[n1]):
                        # list最多检查3个
                        if expect_index > 2:
                            break
                        flag = False
                        for resp_index, resp_value in enumerate(response_data[n1]):
                            if isinstance(expect_value, dict):
                                if resp_index > 2:
                                    break
                                temp_diff = diff_response_data(resp_value, expect_value)
                                # diff_detail['%s-%s' % (n1, resp_index)] = temp_diff
                                if temp_diff == {}:
                                    flag = True
                                    break

                            elif isinstance(expect_value, list):
                                if expect_value == resp_value:
                                    flag = True
                                    break
                                # else:
                                #     diff_detail['%s-%s' % (n1, expect_index)] = "expect: %s but get: %s" \
                                #                                                 % (expect_value, resp_value,)
                            else:
                                if expect_value == resp_value:
                                    flag = True
                                    break
                                # else:
                                #     diff_detail['%s-%s' % (n1, expect_index)] = "expect: %s but get: %s" \
                                #                                                 % (expect_value, resp_value,)
                        if flag is False:
                            diff_detail['%s-%s' % (n1, expect_index)] = "expect: %s but get: %s" \
                                                                        % (expect_value, resp_value,)
            else:
                # print "string"
                if n1 in response_data and response_data[n1] == expect_response[n1]:
                    # diff_detail[n1] = 'equal'
                    continue
                else:
                    diff_detail[n1] = "expect: %s but get: %s" % \
                                      (expect_response[n1] if n1 in expect_response else '',
                                       response_data[n1] if n1 in response_data else '')
    else:
        diff_detail = 'not json data'
        logger.warn('not json data. response: %s' % response_data)

    # 去掉不必要的差异
    pure_diff_detail = {}
    if isinstance(diff_detail, dict):
        for n2 in diff_detail:
            if diff_detail[n2] != {}:
                pure_diff_detail[n2] = diff_detail[n2]
    else:
        pure_diff_detail = diff_detail
    return pure_diff_detail


# 检查响应结果的message
def check_response_message(response_data):
    result = True
    try:
        if not isinstance(response_data, dict):
            response_data = json.loads(response_data)

        # TODO: 业务码存在 Message->MessageCode, MessageText
        if 'message' in response_data:
            message = response_data['message']
            # code 不为0，返回失败
            if 'code' in message and message['code'] != 0:
                result = False

        # 没有message，返回成功
        else:
            result = True
    except:
        logger.warn('检查业务状态码出错! 错误信息:\n%s' % traceback.format_exc())
    return result


# 运行测试用例
def run_testcase(execution_id, user_name, func_type=None, req_data=None, req=None):
    try:
        server_list = []
        result = ''
        execution = ApiExecution.objects.get(id=execution_id)
        code = 0
        if execution:
            testplan_id = execution.testplan_id
            testplan = ApiTestplan.objects.get(id=testplan_id)
            if testplan and len(server_list) == 0:
                testcase_id = execution.testcase_id
                testcase_info = testcase_service.get_testcase_info(testcase_id)

                system_alias = testcase_info['system_alias']
                server_url_list = get_project_domain(system_alias, testplan.run_env)
                # server_list = get_server_list(system_alias, testplan.run_env)

            execution.updater = user_name
            if func_type is None:
                result = run_execution(execution, server_url_list)
                msg = "测试用例执行结果: %s" % result
                logger.info(msg)
            else:
                result = run_execution(execution, server_url_list, func_type=func_type, req_data=req_data, req=req)
                msg = "测试用例执行结果: %s" % result['code']
                logger.info(msg)
        else:
            code = 1
            msg = '测试用例不存在! execution_id: %s' % execution_id
            result = 'fail'
            logger.error(msg)
    except:
        code = 1
        msg = '执行测试用例失败! %s' % traceback.format_exc()
        logger.error(msg)

    if func_type is None:
        return {"code": code, "message": msg}
    else:
        return result


# 多线程并行执行测试计划
def parallel_run_testplan(testplan_id, server_list, username, func_type=None):
    if func_type is not None:
        request_data = []
        result = {}
        testplan = ApiTestplan.objects.get(id=testplan_id)
        if testplan:
            if testplan.actual_start_time is None:
                testplan.actual_start_time = datetime.datetime.now()
            testplan.status = 1
            testplan.save()

            req = requests.session()  # 为持久化cookies，创建req对象

            executions = ApiExecution.objects.filter(testplan_id=testplan_id).order_by('id')
            if len(server_list) == 0 and len(executions) > 0:
                for execution in executions:
                    testcase_id = execution.testcase_id
                    testcase_info = testcase_service.get_testcase_info(testcase_id)
                    api_name = testcase_info['api_name']
                    result[str(api_name)] = run_testcase(execution_id=execution.id, user_name=username,
                                                         func_type=func_type, req_data=result, req=req)
                    request_data.append({str(api_name): result[(api_name)]})
            # 更新执行人
            executions.update(updater=username)
        # 修改测试计划状态、完成时间
        notrun_count = ApiExecution.objects.filter(testplan_id=testplan_id, status__in=[0, 1]).count()
        if notrun_count == 0:
            testplan.status = 2
            # 更新计划实际结束时间
            if testplan.actual_end_time is None:
                testplan.actual_end_time = datetime.datetime.now()

            testplan.save()
            script = DataScript.objects.get(testplan_id=testplan_id)
            if len(request_data) > 0:
                for index in request_data:
                    for value in index.keys():
                        if index[value]['code'] == 'success':
                            status = 0
                        else:
                            status = 1
                            break
                record = DataScriptRecord(script_id=script.script_id, run_status=status,
                                          create_time=datetime.datetime.now(),
                                          run_data=json.dumps(index[value]['result'], encoding='UTF-8',
                                                              ensure_ascii=False),
                                          testplan_id=testplan_id)
                record.save()
            else:
                logger.error(u'测试用例执行错误%s' % testplan_id)

            logger.info(u'测试计划已完成. ID: %s' % testplan_id)

        else:
            msg = u'测试计划未执行完成，请检查执行状态。testplanId: %s' % testplan_id
            logger.warn(msg)
    else:
        testplan = ApiTestplan.objects.get(id=testplan_id)
        if testplan:
            if testplan.actual_start_time is None:
                testplan.actual_start_time = datetime.datetime.now()
            testplan.status = 1
            testplan.save()

            run_env = testplan.run_env

            executions = ApiExecution.objects.filter(testplan_id=testplan_id)
            if len(executions) > 0:
                testcase_id = executions[0].testcase_id
                testcase_info = testcase_service.get_testcase_info(testcase_id)
                system_alias = testcase_info['system_alias']

                # 获取服务器列表
                if len(server_list) == 0:
                    server_list = get_project_domain(system_alias, run_env)

                # 更新执行人
                executions.update(updater=username)

                # 备份数据库
                result = db_service.backup_database(testplan_id, system_alias, run_env)
                if result['code'] == 0:
                    # 采用线程池执行用例
                    testcase_pool = threadpool.ThreadPool(parallel_testcase_count)
                    data = [((execution, server_list), None) for execution in executions]
                    reqs = threadpool.makeRequests(run_execution, data)
                    [testcase_pool.putRequest(req) for req in reqs]
                    testcase_pool.wait()

                    # 恢复数据库
                    result = db_service.restore_database(testplan_id, system_alias, run_env)
                    if result['code'] != 0:
                        logger.error(result['message'])
                        logger.error('还原数据库失败. 请手动检查数据库还原情况. 测试计划ID:%s' % testplan_id)
                else:
                    logger.error(result['message'])
                    logger.error('备份数据库失败，测试计划执行中止！测试计划ID:%s' % testplan_id)

            # 修改测试计划状态、完成时间
            notrun_count = ApiExecution.objects.filter(testplan_id=testplan_id, status__in=[0, 1]).count()
            if notrun_count == 0:
                testplan.status = 2
                # 更新计划实际结束时间
                if testplan.actual_end_time is None:
                    testplan.actual_end_time = datetime.datetime.now()
                testplan.save()
                logger.info(u'测试计划已完成. ID: %s' % testplan_id)
            else:
                msg = u'测试计划未执行完成，请检查执行状态。testplanId: %s' % testplan_id
                logger.warn(msg)


def parallel_creat_datascript(script_id, username):
    script = DataScript.objects.get(script_id=script_id)
    system_alias = ''
    testcase_list = []
    if script:

        # 脚本未关联测试计划，走新建的路线
        script.last_runtime = datetime.datetime.now()
        script.save()
        run_env = 2
        # 拼装接口列表-
        if script.api_list:
            for index in eval(str(script.api_list)):
                Testcase = ApiTestcases.objects.get(id=index)
                api_info = ApiList.objects.get(id=Testcase.api_id)
                system_alias = api_info.system_alias
                # 更新执行人-
                Testcase.updater = username
                Testcase.save()
                # 测试用例id组合成一个列表
                testcase_list.append(Testcase.id)
            try:  # 根据应用信息和测试用例信息创建测试计划
                testplan_id = testplan_service.testplan_create(system_alias=system_alias, run_env=run_env,
                                                               user=username, is_auto=0,
                                                               func_type=1, apis=testcase_list)
                # 更新脚本最后执行时间
                script.last_runtime = datetime.datetime.now()
                script.testplan_id = testplan_id
                script.save()
                # 用特别类型执行测试计划
                parallel_run_testplan(testplan_id=testplan_id, server_list='', username=username, func_type=1)
            except:
                msg = '创建或执行脚本计划时异常' + traceback.format_exc()
                logger.error(msg)
        else:
            msg = '测试用例集为空，请检查'
            logger.error(msg)
    else:
        msg = '脚本id %s 不存在' % script_id
        logger.error(msg)


# 自动调度执行测试用例
def auto_run_testcase():
    auto_testplans = ApiTestplan.objects.filter(is_delete=0, is_auto=1, status=0)
    if len(auto_testplans) > 0:
        logger.info("开始调度执行测试计划: %s" % datetime.datetime.now())
        data = [((testplan.id, [], 'System'), None) for testplan in auto_testplans]
        reqs = threadpool.makeRequests(parallel_run_testplan, data)
        [task_pool.putRequest(req) for req in reqs]
        task_pool.wait()

    else:
        logger.info("没有自动调度执行的测试计划。")

    logger.info("本次调度执行完成!")


# 获取测试用例执行详情
def get_execution_info(id):
    execution_info = {}
    execution = ApiExecution.objects.get(id=id)

    if execution:
        testcase_info = testcase_service.get_testcase_info(execution.testcase_id)
        execution_info = {"id": execution.id, "result": execution.result, "diff": execution.diff,
                          "updater": execution.updater, "method": testcase_info['method'],
                          "api_name": testcase_info['api_name'], "system_alias": testcase_info['system_alias'],
                          "server_ip": execution.server_ip, "client_ip": client_ip,
                          "status": status_dict[execution.status],
                          "expect_response_data": testcase_info['expect_response_data'],
                          "status_code": execution.status_code,
                          "request_data": execution.request_data, "response_data": execution.response_data,
                          "create_time": utc2local(execution.create_time).strftime('%Y-%m-%d %H:%M:%S'),
                          "execute_time": utc2local(execution.execute_time).strftime(
                              '%Y-%m-%d %H:%M:%S') if execution.execute_time else '',
                          "message": execution.message, "status_code": execution.status_code}

    return execution_info


# 获取server url
def get_project_domain(system_alias, run_env):
    domain = None
    projects = Projects.objects.filter(name=system_alias, is_delete=0)
    if len(projects) > 0:
        project = projects[0]
        env = project_service.get_project_env(project.id)
        if env:
            domain = env['domain']

    return domain


# json校验方法
def json_validate(response_data, json_path, operate, expect_value):
    result = True
    try:
        # 判断返回值是否json格式
        if not isinstance(response_data, dict):
            response_data = json.loads(response_data)
            value = jsonpath.jsonpath(response_data, json_path)

            # 判断jsonpath解析结果有值或list
            if value and isinstance(value, list) and len(value) > 0:
                actual_value = str(value[0])
                if isinstance(value[0], bool):
                    actual_value = actual_value.lower()
                    expect_value = expect_value.lower()
                expr = "'%s' %s '%s'" % (actual_value, operate, expect_value)
                if eval(expr):
                    logger.warn('json校验成功！expr: %s' % expr)
                else:
                    logger.warn('json校验失败！实际值: %s' % actual_value)
                    result = False
            else:
                logger.warn('json校验失败！返回值: %s' % value)
                result = False
        else:
            logger.warn('返回值不是json格式！ %s' % response_data)
            result = False

    except:
        logger.warn('json校验出错! 错误信息:\n%s' % traceback.format_exc())
        result = False
    return result
