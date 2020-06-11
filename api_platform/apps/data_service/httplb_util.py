# -*- coding:utf-8 -*-

import logging
import random
import traceback

import requests

RETRY_TIMES = 3
logger = logging.getLogger('gears.app')


def ha_request(method, server_list, url, data, request_header={}, func_type=None, req=None):
    # logger.debug(u"开始连接服务器...")
    result = None
    index = random.randint(-1, len(server_list) - 1)
    for i in range(0, RETRY_TIMES + 1):
        if i > 0:
            logger.info(u"开始第%s次重试..." % i)

        try:
            result = request(method, server_list[index], url, data, request_header, func_type=func_type, req=req)

            if result is None or result.status_code != 200:
                index += 1
                index %= len(server_list)
                if result is not None:
                    err_code = result.status_code
                else:
                    err_code = 'None'
                logger.info(u"请求失败! 错误码: %s." % err_code)
            else:
                logger.info('请求成功! URL: %s' % server_list[index])
                try:
                    if result.json()['key']:
                        sso_set_cookies(domains=result.json()['domains'], key=result.json()['key'], req=req)
                except:
                    pass
                break

        except Exception, ex:
            logger.warn(u"请求失败! Url: %s， 错误信息: %s" % (server_list[index] + url, traceback.format_exc()))

    return result


# 发起HTTP请求
def request(method, host, url, data, request_header={}, func_type=None, req=None):
    request_url = host + url
    if method == 'post':
        request_header['Content-type'] = 'application/json'
        request_header['charset'] = 'utf-8'
        # result = requests.post(request_url, data=str(data), headers=request_header, timeout=10)
        if func_type is None:
            result = requests.request("POST", request_url, headers=request_header, data=data, timeout=10)
        else:
            result = req.request("POST", request_url, headers=request_header, data=data, timeout=10, verify=False)
    elif method == 'get' and data:
        result = req.get(request_url + data)
    else:
        if func_type is None:
            result = requests.get(request_url)
        else:
            result = req.get(request_url)

    return result


def sso_set_cookies(domains=[], key='', req=None):
    for url in domains:
        if url != 'sso.pangmaoyuntest.com':
            rs = req.request("GET", url="https://" + str(
                url) + "/cookie/setCookie?jsonpCallBack=jQuery171021077975876533728_1551777508349&"
                       "domain=" + str(url) + "&ticket=" + str(key) + "&_=1551777520661", verify=False)

            logger.info("Set Cookies with %s" % rs.text)


# def get_purcher_oid(html):#暂时废弃，后期加入爬虫库处理html
#     soup = BeautifulSoup(html,'html.parser')
#     first_oid = soup.find(attrs={'class':'one in'})
#     result = {}
#     result['oid']=first_oid.get('data-oid')
#     result['status'] = first_oid.b.get_text()
#     result['type'] = first_oid.find(attrs={'class':'type'}).get_text()
#     result['size'] = first_oid.find(attrs={'class':'span-right'}).get_text()
#     return result
if __name__ == "__main__":
    slist = ['http://10.90.10.45:8090', 'http://10.90.10.101:8090']
    logger.info(ha_request(slist, '/healthCheck', None))
