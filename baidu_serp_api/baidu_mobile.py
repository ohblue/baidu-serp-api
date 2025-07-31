import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from .util import gen_random_params, clean_html_tags, convert_date_format
import certifi

class BaiduMobile:
    
    def __init__(self):
        self.exclude = []

    def extract_baidum_data(self, html_content, keyword, pn):
        match_count = 0
        search_data = []
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
            ranking = order + ((pn or 1) - 1) * 10

            summary_element = result.select_one('div[class*=summary-]')
            if summary_element:
                description = clean_html_tags(summary_element.get_text().strip())

                date_time_element = summary_element.find('span', class_='c-gap-right-small c-color-gray')
                if date_time_element:
                    description = description.replace(date_time_element.get_text().strip(), '')
                    date_time = date_time_element.get_text().strip()
                    date_time = convert_date_format(date_time)

            source_element = result.select_one('div[class*=_text_]')
            if source_element:
                source = source_element.get_text().strip()

            if title_element and url:
                title_text = clean_html_tags(title_element.get_text().strip())
                if keyword in title_text:
                    match_count += 1
                search_data.append({'title': title_text, 'url': url, 'description': description, 'date_time': date_time, "source": source, "ranking": ranking})

        return search_data, match_count

    def get_recommend(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        page_rcmd = [elem.get_text() for elem in soup.select('a.c-fwb, span.c-fwb')]
        # 对page_rcmd进行排重
        recommend = list(set(page_rcmd))
        return recommend

    def get_ext_recommend(self, keyword, qid, random_params, proxies):
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
            'baiduid': f'BAIDUID={random_params["baiduid"]}:FG=1',
            'tn': '',
            'clientWidth': '412',
            't': random_params['timestamp'],
            'r': random_params['r'],
        }
        headers = {
            'Cookie': f'BAIDUID={random_params["baiduid"]}:FG=1; BAIDUID_BFESS={random_params["baiduid"]}:FG=1;BDUSS={random_params["bduss"]};',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 baiduboxapp/13.10.0.10',
            'Connection': 'close'
        }
        try:
            with requests.Session() as session:
                response = session.get(
                    url,
                    headers=headers,
                    params=params,
                    proxies=proxies,
                    timeout=10,
                    verify=certifi.where()
                )
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
                    ext_recommend = list(set(up_values + down_values))
                    return ext_recommend
        except requests.exceptions.RequestException as e:
            return []

    def get_baidum_serp(self, keyword, date_range, pn, proxies, random_params):
        url = 'https://m.baidu.com/s'
        params = {
            'word': keyword
        }
        if date_range:
            start_date, end_date = date_range.split(',')
            start_timestamp = int(datetime.strptime(start_date, '%Y%m%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y%m%d').timestamp())
            params['gpc'] = f'stf={start_timestamp},{end_timestamp}|stftype=2'
        if pn:
            params['pn'] = str((int(pn) - 1) * 10)
        headers = {
            'Cookie': f'BAIDUID={random_params["baiduid"]}:FG=1; BAIDUID_BFESS={random_params["baiduid"]}:FG=1;BDUSS={random_params["bduss"]};',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 baiduboxapp/13.10.0.10',
            'Connection': 'close'
        }
        try:
            with requests.Session() as session:
                response = session.get(url, headers=headers, params=params, proxies=proxies, timeout=10, verify=certifi.where())
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                # # 检查302重定向到验证码页面
                # if response.status_code == 302:
                #     location = response.headers.get('Location', '')
                #     if 'wappass.baidu.com/static/captcha' in location or 'captcha' in response.text:
                #         return {"code": 501, "msg": "百度M安全验证"}
                
                # # 检查响应内容中的验证码链接
                # if 'wappass.baidu.com/static/captcha' in response.text:
                #     return {"code": 501, "msg": "百度M安全验证"}

                recommend = self.get_recommend(response.text)
                ext_recommend = None
                
                if (pn is None or pn == 1) and 'ext_recommend' not in self.exclude:
                    res_headers = response.headers
                    qid = res_headers.get('qid', None)
                    if qid:
                        ext_recommend = self.get_ext_recommend(keyword, qid, random_params, proxies)

                return response.text, recommend, ext_recommend
            
        except requests.exceptions.ChunkedEncodingError:
            return {'code': 502, 'msg': '响应提前结束'}
        except requests.exceptions.ReadTimeout:
            return {'code': 504, 'msg': '读取超时'}
        except requests.exceptions.ProxyError as e:
            if 'Connection reset by peer' in str(e):
                return {'code': 505, 'msg': '代理连接被重置'}
            elif 'Remote end closed connection' in str(e):
                return {'code': 506, 'msg': '代理连接被远程关闭'}
            else:
                return {'code': 507, 'msg': f'代理服务器错误: {str(e)}'}
        except requests.exceptions.SSLError:
            return {'code': 508, 'msg': 'SSL连接错误'}
        except requests.exceptions.ConnectionError as e:
            if 'Connection reset by peer' in str(e):
                return {'code': 509, 'msg': '连接被重置'}
            elif 'Remote end closed connection' in str(e):
                return {'code': 510, 'msg': '远程服务器关闭连接'}
            else:
                return {'code': 511, 'msg': f'连接错误: {str(e)}'}
        except requests.exceptions.RequestException as e:
            return {'code': 500, 'msg': f'请求异常: {str(e)}'}

    def handle_response(self, response, keyword, recommend, ext_recommend, pn):
        if isinstance(response, str):
            # 检查百度安全验证 - 包括原有逻辑和验证码URL检测
            if ('百度安全验证' in response):
                return {'code': 501, 'msg': '百度M安全验证'}
            if '未找到相关结果' in response:
                return {'code': 404, 'msg': '未找到相关结果'}
            
            # 提前执行数据提取以便进行准确判断
            search_results, match_count = self.extract_baidum_data(response, keyword, pn)
            
            # 检查是否有搜索结果（基于实际提取的数据）
            if (
                not search_results
                and 'site:' not in keyword
                and not keyword.startswith(('http://', 'https://', 'www.', 'm.'))
            ):
                return {'code': 405, 'msg': '无搜索结果'}
            
            # 检查是否有推荐词
            if (
                not recommend
                and 'site:' not in keyword
                and not keyword.startswith(('http://', 'https://', 'www.', 'm.'))
            ):
                return {'code': 406, 'msg': '无推荐词'}
            
            data = {
                'results': search_results,
                'recommend': recommend,
                'ext_recommend': ext_recommend,
                'last_page': 'new-nextpage' not in response,
                'match_count': match_count
            }
            keys_to_delete = [key for key in self.exclude]
            for key in keys_to_delete:
                del data[key]
            return {'code': 200, 'msg': 'ok', 'data': data}
        else:
            return response

    def search(self, keyword, date_range=None, pn=None, proxies=None, exclude=['ext_recommend']):
        if exclude is not None:
            self.exclude = exclude

        random_params = gen_random_params()

        if 'recommend' in self.exclude and 'ext_recommend' not in self.exclude:
            self.exclude.append('ext_recommend')

        result = self.get_baidum_serp(keyword.strip(), date_range, pn, proxies, random_params)

        # 添加错误处理
        if isinstance(result, dict):
            return result
        
        html_content, recommend, ext_recommend = result

        return self.handle_response(html_content, keyword.strip(), recommend, ext_recommend, pn)