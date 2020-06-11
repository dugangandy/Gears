# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Projects(models.Model):
    name = models.CharField(verbose_name='应用名', max_length=128)
    type = models.CharField(verbose_name='应用类型', max_length=32)
    api_count = models.IntegerField(verbose_name='接口数', default=0)
    access_type = models.IntegerField(verbose_name='服务器访问方式（0:域名，1:IP）', default=1)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'projects'
        verbose_name = '应用列表'

    def __unicode__(self):
        return self.name


class ProjectEnv(models.Model):
    name = models.CharField(verbose_name='环境名', max_length=128)
    domain = models.CharField(verbose_name='访问域名', max_length=32)
    project_id = models.IntegerField(verbose_name='项目id', blank=False)
    is_default = models.IntegerField(verbose_name='默认值', default=0)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        db_table = 'project_env'
        verbose_name = '项目环境'

    def __unicode__(self):
        return self.name


class ApiList(models.Model):
    api_name = models.CharField(verbose_name='接口名', max_length=256)
    system_alias = models.CharField(verbose_name='系统别名', max_length=64)
    protocol_type = models.CharField(verbose_name='协议', max_length=32, default="http")
    method = models.CharField(verbose_name='方法', max_length=16, default="post")
    api_desc = models.CharField(verbose_name='接口说明', max_length=1024, blank=True)
    api_level = models.CharField(verbose_name='优先级', max_length=2, default='P1')
    request_header = models.TextField(verbose_name='请求头', default='')
    response_header = models.TextField(verbose_name='响应头', default='')
    tag = models.CharField(verbose_name='标签', max_length=64, default='')
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'api_info'
        verbose_name = '接口列表'

    def __unicode__(self):
        return self.api_name


class ApiParams(models.Model):
    api_id = models.IntegerField(verbose_name='接口名', blank=False)
    request_data = models.TextField(verbose_name='请求数据', blank=False)
    response_data = models.TextField(verbose_name='预期响应结果', blank=True)
    status_code = models.IntegerField(verbose_name='预期状态码', default=200)
    source = models.CharField(verbose_name='数据来源', max_length=32, blank=True)
    run_env = models.IntegerField(verbose_name='运行环境', blank=False, default=2)
    link_script = models.CharField(verbose_name='关联脚本ID', max_length=100, default='')
    params_desc = models.CharField(verbose_name='参数说明', max_length=1024, blank=True)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'api_params'
        verbose_name = '接口参数历史'

    def __unicode__(self):
        return self.api_id


