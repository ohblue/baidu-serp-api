import unittest
from baidu_serp_api import BaiduMobile

class TestBaiduSerpApi(unittest.TestCase):
    def test_baidu_mobile(self):
        m_serp = BaiduMobile()
        results = m_serp.search('黑神话悟空抢先版手游下载')
        print(results)
        self.assertTrue('code' in results)
        self.assertTrue('msg' in results)
        self.assertTrue('data' in results)
        self.assertTrue('results' in results['data'])
        self.assertTrue('last_page' in results['data'])

if __name__ == '__main__':
    unittest.main()
