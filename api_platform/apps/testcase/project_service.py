# -*-coding:utf-8 -*-


from api_platform.apps.data_service.models import *
from utils import *


def project_sence(projectName):
    rows = []
    projects = Projects.objects.filter(name=projectName.strip()).order_by('name')
    for prj_info in projects:
        if len(projects) < 1:
            break
        cmdb_projects = cmdb_util.get_all_projects_db()
        domain_name = ''
        if prj_info.name in cmdb_projects:
            domain_name = cmdb_projects[prj_info.name]['domain_name']
        if prj_info:
            row = {"id": prj_info.id, "api_count": prj_info.api_count, "type": prj_info.type,
                   "project_name": prj_info.name, "domain_name": domain_name,
                   "access_type": prj_info.access_type,
                   "update_time": utc2local(prj_info.update_time).strftime('%Y-%m-%d %H:%M:%S')
                   }
            rows.append(row)

    return {"total": len(projects), "rows": rows}


def project_datagrid(bu_name, page_num, page_size, has_api=0):
    start_pos = (page_num - 1) * page_size
    end_pos = start_pos + page_size
    rows = []

    projects = Projects.objects.filter(is_delete=0).order_by('name')
    # 仅显示有接口的应用
    if has_api == 1:
        projects = projects.filter(api_count__gt=0)

    # 按业务线过滤
    project_name_list = []
    cmdb_projects = cmdb_util.get_all_projects_db()
    for name in cmdb_projects:
        if bu_name != '' and cmdb_projects[name]['dept_name'] != bu_name:
            continue
        project_name_list.append(name)

    projects = projects.filter(name__in=project_name_list)

    for index in range(start_pos, end_pos):
        if (index + 1) > len(projects):
            break
        prj_info = projects[index]
        domain_name = ''
        if prj_info.name in cmdb_projects:
            domain_name = cmdb_projects[prj_info.name]['domain_name']

        if prj_info:
            row = {"id": prj_info.id, "api_count": prj_info.api_count, "type": prj_info.type,
                   "project_name": prj_info.name, "domain_name": domain_name,
                   "access_type": prj_info.access_type,
                   "update_time": utc2local(prj_info.update_time).strftime('%Y-%m-%d %H:%M:%S')
                   }
            rows.append(row)

    return {"total": len(projects), "rows": rows}


# 查询本地应用
def get_project(buName):
    rows = []
    projects = CmdbInfo.objects.filter(product_line=buName).order_by('project_name')
    if projects:
        for prj_info in projects:
            row = {"project_name": prj_info.project_name}
            rows.append(row)
    return {"total": len(projects), "rows": rows}


# 删除应用
def remove(id):
    code = 0
    msg = ''
    prj_info = Projects.objects.get(id=id)
    if prj_info:
        prj_info.is_delete = 1
        prj_info.save()
        msg = '删除应用成功'
    else:
        msg = '应用id: %s 不存在!' % id
        code = 1
    return {"code": code, "message": msg}


# 应用设置域名访问
def project_toggle_domain(project_id):
    code = 0
    msg = ''
    prj_info = Projects.objects.get(id=project_id)
    if prj_info:
        prj_info.access_type = 0 if prj_info.access_type == 1 else 1
        prj_info.save()
        msg = '应用设置域名访问成功'
    else:
        msg = '应用:%s 不存在!' % project_id
        code = 1
    return {"code": code, "message": msg}


# 同步应用数据
def project_sync(name):
    code = 0
    msg = ''
    projects = Projects.objects.filter(name=name, is_delete=0)
    api_count = ApiList.objects.filter(system_alias=name, is_delete=0).count()
    if len(projects) > 0:
        prj_info = projects[0]
        prj_info.update_time = datetime.datetime.now()
        prj_info.api_count = api_count
    else:
        prj_info = Projects(name=name, is_delete=0, api_count=api_count, access_type=1)

    prj_info.save()
    msg = '同步应用数据成功. %s' % name
    logger.info(msg)

    return {"code": code, "message": msg}


# 同步所有应用数据
def project_sync_all():
    code = 0
    msg = ''
    sucess_count = 0
    failed_count = 0
    all_projects = cmdb_util.get_all_projects_db()
    for name in all_projects:
        result = project_sync(name)
        if result['code'] == 0:
            sucess_count += 1
        else:
            failed_count += 1

    return {"code": 0, "message": "同步成功数: %s, 失败数: %s" % (sucess_count, failed_count)}


def get_project_info(system_alias):
    prj_info = {}
    cmdb_projects = cmdb_util.get_all_projects_db()
    if system_alias != '' and system_alias in cmdb_projects:
        prj_info = cmdb_projects[system_alias]
    return prj_info


def get_project_env(project_id, env_id=None):
    project_env = {}
    if env_id:
        envs = ProjectEnv.objects.all().filter(project_id=project_id, id=env_id)
    else:
        envs = ProjectEnv.objects.all().filter(project_id=project_id, is_default=1).order_by('id')
    if len(envs) > 0:
        env = envs[0]
        project_env = {"name": env.name, "domain": env.domain}
    return project_env
