# -*- coding:utf-8 -*-

import MySQLdb

from date_util import *
from models import DbConfig, DbRestoreHis

logger = logging.getLogger('gears.app')
env_dict = {1: '生产', 2: '测试', 3: 'MIT', 4: 'UAT'}


# 获取应用的数据库配置
def get_db_conf(system_alias, run_env=2):
    db_conf = None
    db_confs = DbConfig.objects.filter(system_alias=system_alias, is_delete=0, run_env=run_env)
    if len(db_confs) > 0:
        db_conf = db_confs[0]
    return db_conf


# 根据应用获取数据库连接
def get_conn(db_conf):
    db_conn = None
    if db_conf:
        db_conn = MySQLdb.connect(db_conf.db_host, db_conf.db_user, db_conf.db_pwd, db_conf.db_name)
    else:
        logger.warn('未找到应用【%s】的数据库配置!' % db_conf.system_alias)

    return db_conn


# 查询数据库
def queryFromDB(db_conn, sqlStr):
    result = None
    try:
        db_conn.set_character_set('utf8')
        cursor = db_conn.cursor()
        cursor.execute(sqlStr)
        result = cursor.fetchall()
        cursor.close()
        db_conn.close
    except:
        logger.error('查询数据库出错! %s' % traceback.format_exc())
    return result


# 更新数据库
def updateDB(db_conn, sqlStr):
    ret = 0
    try:
        db_conn.set_character_set('utf8')
        cursor = db_conn.cursor()
        cursor.execute(sqlStr)
        db_conn.commit()
        cursor.close()
        ret = 1
    except:
        logger.error(u"更新数据库时出现异常! %s" % traceback.format_exc())
        db_conn.rollback()
    db_conn.close
    return ret


def backup_database(testplan_id, system_alias, run_env=2):
    # cleanup_database(system_alias, run_env)
    code = 0
    message = ''
    db_conf = get_db_conf(system_alias, run_env)
    if db_conf:
        db_conn = get_conn(db_conf)
        if db_conn:
            sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='%s' AND table_type='base table'" \
                  " AND table_name NOT LIKE 'z_%%'" % db_conf.db_name;
            result = list(queryFromDB(db_conn, sql))
            if len(result) == 0:
                logger.warn('应用[%s]的数据库下没有业务表.' % system_alias)
            else:
                table_postfix = time.strftime('%Y%m%d%H%M%S')
                for row in result:
                    table_name = row[0]
                    backup_table_name = "z_%s_%s" % (table_name, table_postfix)

                    # 创建备份表
                    create_sql = "create table %s like %s" % (backup_table_name, table_name)
                    insert_sql = "insert into %s select * from %s" % (backup_table_name, table_name)
                    if updateDB(db_conn, create_sql) == 1:
                        if updateDB(db_conn, insert_sql) == 1:
                            count_sql = "select count(*) from %s" % table_name
                            count = list(queryFromDB(db_conn, count_sql))
                            DbRestoreHis(system_alias=system_alias, db_conf_id=db_conf.id, testplan_id=testplan_id,
                                         backup_table_name=backup_table_name,
                                         origin_table_name=table_name, old_count=count[0][0], status=0,
                                         message='已备份').save()
                            logger.info('备份表[%s]成功' % backup_table_name)
                        else:
                            err_msg = '备份表[%s]失败! ' % backup_table_name
                            logger.error(err_msg)
                            message += err_msg
                            code = 1
                    else:
                        err_msg = '创建备份表[%s]失败! ' % backup_table_name
                        logger.error(err_msg)
                        message += err_msg
                        code = 1
        else:
            err_msg = '数据库连接失败!'
            logger.error(err_msg)
            message += err_msg
            code = 1

        if code == 0:
            message = '备份应用[%s]数据库成功! ' % system_alias
    else:
        message = '没有找到应用的数据库配置'
        logger.info(message)

    return {"code": code, "message": message}


def restore_database(testplan_id, system_alias, run_env=2):
    code = 0
    message = ''
    db_conf = get_db_conf(system_alias, run_env)
    if db_conf:
        db_conn = get_conn(db_conf)
        if db_conn:
            history = DbRestoreHis.objects.filter(testplan_id=testplan_id, system_alias=system_alias, is_delete=0,
                                                  status=0)
            if len(history) > 0:
                for row in history:
                    err_msg = ''
                    backup_name = row.backup_table_name
                    origin_name = row.origin_table_name
                    row.status = 1  # 进行中

                    # 记录修改后的记录数
                    count_sql = "select count(*) from %s" % origin_name
                    new_count = list(queryFromDB(db_conn, count_sql))[0][0]
                    row.new_count = new_count
                    row.save()

                    # 检测恢复的表数据是否为空
                    if row.old_count == 0:
                        row.status = 2
                        row.message = '数据表为空，无需还原'
                        row.save()
                        continue

                    # 恢复表
                    trunc_sql = "truncate table %s" % origin_name
                    insert_sql = "insert into %s select * from %s" % (origin_name, backup_name)
                    if updateDB(db_conn, trunc_sql) == 1:
                        if updateDB(db_conn, insert_sql) == 1:
                            count_sql = "select count(*) from %s" % origin_name
                            restore_count = list(queryFromDB(db_conn, count_sql))[0][0]
                            if restore_count == row.old_count:
                                err_msg = '还原数据表[%s]成功！' % origin_name
                                logger.info(err_msg)
                                row.status = 2
                            else:
                                err_msg = '还原数据表[%s]失败！ 原表记录数： %s, 还原后记录数: %s' % (
                                    origin_name, back_count, restore_count)
                                logger.error(err_msg)
                                row.status = 3
                                message += err_msg
                                code = 1
                        else:
                            err_msg = '执行插入表[%s]语句失败!' % origin_name
                            row.status = 3
                            logger.error(err_msg)
                            message += err_msg
                            code = 1
                    else:
                        err_msg = '执行清空表[%s]语句失败!' % origin_name
                        row.status = 3
                        logger.error(err_msg)
                        message += err_msg
                        code = 1

                    # 保存还原状态
                    row.message = err_msg
                    row.save()
            else:
                logger.info('本次测试计划[%s]没有需要还原的表.' % testplan_id)

        else:
            err_msg = '数据库连接失败!'
            logger.error(err_msg)
            message += err_msg
            code = 1

        if code == 0:
            message = '还原应用[%s]数据库成功! ' % system_alias
    else:
        message = '没有找到应用的数据库配置'
        logger.info(message)

    return {"code": code, "message": message}


