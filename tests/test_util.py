# Python
import unittest
from baidu_serp_api.util import convert_date_format
from datetime import datetime, timedelta

class TestConvertDateFormat(unittest.TestCase):
    def test_convert_date_format(self):
        # 测试以下几种情况："5分钟前", "2小时前", "今天", "昨天", "昨天 14:30", "前天", "前天 09:15", "3天前", "4月5日", "2021年12月25日"

        # 测试 "5分钟前"
        self.assertEqual(convert_date_format("5分钟前"), datetime.now().strftime("%Y-%m-%d"))

        # 测试 "2小时前"
        self.assertEqual(convert_date_format("2小时前"), datetime.now().strftime("%Y-%m-%d"))
 
        # 测试 "今天"
        self.assertEqual(convert_date_format("今天"), datetime.now().strftime("%Y-%m-%d"))

        # 测试 "昨天"
        self.assertEqual(convert_date_format("昨天"), (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))

        # 测试 "昨天 14:30"
        self.assertEqual(convert_date_format("昨天 14:30"),  (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))

        # 测试 "前天"
        self.assertEqual(convert_date_format("前天"),  (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"))

        # 测试 "前天 09:15"
        self.assertEqual(convert_date_format("前天 09:15"), (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"))

        # 测试 "3天前"
        self.assertEqual(convert_date_format("3天前"),  (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"))

        # 测试 "4月5日"
        self.assertEqual(convert_date_format("4月5日"), "2024-04-05")

        # 测试 "2021年12月25日"
        self.assertEqual(convert_date_format("2021年8月25日"), "2021-08-25")
        # 测试输入为不正确的格式，期望返回 None
        self.assertIsNone(convert_date_format("20211225"))


if __name__ == '__main__':
    unittest.main()