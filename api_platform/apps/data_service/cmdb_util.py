# -*-coding:utf-8 -*-
import json
import logging
import traceback

import mysql_util
import redis_util
from api_platform.libs import config

CMDB_API = config.get('others', 'cmdb_api')

logger = logging.getLogger("gears.app")

cache_enable = int(config.get('cache', 'enable'))
if cache_enable == 1:
    redis = redis_util.get_conn()


# 从数据库获取所有应用
def get_all_projects_db():
    if cache_enable == 1:
        try:
            cmdb_projects = redis.get('cmdb_projects')
            if cmdb_projects is not None and len(cmdb_projects) > 0:
                return json.loads(cmdb_projects)
        except Exception, ex:
            logger.error(u"redis获取应用信息失败! %s" % traceback.format_exc())

    cmdb_projects = {}
    sqlStr = "select project_name, product_team, product_line, description, owner, project_id, arch_type, domain_name from cmdb_info where 1=1 "
    try:
        products = mysql_util.queryFromDB(sqlStr)
        # logger.debug("CMDB中应用数: %d" % len(products))
        for row in products:
            project_name = row[0]
            team_name = row[1]
            dept_name = row[2]
            desc = row[3]
            owner = row[4]
            project_id = row[5]
            arch_type = row[6]
            cmdb_projects[project_name] = {'owner': owner, "team_name": team_name, "dept_name": dept_name, "desc": desc,
                                           "project_id": project_id, "arch_type": arch_type, "domain_name": row[7]}
    except Exception, ex:
        logger.error(u"查询数据库失败! %s" % traceback.format_exc())

    if cache_enable == 1:
        try:
            redis.set('cmdb_projects', json.dumps(cmdb_projects), ex=1800)
        except:
            pass
    return cmdb_projects


# 获取所有研发组
def getAllProducts():
    product_list = []
    # url = CMDB_API + "/products?count=1000"
    # result = requests.get(url)
    # product_list = result.json()['products']
    return product_list


# 获取所有业务线
def getAllProductlines():
    # url = CMDB_API + "/bu"
    # result = requests.get(url)
    products = []
    # for product in result.json()['bu']:
    #     if 'status' in product and product['status'] == u'在线':
    #         products.append(product)

    return products


if __name__ == "__main__":
    print