class ApiTestcases(models.Model):
    summary = models.CharField(verbose_name='用例摘要', max_length=256, blank=False)
    api_id = models.IntegerField(verbose_name='接口ID', blank=False)
    params_id = models.IntegerField(verbose_name='参数ID', blank=False)
    desc = models.CharField(verbose_name='用例说明', max_length=1024, blank=True)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)
    status = models.IntegerField(verbose_name='用例状态（0：禁用, 1:启用）', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'api_testcase'
        verbose_name = '接口测试用例'

    def __unicode__(self):
        return "api_id: %s | params_id: %s" % (self.api_id, self.params_id)


class ApiTestplan(models.Model):
    name = models.CharField(verbose_name='测试计划名称', max_length=64, blank=False)
    desc = models.CharField(verbose_name='测试计划说明', max_length=1024, blank=True)
    status = models.IntegerField(verbose_name='测试计划状态', blank=False, default=0)
    run_env = models.IntegerField(verbose_name='运行环境', blank=False, default=2)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)
    is_auto = models.IntegerField(verbose_name='是否自动调度', default=0)
    start_time = models.DateTimeField(verbose_name='计划开始时间')
    actual_start_time = models.DateTimeField(verbose_name='实际开始时间', blank=True)
    actual_end_time = models.DateTimeField(verbose_name='实际结束时间', blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'api_testplan'
        verbose_name = '接口测试计划'

    def __unicode__(self):
        return self.name


class ApiExecution(models.Model):
    testcase_id = models.IntegerField(verbose_name='测试用例ID', blank=False, default=None)
    request_data = models.TextField(verbose_name='请求数据', blank=True)
    response_data = models.TextField(verbose_name='实际响应结果', blank=True)
    status_code = models.IntegerField(verbose_name='实际状态码', blank=True)
    testplan_id = models.IntegerField(verbose_name='测试计划ID', blank=False)
    status = models.IntegerField(verbose_name='执行状态', blank=False, default=0)
    result = models.CharField(verbose_name='执行结果', max_length=16, blank=True)
    diff = models.TextField(verbose_name='差异结果', blank=True)
    message = models.CharField(verbose_name='报错信息', max_length=8192, blank=True)
    client_ip = models.CharField(verbose_name='客户端IP', max_length=256, blank=True)
    server_ip = models.CharField(verbose_name='服务器IP', max_length=256, blank=True)
    execute_time = models.DateTimeField(verbose_name='执行时间', blank=True)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'api_execution'
        verbose_name = '接口执行结果'

    def __unicode__(self):
        return "testplan_id: %s | testcase_id: %s" % (self.testplan_id, self.testcase_id)


class TestcaseCheckpoint(models.Model):
    testcase_id = models.IntegerField(verbose_name='测试用例ID', blank=False)
    check_type = models.CharField(verbose_name='匹配规则类型', max_length=16, blank=False)
    check_param = models.CharField(verbose_name='检查点参数', max_length=256, blank=False)
    operate = models.CharField(verbose_name='操作', max_length=16, blank=False)
    expect_value = models.CharField(verbose_name='预期值', max_length=256, blank=False)
    weight = models.IntegerField(verbose_name='权重', blank=False, default=100)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'testcase_checkpoint'
        verbose_name = '测试用例检查点'

    def __unicode__(self):
        return "testcase_id: %s | checkpoint: %s %s %s" % (
            self.testcase_id, self.check_params, self.operate, self.expect_value)


class UserLog(models.Model):
    user_name = models.CharField(verbose_name='用户名', max_length=64)
    login_name = models.CharField(verbose_name='登录名', max_length=32)
    user_token = models.CharField(verbose_name='用户Token', max_length=256, blank=True)
    client_ip = models.CharField(verbose_name='客户端IP', max_length=16, blank=True)
    server_ip = models.CharField(verbose_name='服务器IP', max_length=16, blank=True)
    access_url = models.CharField(verbose_name='访问地址', max_length=1024)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'user_log'
        verbose_name = '操作日志'

    def __unicode__(self):
        return self.login_name


class SysConfig(models.Model):
    group = models.CharField(verbose_name='配置组', max_length=64)
    key = models.CharField(verbose_name='配置项', max_length=32)
    value = models.CharField(verbose_name='值', max_length=256, blank=True)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'sys_config'
        verbose_name = '系统配置'

    def __unicode__(self):
        return "%s: %s" % (self.group, self.key)


# 配置信息
class CmdbInfo(models.Model):
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=64, null=True)
    product_team = models.CharField(max_length=64, null=True)
    product_line = models.CharField(max_length=64, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    owner = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=1024, null=True)
    project_id = models.IntegerField(null=True)
    product_team_id = models.IntegerField(null=True)
    product_line_id = models.IntegerField(null=True)
    arch_type = models.CharField(max_length=32, null=True)
    domain_name = models.CharField(max_length=512, null=True)
    language = models.CharField(max_length=64, null=True)

    class Meta:
        db_table = 'cmdb_info'


# 数据库配置
class DbConfig(models.Model):
    id = models.AutoField(primary_key=True)
    system_alias = models.CharField(max_length=64, null=False)
    run_env = models.IntegerField(verbose_name='运行环境', blank=False, default=2)
    db_host = models.CharField(verbose_name='数据库IP', max_length=32, blank=True)
    db_port = models.CharField(verbose_name='数据库端口', max_length=16, blank=True)
    db_user = models.CharField(verbose_name='数据库用户名', max_length=32, blank=True)
    db_pwd = models.CharField(verbose_name='数据库密码', max_length=256, blank=True)
    db_name = models.CharField(verbose_name='数据库名', max_length=32, blank=True)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'db_config'


# 数据库还原历史
class DbRestoreHis(models.Model):
    id = models.AutoField(primary_key=True)
    system_alias = models.CharField(max_length=64, null=False)
    testplan_id = models.IntegerField(verbose_name='测试计划ID', blank=False)
    db_conf_id = models.IntegerField(verbose_name='数据库配置ID', blank=False, default=2)
    backup_table_name = models.CharField(verbose_name='备份表名', max_length=64, blank=True)
    origin_table_name = models.CharField(verbose_name='原始表名', max_length=64, blank=True)
    old_count = models.IntegerField(verbose_name='测试前记录条数', default=0)
    new_count = models.IntegerField(verbose_name='测试后记录条数', default=0)
    status = models.IntegerField(verbose_name='表还原状态', blank=False, default=0)
    message = models.CharField(verbose_name='报错信息', max_length=1024, blank=True)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'db_restore_his'


