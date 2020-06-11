# -*- coding:utf-8 -*-

import logging
import traceback

import MySQLdb
from api_platform.libs import config

from api_platform.apps.data_service.models import *

logger = logging.getLogger('gears.app')

host = config.get("runtime", "db_host").split(':')[0]
userName = config.get("runtime", "db_user")
password = config.get("runtime", "db_pwd")
database = config.get("runtime", "db_name")
timeout = 30


def queryFromDB(sqlStr):
    result = None
    try:
        db = MySQLdb.connect(host, userName, password, database, connect_timeout=timeout)
        db.set_character_set('utf8')
        cursor = db.cursor()
        cursor.execute(sqlStr)
        result = cursor.fetchall()
        cursor.close()
        db.close()
    except:
        logger.error('查询数据库出错! %s' % traceback.format_exc())
    return result


def updateDB(sqlStr):
    db = MySQLdb.connect(host, userName, password, database, connect_timeout=timeout)
    try:
        db.set_character_set('utf8')
        cursor = db.cursor()
        cursor.execute(sqlStr)
        db.commit()
        cursor.close()

    except:
        logger.error(u"更新数据库时出现异常! %s" % traceback.format_exc())
        db.rollback()
    db.close
    return 1


# Specify the encoding to avoid the error: UnicodeDecodeError: ‘ascii’ codec can’t decode byte xxx in position 0: ordinal not in range(128)
def encodeStr(str):
    return unicode(str, 'UTF-8')


# 根据db_key执行sql语句
def query_db(db_key, sql):
    limit = 1000
    result = {'code': 0, 'message': '', 'data': []}
    try:
        db_configs = DbConfig.objects.filter(id=db_key)
        if len(db_configs) != 0:
            db_config = db_configs[0]
            db = MySQLdb.connect(db_config.db_host, db_config.db_user, db_config.db_pwd, db_config.db_name,
                                 connect_timeout=timeout)
            db.set_character_set('utf8')
            cursor = db.cursor()
            cursor.execute(sql)
            field_list = []
            for item in cursor.description:
                field_list.append(item[0])
            i = 0
            for row in cursor.fetchall():
                if i > limit:
                    break
                result['data'].append(dict(map(lambda x, y: [x, y], field_list, list(row))))
                i += 1
            cursor.close()
            db.close
    except Exception, ex:
        message = u'查询数据库[key:%s]出错! %s' % (db_key, str(ex))
        logger.error(message + traceback.format_exc())
        result['code'] = 1
        result['message'] = message
    return result


# 根据db_key执行更新sql
def update_db(db_key, sql):
    result = {'code': 0, 'message': '', 'data': []}
    db_configs = DbConfig.objects.filter(id=db_key)
    if len(db_configs) != 0:
        db_config = db_configs[0]
        db = MySQLdb.connect(db_config.db_host, db_config.db_user, db_config.db_pwd, db_config.db_name)
    try:
        db.set_character_set('utf8')
        cursor = db.cursor()
        cursor.execute(sql)
        result['message'] = u'影响行数: %d' % db.affected_rows()
        logger.info(result['message'])
        db.commit()
        cursor.close()
    except:
        db.rollback()
        message = u'更新数据库[key:%s]出现异常! %s' % (db_key, traceback.format_exc())
        logger.error(message)
        result['code'] = 1
        result['message'] = message
    finally:
        db.close()
    return result


# 连接数据库测试
def conn_db(db_host, db_port, db_user, db_pwd, db_name, test_sql):
    result = {'code': 0, 'message': '', 'data': []}
    try:
        db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pwd, db=db_name, port=int(db_port),
                             connect_timeout=2, charset="utf8")
        db.set_character_set('utf8')
        cursor = db.cursor()
        cursor.execute(test_sql)
        cursor.close()
        db.close
    except Exception, ex:
        message = u'连接数据库出错! %s' % str(ex)
        logger.error(message + traceback.format_exc())
        result['code'] = 1
        result['message'] = message
    return result