def cleanup_database(system_alias, run_env=2):
    message = ''
    logger.info('开始清理应用[%s]下的备份表...' % system_alias)
    db_conf = get_db_conf(system_alias, run_env)
    db_conn = get_conn(db_conf)
    if db_conn:
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='%s' AND table_type='base table'" \
              " AND table_name LIKE 'z_%%'" % db_conf.db_name;
        result = list(queryFromDB(db_conn, sql))
        if len(result) == 0:
            logger.warn('应用[%s]的数据库下没有临时表.' % system_alias)
        else:
            for row in result:
                temp_table_name = row[0]
                drop_sql = "drop table %s" % temp_table_name
                if updateDB(db_conn, drop_sql) == 1:
                    logger.info('删除临时表[%s]成功' % temp_table_name)
                else:
                    logger.error('删除临时表[%s]失败' % temp_table_name)

    message += '应用[%s]下的备份表清理完成!' % system_alias
    logger.info(message)
    return {"code": 0, "message": message}


# 数据库配置表格
def config_datagrid(system_alias, page, size):
    start_pos = (page - 1) * size
    end_pos = start_pos + size

    db_configs = DbConfig.objects.filter(is_delete=0, system_alias=system_alias).order_by("-update_time")

    config_list = []
    for index in range(start_pos, end_pos):
        if (index + 1) > len(db_configs):
            break
        db_config = db_configs[index]
        if db_config:
            row = {"id": db_config.id, "system_alias": db_config.system_alias,
                   "run_env_str": env_dict[db_config.run_env], "run_env": db_config.run_env,
                   "db_host": db_config.db_host, "db_port": db_config.db_port, "db_user": db_config.db_user,
                   "db_pwd": db_config.db_pwd, "db_name": db_config.db_name, "updater": db_config.updater,
                   "update_time": utc2local(db_config.update_time).strftime('%Y-%m-%d %H:%M:%S')}
            config_list.append(row)

    result = {"total": len(db_configs), "rows": config_list}
    return result


# 删除数据库配置
def remove(id):
    if id == '':
        result = {'code': 1, 'message': 'id不能为空.'}
    else:
        DbConfig.objects.filter(id=id).update(is_delete=1, update_time=datetime.datetime.now())
        result = {'code': 0, 'message': '删除数据库配置成功'}

    return result


# 新增/修改配置
def edit(params):
    code = 0
    msg = ''
    # id
    id = ''
    if 'id' in params and params['id'] != '':
        id = params['id']

    system_alias = params['system_alias']
    if id == '':
        # 新增
        exist_count = DbConfig.objects.filter(system_alias=system_alias, is_delete=0, run_env=params['run_env'],
                                              db_host=params['db_host'], db_port=params['db_port'], db_user=params['db_user']).count()
        if exist_count == 0:
            db_config = DbConfig(system_alias=system_alias, is_delete=0, db_host=params['db_host'],
                                db_port=params['db_port'], db_user=params['db_user'], db_pwd=params['db_pwd'],
                                db_name=params['db_name'], run_env=params['run_env'], )
            db_config.save()
            logger.info('新增数据库配置成功!')
        else:
            code = 1
            msg = '已存在%s环境的数据库配置，请修改。' % env_dict[int(params['run_env'])]
            logger.warn(msg)
    else:
        # 修改
        db_config = DbConfig.objects.get(id=id)
        if db_config:
            old_env = db_config.run_env
            new_env = int(params['run_env'])
            exist_count = DbConfig.objects.filter(system_alias=system_alias, is_delete=0, run_env=new_env).count()
            # 检查是否存在相同环境的配置
            if old_env != new_env and exist_count > 0:
                code = 1
                msg = '已存在%s环境的数据库配置，请修改。' % env_dict[int(params['run_env'])]
                logger.warn(msg)
            else:
                db_config.run_env = params['run_env']
                db_config.db_host = params['db_host']
                db_config.db_port = params['db_port']
                db_config.db_user = params['db_user']
                db_config.db_pwd = params['db_pwd']
                db_config.db_name = params['db_name']
                db_config.update_time = datetime.datetime.now()
                db_config.updater = params['user'] if 'user' in params else ''
                db_config.save()
                msg = '保存数据库配置成功'
        else:
            msg = 'id: %s 不存在!' % id
            code = 1

    return {"code": code, "message": msg}
