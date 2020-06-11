# -*-coding:utf-8 -*-

import datetime
import logging
import time
import traceback

logger = logging.getLogger('gears.app')


def utc2local(utc_st):
    """"UTC时间转本地时间（+8:00）"""""
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    if utc_st:
        local_st = utc_st + offset
    else:
        local_st = None
    return local_st


def local2utc(local_st):
    """本地时间转UTC时间（-8:00）"""
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st


def is_valid_format(date_str, formatter='%Y-%m-%d %H:%M:%S'):
    try:
        time.strptime(date_str.strip(), formatter)
        return True
    except Exception, e:
        # logger.warn(traceback.format_exc())
        return False
