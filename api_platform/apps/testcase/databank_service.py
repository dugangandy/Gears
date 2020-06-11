# -*-coding:utf-8 -*-

from api_platform.apps.data_service.models import *
import testcase_service
from utils import *



def databank_grid(bu_name, page_num, page_size, has_api=0):
    start_pos = (page_num - 1) * page_size
    end_pos = start_pos + page_size
    rows = []
    datascript = DataScript.objects.filter(is_delete=0).order_by('script_id')
    #按业务线过滤
    if bu_name != '':
        datascript = datascript.filter(dept_name=bu_name)

    for index in range(start_pos, end_pos):
        if (index + 1) > len(datascript):
            break
        prj_info = datascript[index]
        if prj_info:
            row = {"script_id": prj_info.script_id,
                   "script_bu": prj_info.script_bu,
                   "dept_name": prj_info.dept_name,
                   "last_runtime": utc2local(prj_info.last_runtime).strftime('%Y-%m-%d %H:%M:%S'),
                   "run_times":prj_info.run_times,
                   "run_cron":prj_info.run_cron
                   }
            rows.append(row)

    return {"total": len(datascript), "rows": rows}
#数据脚本执行记录
def databank_records(Sid,page_num, page_size):
    start_pos = (page_num - 1) * page_size
    end_pos = start_pos + page_size
    rows = []
    print Sid
    datarecords = DataScriptRecord.objects.filter(script_id=Sid).order_by('-create_time')
    for index in range(start_pos, end_pos):
        if (index + 1) > len(datarecords):
            break
        prj_info = datarecords[index]
        if prj_info:
            row = {"script_id": prj_info.script_id,
                   "run_status": '成功' if prj_info.run_status == 0 else '失败',
                   "create_time": utc2local(prj_info.create_time).strftime('%Y-%m-%d %H:%M:%S'),
                   "testplan_id":prj_info.testplan_id
                   }
            rows.append(row)
            print row

    return {"total": len(rows), "rows": rows}
#数据池
def databank_source(Sid,page_num, page_size):
    start_pos = (page_num - 1) * page_size
    end_pos = start_pos + page_size
    rows = []
    # datarecords = DataSource.objects.filter(ScriptId=Sid).order_by('create_time')

    datarecords = DataScriptRecord.objects.filter(script_id=Sid).order_by('-create_time')
    for index in range(start_pos, end_pos):
        if (index + 1) > len(datarecords):
            break
        prj_info = datarecords[index]
        if prj_info:
            row = {"script_id": prj_info.script_id,
                   "run_data": prj_info.run_data,
                   "create_time": utc2local(prj_info.create_time).strftime('%Y-%m-%d %H:%M:%S'),
                   "testplan_id":prj_info.testplan_id
                   }
            rows.append(row)

    return {"total": len(rows), "rows": rows}
#查询数据脚本信息
def get_databank_script(Sid):

    data = DataScript.objects.filter(script_id = Sid).values_list('dept_name','script_bu')
    if data:
        content = {'dept_name':data[0][0],'script_bu':data[0][1]}
    else:
        content = {'dept_name':'','script_bu':''}
    return content
#查询数据脚本关联测试用例
def get_datascript_testcase(Sid):
    rows = []
    data = DataScript.objects.filter(script_id = Sid).values_list('dept_name','api_list')
    if data:
        apilist = eval(data[0][1])
        for index in apilist:
            if index:
                case = testcase_service.get_testcase_info(index)
                row = {'testcase_id':case['case_id'],'alians':case['system_alias'],'api_name':case['api_name'],
                       'summary':case['summary'],'dept_name':data[0][0],'case_response_data':case['expect_response_data'],
                       'case_request_data':case['request_data'],'case_summary':case['summary'],'case_api_name':case['api_name']}
                rows.append(row)

    return {"total": len(rows), "rows": rows}

#数据脚本编辑
def data_script_edit(params):
    code = 0
    msg = ''
    # 测试用例ID
    script_id = ''
    if 'script_id' in params and params['script_id'] != '':
        script_id = params['script_id']

    script = DataScript.objects.filter(script_id=script_id)
    if not script:
        # 新增脚本
        try:
            datascript = DataScript(script_id = params['script_id'],dept_name=params['dept_name'],script_bu=params['script_bu'],
                                    api_list=params['api_list'],creator=params['user'],updater=params['user'])
            datascript.save()
            code = 0
            msg ='新增用例成功!'
            logger.info('msg!')
        except:
            code = 1
            msg = '新增用例失败!'
            logger.error('msg!')

    else:
        script = DataScript.objects.get(script_id=script_id)
        if script:
            try:
                script.dept_name = params['dept_name']
                script.script_bu = params['script_bu']
                script.api_list = params['api_list']
                script.updater = params['user']
                script.save()
                code = 0
                msg = '修改用例成功!'
                logger.info('msg!')
            except:
                code = 1
                msg = '修改用例失败!'
                logger.error('msg!')
        else:
            msg = 'script_id id: %s 不存在!' % script_id
            code = 1

    return {"code": code, "message": msg}
#数据脚本更新
def databank_script_save(Sid,run_times,run_cron,auto_run):
    code = 0
    data_info = DataScript.objects.get(script_id = Sid)
    if data_info:
        data_info.run_times = run_times
        data_info.run_cron = run_cron
        data_info.auto_run = auto_run
        data_info.save()
        msg = '更新成功.'
    else:
        msg = '脚本名称: %s 不存在!' % Sid
        code = 1
    return {"code": code, "message": msg}
#执行脚本
def databank_script_run(Sid):
    code = 0
    msg = '数据脚本已启动，请稍候查看数据池!'

    # script = DataScript.objects.get(script_id = Sid)
    # api_list = script.api_list
    # if api_list:
    #     pass
    # else:
    #     pass
    return {"code": code, "message": msg}
# 删除脚本
def script_remove(id):
    code = 0
    msg = ''
    data_info = DataScript.objects.get(script_id=id)
    if data_info:
        data_info.is_delete = 1
        data_info.save()
        msg = '删除应用成功'
    else:
        msg = '脚本id: %s 不存在!' % id
        code = 1
    return {"code": code, "message": msg}
