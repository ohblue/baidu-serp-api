import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from .util import gen_random_params, clean_html_tags, logger

class BaiduMobile:
    
    def __init__(self):
        self.random_params = gen_random_params()
        self.keyword = None
        self.recomment_list = []
        self.date_range = None
        self.pn = None
        self.proxies = None
        self.match_count = 0

    def extract_baidum_data(self, html_content):
        search_data = []
        self.match_count = 0
        soup = BeautifulSoup(html_content, 'html.parser')
        search_results = soup.select('div[tpl="www_index"], div[tpl="www_struct"]')
        
        for result in search_results:
            title_element = result.find('p', class_='cu-title')

            url = result.get('data-log')
            if url:
                url = json.loads(url)['mu']

            description = ""
            date_time = ""
            source = ""

            order = int(result.get('order', 0))
            pn = self.pn if self.pn is not None else 1
            ranking = order + (pn - 1) * 10

            summary_element = result.select_one('div[class*=summary-]')
            if summary_element:
                description = clean_html_tags(summary_element.get_text().strip())

                date_time_element = summary_element.find('span', class_='c-gap-right-small c-color-gray')
                if date_time_element:
                    description = description.replace(date_time_element.get_text().strip(), '')
                    date_time = date_time_element.get_text().strip()

            source_element = result.select_one('div[class*=_text_]')
            if source_element:
                source = source_element.get_text().strip()

            if title_element and url:
                title_text = clean_html_tags(title_element.get_text().strip())
                if self.keyword in title_text:
                    self.match_count += 1
                search_data.append({'title': title_text, 'url': url, 'description': description, 'date_time': date_time, "source": source, "ranking": ranking})

        return search_data

    def get_recommend(self, keyword, qid):
        url = 'https://m.baidu.com/rec'
        params = {
            'word': keyword,
            'platform': 'wise',
            'ms': '1',
            'lsAble': '1',
            'rset': 'rcmd',
            'qid': qid,
            'rq': 'python',
            'from': '0',
            'baiduid': f'BAIDUID={self.random_params["baiduid"]}:FG=1',
            'tn': '',
            'clientWidth': '412',
            't': self.random_params['timestamp'],
            'r': self.random_params['r'],
        }
        headers = {
            'Cookie': f'BAIDUID={self.random_params["baiduid"]}:FG=1; BAIDUID_BFESS={self.random_params["baiduid"]}:FG=1;BDUSS={self.random_params["bduss"]};',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 baiduboxapp/13.10.0.10',
        }
        try:
            response = requests.get(url, headers=headers, params=params, proxies=self.proxies, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            json_data = response.json()
            # 获取所有键名为'up'和'down'的值
            up_values = []
            down_values = []
            if json_data['errcode'] != 0:
                return []
            else: 
                for item in json_data['rs']['rcmd']['list']:
                    up_values.extend(item['up'])
                    down_values.extend(item['down'])

                # 排重并合并为新的列表
                recomment_list = list(set(up_values + down_values))
                return recomment_list
        except requests.exceptions.RequestException as e:
            return []

    def get_baidum_serp(self, keyword):
        url = 'https://m.baidu.com/s'
        params = {
            'word': keyword
        }
        if self.date_range:
            start_date, end_date = self.date_range.split(',')
            start_timestamp = int(datetime.strptime(start_date, '%Y%m%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y%m%d').timestamp())
            params['gpc'] = f'stf={start_timestamp},{end_timestamp}|stftype=2'
        if self.pn:
            params['pn'] = str((int(self.pn) - 1) * 10)
        headers = {
            'Cookie': f'BAIDUID={self.random_params["baiduid"]}:FG=1; BAIDUID_BFESS={self.random_params["baiduid"]}:FG=1;BDUSS={self.random_params["bduss"]};',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 baiduboxapp/13.10.0.10'
        }
        try:
            response = requests.get(url, headers=headers, params=params, proxies=self.proxies, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'

            # 如果没有传页码或者是第1页则获取相关搜索词
            if self.pn is None or self.pn==1:
                res_headers = response.headers
                qid = res_headers.get('qid', None)
                if qid:
                    self.recomment_list = self.get_recommend(keyword, qid=qid)

                soup = BeautifulSoup(response.text, 'html.parser')
                page_rcmd = [elem.get_text() for elem in soup.select('a.c-fwb, span.c-fwb')]
                
                # 合并并排重
                self.recomment_list = list(set(self.recomment_list + page_rcmd))

            return response.text
        except requests.exceptions.RequestException as e:
            return {'code': 500, 'msg': '网络请求失败'}

    def handle_response(self, response):
        if isinstance(response, str):
            if '百度安全验证' in response:
                return {'code': 501, 'msg': '百度安全验证'}
            if '未找到相关结果' in response:
                return {'code': 404, 'msg': '未找到相关结果'}
            soup = BeautifulSoup(response, 'html.parser')
            if not soup.find('p', class_='cu-title'):
                return {'code': 403, 'msg': '疑似违禁词'}
            data = {
                'results': self.extract_baidum_data(response),
                'recommend': self.recomment_list,
                'last_page': 'new-nextpage' not in response,
                'match_count': self.match_count
            }
            return {'code': 200, 'msg': 'ok', 'data': data}
        else:
            return response

    def search(self, keyword, date_range=None, pn=None, proxies=None):
        self.keyword = keyword
        self.date_range = date_range
        self.pn = pn
        self.proxies = proxies
        html_content = self.get_baidum_serp(keyword)
        return self.handle_response(html_content)
