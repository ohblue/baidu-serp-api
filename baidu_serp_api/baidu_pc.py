import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from .util import gen_random_params, clean_html_tags, logger
import re

class BaiduPc:

    def __init__(self):
        self.random_params = gen_random_params()
        self.keyword = None
        self.date_range = None
        self.pn = None
        self.proxies = None
        self.match_count = 0
        self.exclude = []

    def extract_baidupc_data(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        search_results = soup.select('div[tpl="se_com_default"]')
        result_data = []
        self.match_count = 0
        for result in search_results:
            title_element = result.select_one('h3.c-title')

            url = result.get('mu')

            description = ""
            date_time = ""
            source = ""

            ranking = result.get('id', 0)

            summary_element = result.select_one('span[class^="content-right_"]')
            if summary_element:
                description = clean_html_tags(summary_element.get_text().strip())

            date_time_element = result.select_one('span.c-color-gray2')
            if date_time_element:
                date_time = date_time_element.get_text().strip()

            source_element = result.select_one('span.c-color-gray')
            if source_element:
                source = source_element.get_text().strip()

            if title_element and url:
                title_text = clean_html_tags(title_element.get_text().strip())
                if self.keyword in title_text:
                    self.match_count += 1
                result_data.append({"title": title_text, "url": url, "description": description, "date_time": date_time, "source": source, "ranking": ranking})

        return result_data

    def get_recommend(self, html_content):
        # 找出所有 s-data 注释块
        pattern = r"<!--s-data:(.*?)-->"
        matches = re.findall(pattern, html_content, re.DOTALL)

        # 定义一个集合用于存放关键词以实现自动排重
        keyword_set = set()

        # 遍历匹配结果，找到特定的两个注释块
        for comment in matches:
            if '"title":"其他人还在搜"' in comment:
                json_data = json.loads(comment)
                for item in json_data['list']:
                    keyword_set.add(item['text'])
            elif '"newList"' in comment:
                json_data = json.loads(comment)
                for sublist in json_data['newList']:
                    for item in sublist:
                        keyword_set.add(item['word'])

        recomment_list = list(keyword_set)
        return recomment_list

    def get_baidupc_serp(self, keyword):
        url = 'http://www.baidu.com/s'

        params = {
            'wd': keyword,
            'ie':'utf-8',
            'f':'8',
            'rsv_bp':'1',
            'rsv_idx':'1',
            'tn':'baidu',
            'fenlei':'256',
            'rqlang':'cn',
            'rsv_enter':'1',
            'rsv_dl':'tb',
            'rsv_btype':'i',
            'inputT':'2751',
            'mod': '1',
            'isbd': '1',
            'isid': self.random_params['isid'],
            'rsv_pq': self.random_params['rsv_pq'],
            'rsv_t': self.random_params['rsv_t'],
            'tfflag': '1',
            'bs': keyword,
            'rsv_sid': self.random_params['rsv_sid'],
            '_ss': '1',
            'clist': self.random_params['clist'],
            'hsug': '',
            'f4s': '1',
            'csor': '20',
            '_cr1': self.random_params['_cr1'],
        }

        # 搜索词为site:xxx时, 增加si和ct参数
        if 'site:' in keyword:
            site = keyword.split('site:')[1].strip()
            params['si'] = site
            params['ct'] = '2097152'

        # 搜索指定日期范围
        if self.date_range:
            start_date, end_date = self.date_range.split(',')
            start_timestamp = int(datetime.strptime(start_date, '%Y%m%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y%m%d').timestamp())
            params['gpc'] = f'stf={start_timestamp},{end_timestamp}|stftype=2'

        # 搜索指定页码
        if self.pn:
            params['pn'] = str((int(self.pn) - 1) * 10)

        # logger.debug(params)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.baidu.com',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Referer': 'http://www.baidu.com/',
            'cookie': f'BAIDUID={self.random_params["baiduid"]}:FG=1; BAIDUID_BFESS={self.random_params["baiduid"]}:FG=1; '\
                    f'BDUSS={self.random_params["bduss"]}; H_PS_645EC={self.random_params["rsv_t"]}; H_PS_PSSID={self.random_params["rsv_sid"]}',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, params=params, proxies=self.proxies, timeout=10, allow_redirects=False)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            return {'code': 500, 'msg': '网络请求失败'}

    def handle_response(self, response):
        if isinstance(response, str):
            if '百度安全验证' in response or response.strip() == '':
                return {'code': 501, 'msg': '百度安全验证'}
            if '未找到相关结果' in response:
                return {'code': 404, 'msg': '未找到相关结果'}
            if '相关搜索' not in response and 'site:' not in self.keyword:
                return {'code': 403, 'msg': '疑似违禁词'}
            data = {
                'results': self.extract_baidupc_data(response),
                'recommend': self.get_recommend(response),
                'last_page': '下一页' not in response,
                'match_count': self.match_count
            }
            keys_to_delete = [key for key in self.exclude]
            for key in keys_to_delete:
                del data[key]
            return {'code': 200, 'msg': 'ok', 'data': data}
        else:
            return response

    def search(self, keyword, date_range=None, pn=None, proxies=None, exclude=[]):
        self.keyword = keyword
        self.date_range = date_range
        self.pn = pn
        self.proxies = proxies
        self.exclude = exclude
        html_content = self.get_baidupc_serp(keyword)
        return self.handle_response(html_content)
