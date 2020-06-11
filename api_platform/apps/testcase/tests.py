# -*-coding:utf-8 -*-
import os
import sys

from django.test import TestCase

from testcase_service import *

logger = logging.getLogger('gears.app')

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.utf8'
reload(sys)
sys.setdefaultencoding('utf-8')


# Create your tests here.


class TestcaseServiceTestCase(TestCase):
    def setUp(self):
        api_info = ApiList.objects.create(api_name='/basicplatform.scm.baseinfo.api/warehouse/findbycondition',
                                          system_alias='basicplatform.scm.baseinfo.api', protocol_type='http',
                                          method='post',
                                          is_delete=0)
        api_params = ApiParams.objects.create(api_id=1,
                                              request_data='{"page":{"pageTotal":0,"pageSize":10,"sortList":[{"name":"code","type":"asc"}],"currentPage":1,"recordsTotal":0},"status":"E","type":"SRV","locale":"zh"}',
                                              response_data='"total":9,"message":{"code":0，"text":"操作成功"}}',
                                              status_code=200, source='es', is_delete=0, run_env=2)
        ApiTestcases.objects.create(api_id=api_info.id, params_id=api_params.id, is_delete=0)
        logger.info(u'测试数据已准备好!')

    def test_datagrid(self):
        testcase_dto = {'system_alias': 'basicplatform.scm.baseinfo.api', 'api_name': '',
                        'api_level': '', 'page': 1, 'size': 10}
        result = datagrid(testcase_dto)
        logger.info('找到记录数：%s' % result['total'])
        self.assertTrue(result['total'] > 0)

    def test_create(self):
        result = create(1, 2, 'gang.du')
        logger.info(result)
        self.assertTrue(result['code'] == 0)

    def test_get_testcase_info(self):
        result = get_testcase_info(1)
        # logger.info(result)
        self.assertEqual(result['system_alias'], 'basicplatform.scm.baseinfo.api')
        self.assertEqual(result['api_name'], '/basicplatform.scm.baseinfo.api/warehouse/findbycondition')
        self.assertEqual(result['method'], 'post')
        self.assertEqual(result['protocol_type'], 'http')

    def test_remove(self):
        result = remove(1)
        logger.info(result)
        self.assertTrue(result['code'] == 0)

    def tearDown(self):
        pass
