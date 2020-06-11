# -*-coding:utf-8 -*-
import project_service
from utils import *


# 删除测试计划
def remove(testplan_id):
    code = 0
    if testplan_id == '':
        msg = 'testplan id不能为空.'
        code = 1
    else:
        ApiTestplan.objects.filter(id=testplan_id).update(is_delete=1, update_time=datetime.datetime.now())
        msg = '删除测试计划成功'

        # 删除测试计划下的用例
        ApiExecution.objects.filter(testplan_id=testplan_id).delete()
        logger.info("测试计划下的用例已全部删除! testplan id: %s" % testplan_id)

    return {"code": code, "message": msg}


# 获取测试计划
def get_testplan_list(system_alias):
    testplan_list = []
    testplans = ApiTestplan.objects.filter(is_delete=0)
    if system_alias != '':
        testplans = testplans.filter(name__startswith=system_alias)
    testplans = testplans.order_by("-create_time")
    for testplan in testplans:
        testplan_list.append({"id": testplan.id, "name": "[%s]: %s" % (testplan.id, testplan.name)})
    return testplan_list


# 测试计划表格
def testplan_datagrid(system_alias, status, page, size):
    start_pos = (page - 1) * size
    end_pos = start_pos + size

    testplans = ApiTestplan.objects.filter(is_delete=0, name__startswith=system_alias)

    # 根据状态过滤
    if status != '':
        testplans = testplans.filter(status=int(status))

    testplans = testplans.order_by("-create_time")

    testplan_list = []
    for index in range(start_pos, end_pos):
        if (index + 1) > len(testplans):
            break
        testplan = testplans[index]
        if testplan:
            testplan_list.append(get_testplan_info(testplan.id))

    result = {"total": len(testplans), "rows": testplan_list}
    return result


# 创建测试计划
def testplan_create(system_alias, run_env, user, is_auto=0, func_type=None, apis=None):
    if func_type is not None:
        # 创建测试计划
        testplan_name = "%s-%s" % (system_alias, time.strftime("%Y%m%d%H%M%S"))
        testplan = ApiTestplan(name=testplan_name, desc=u'%s 创建的测试计划' % user, status=0, is_auto=is_auto,
                               start_time=datetime.datetime.now(), creator=user)

        testplan.save()
        testplan_id = testplan.id
        add_count = 0
        for case in apis:
            testcase = ApiTestcases.objects.get(id=case)
            params_id = testcase.params_id
            params = ApiParams.objects.get(id=params_id)
            if params and params.run_env == run_env and params.is_delete == 0:
                execution = ApiExecution(testcase_id=testcase.id, testplan_id=testplan_id, status=0,
                                         creator=user)
                execution.save()
                # logger.debug(u'新增执行记录成功! %s' % execution)
                add_count += 1
            else:
                continue
        msg = "创建测试计划（id:%s）成功！ 添加用例数: %s" % (testplan_id, add_count)
        logger.info(msg)
        return testplan_id
    else:
        code = 0
        testplan_id = -1
        add_count = 0
        # 生成用例执行记录
        api_list = ApiList.objects.filter(is_delete=0, system_alias=system_alias)
        # 自动创建测试计划时，根据配置加入对应级别的用例
        if is_auto == 1:
            level = []
            sys_configs = SysConfig.objects.filter(group='autotest_level', key=system_alias, is_delete=0)
            if len(sys_configs) > 0:
                config_value = sys_configs[0].value
                for item in config_value.split(','):
                    level.append(item)
                api_list = api_list.filter(api_level__in=level)

        testcase_list = []
        for api_info in api_list:
            api_id = api_info.id

            # 测试计划中一个接口加入最新的用例
            # testcase_list.extend(ApiTestcases.objects.filter(api_id=api_id, is_delete=0).order_by('-update_time')[0:1])

            # 仅加入已启用用例
            testcase_list.extend(
                ApiTestcases.objects.filter(api_id=api_id, is_delete=0, status=1).order_by('-update_time'))
        # 检查应用是否有测试用例
        if len(testcase_list) > 0:
            # 创建测试计划
            testplan_name = "%s-%s" % (system_alias, time.strftime("%Y%m%d%H%M%S"))
            testplan = ApiTestplan(name=testplan_name, desc=u'%s 创建的测试计划' % user, status=0, is_auto=is_auto,
                                   start_time=datetime.datetime.now(), creator=user)
            testplan.save()
            testplan_id = testplan.id

            for testcase in testcase_list:
                params_id = testcase.params_id
                params = ApiParams.objects.get(id=params_id)
                # TODO： 优化为SQL操作
                if params and params.is_delete == 0:
                    execution = ApiExecution(testcase_id=testcase.id, testplan_id=testplan_id, status=0,
                                             creator=user)
                    execution.save()
                    # logger.debug(u'新增执行记录成功! %s' % execution)
                    add_count += 1
                else:
                    continue
            msg = "创建测试计划（id:%s）成功！ 添加用例数: %s" % (testplan_id, add_count)
            logger.info(msg)
        else:
            msg = '应用: %s 下没有测试用例，无需创建测试计划.' % system_alias
            code = 1

        return {"code": code, "data": testplan_id, "message": msg}


