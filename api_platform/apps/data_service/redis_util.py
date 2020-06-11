# -*- coding:utf-8 -*-
import redis

from api_platform.libs import config

serverIp = config.get("cache", "host")
port = config.get("cache", "port")
r = redis.StrictRedis(host=serverIp, port=port, db=0)


def print_conn_str():
    print ('Redis info:\n\tServer IP: %s \n\tPort: %s' % serverIp, port)


def get_conn():
    return r