# 2019-2-13新增，数据银行相关表
class DataScript(models.Model):
    script_id = models.CharField(verbose_name='脚本ID', max_length=128)
    dept_name = models.CharField(verbose_name='业务线', max_length=1000)
    script_bu = models.CharField(verbose_name='业务场景', max_length=1000)
    last_runtime = models.DateTimeField(verbose_name='最后执行时间', auto_now_add=True, max_length=0)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, max_length=0)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True, max_length=0)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    auto_run = models.IntegerField(verbose_name='自动执行', default=1)
    run_times = models.IntegerField(verbose_name='执行次数', default=1)
    run_cron = models.CharField(verbose_name='cron表达式', max_length=100)
    api_list = models.CharField(verbose_name='接口列表', max_length=1000)
    testplan_id = models.CharField(verbose_name='关联测试计划ID', max_length=300, default='')

    class Meta:
        db_table = 'datascript'
        verbose_name = '数据银行'

    def __unicode__(self):
        return self.script_id


class script_ApiParams(models.Model):
    api_id = models.IntegerField(verbose_name='接口名', blank=False)
    request_data = models.TextField(verbose_name='请求数据', blank=False)
    response_data = models.TextField(verbose_name='预期响应结果', blank=True)
    status_code = models.IntegerField(verbose_name='预期状态码', default=200)
    source = models.CharField(verbose_name='数据来源', max_length=32, blank=True)
    run_env = models.IntegerField(verbose_name='运行环境', blank=False, default=2)
    params_desc = models.CharField(verbose_name='参数说明', max_length=1024, blank=True)
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'script_api_params'
        verbose_name = '接口参数-脚本'

    def __unicode__(self):
        return self.api_id


class DataScriptRecord(models.Model):
    id = models.AutoField(primary_key=True)
    script_id = models.CharField(verbose_name='脚本ID', max_length=128)
    run_status = models.IntegerField(verbose_name='执行结果', default=0)
    create_time = models.DateTimeField(verbose_name='执行时间', auto_now_add=True)
    run_data = models.TextField(verbose_name='结果数据', blank=True)
    testplan_id = models.CharField(verbose_name='关联测试计划ID', max_length=300, default='')

    class Meta:
        db_table = 'datascript_runlist'
        verbose_name = '数据脚本执行记录'

    def __unicode__(self):
        return self.script_id


class script_ApiList(models.Model):
    api_name = models.CharField(verbose_name='接口名', max_length=256)
    system_alias = models.CharField(verbose_name='系统别名', max_length=64)
    protocol_type = models.CharField(verbose_name='协议', max_length=32, default="http")
    method = models.CharField(verbose_name='方法', max_length=16, default="post")
    api_desc = models.CharField(verbose_name='接口说明', max_length=1024, blank=True)
    api_level = models.CharField(verbose_name='优先级', max_length=2, default='P1')
    request_header = models.TextField(verbose_name='请求头', default='')
    response_header = models.TextField(verbose_name='响应头', default='')
    tag = models.CharField(verbose_name='标签', max_length=64, default='')
    is_delete = models.IntegerField(verbose_name='是否已删除', default=0)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.CharField(verbose_name='创建人', max_length=32, blank=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    updater = models.CharField(verbose_name='更新人', max_length=32, blank=True)

    class Meta:
        db_table = 'script_api_info'
        verbose_name = '接口列表'

    def __unicode__(self):
        return self.api_name


# 2019-3-4 新增用户登录信息表
class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名', blank=False, max_length=50)
    chName = models.CharField(verbose_name='中文名', blank=False, max_length=50)
    empCode = models.IntegerField(verbose_name='工号', blank=True)
    ssoRedirectUrl = models.CharField(verbose_name='重定向URL', blank=False, max_length=100)
    systemAlias = models.CharField(verbose_name='系统别名', blank=False, max_length=100)
    orgTitlePkid = models.CharField(max_length=50, default=10000)
    loginName = models.CharField(verbose_name='加密后用户名', blank=False, max_length=50)
    pwd = models.CharField(verbose_name='加密后密码', blank=False, max_length=50)
    isProd = models.CharField(verbose_name='是否生产', max_length=50)
    run_env = models.IntegerField(verbose_name='运行环境', blank=False, default=2)
    api_id = models.IntegerField(verbose_name='接口id', blank=False, default=2154)
    is_delete = models.IntegerField(verbose_name='是否删除', blank=False, default=0)

    class Meta:
        db_table = 'user_info'
        verbose_name = '用户登录信息表'

    def __unicode__(self):
        return self.username


class SysToken(models.Model):
    user = models.CharField(verbose_name='用户名', max_length=32)
    pwd = models.CharField(verbose_name='密码', max_length=32)
    token = models.CharField(verbose_name='Token值', max_length=128, blank=True)
    belong_system = models.CharField(verbose_name='所属系统名', max_length=32, blank=False)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_token'
        verbose_name = '系统登录TOKEN'

    def __unicode__(self):
        return "%s: %s" % (self.user, self.token)