# 自动生成测试计划
def batch_create_testplan(run_env):
    try:
        code = 0
        add_count = 0
        fail_cout = 0
        err_msg = ''
        project_list = []
        api_list = ApiList.objects.filter(is_delete=0).order_by('system_alias').values('system_alias').distinct()
        for api in api_list:
            system_alias = api['system_alias']
            prj_info = project_service.get_project_info(system_alias)
            if len(prj_info) > 0 and prj_info['dept_name'] not in exclude_bu_list:
                project_list.append(system_alias)
        logger.info("自动生成测试计划的应用数: %s" % len(project_list))

        for project in project_list:
            result = testplan_create(project, run_env, 'System', is_auto=1)
            if result['code'] == 0:
                add_count += 1
            else:
                fail_cout += 1
                err_msg += "\n%s" % result['message']
        msg = '本次生成测试计划成功数: %s， 失败数: %s. %s' % (add_count, fail_cout, err_msg)
        logger.info(msg)
    except:
        code = 1
        msg = '生成测试计划失败!%s' % traceback.format_exc()
        logger.error(msg)

    return {"code": code, "message": msg}


# 获取测试计划详细信息
def get_testplan_info(id):
    testplan = ApiTestplan.objects.get(id=id)
    testplan_info = {}

    if testplan:
        # 获取计划中的用例数
        testcase_count = ApiExecution.objects.filter(testplan_id=id).count()

        # 计算通过率
        success_count = ApiExecution.objects.filter(testplan_id=testplan.id, result='success').count()
        failed_count = ApiExecution.objects.filter(testplan_id=testplan.id, result='fail').count()
        success_rate = "%.2f%%" % (success_count * 100.0 / testcase_count) if testcase_count > 0 else 'NA'

        # 业务线
        system_alias = testplan.name.split('-')[0]
        try:
            bu_name = cmdb_util.get_all_projects_db()[system_alias]['dept_name']
        except:
            bu_name = u'部门信息为空'
        testplan_info = {"id": testplan.id, "name": testplan.name, "env": env_dict[testplan.run_env],
                         "count": testcase_count, "desc": testplan.desc, "failed_count": failed_count,
                         "actual_start_time": utc2local(testplan.actual_start_time).strftime(
                             '%Y-%m-%d %H:%M:%S') if testplan.actual_start_time else '',
                         "actual_end_time": utc2local(testplan.actual_end_time).strftime(
                             '%Y-%m-%d %H:%M:%S') if testplan.actual_end_time else '',
                         "start_time": utc2local(testplan.start_time).strftime(
                             '%Y-%m-%d %H:%M:%S') if testplan.start_time else '',
                         "status": testplan.status, "status_text": status_dict[testplan.status],
                         "creator": testplan.creator,
                         "create_time": utc2local(
                             testplan.create_time).strftime('%Y-%m-%d %H:%M:%S'), "success_rate": success_rate,
                         "duration": "%.2f" % (
                                 testplan.actual_end_time - testplan.actual_start_time).total_seconds() if testplan.actual_start_time and testplan.actual_end_time else '-',
                         "bu_name": bu_name,
                         }

    return testplan_info
