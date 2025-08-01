import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
from datetime import datetime
from .util import gen_random_params, clean_html_tags, convert_date_format, gen_mobile_cookies
import certifi
import time

class BaiduMobile:
    
    def __init__(self, connect_timeout=5, read_timeout=10, max_retries=0, pool_connections=1, pool_maxsize=1, keep_alive=False, connection_mode='single'):
        self.exclude = []
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout 
        self.max_retries = max_retries
        self.connection_mode = connection_mode
        
        # 根据连接模式设置参数
        if connection_mode == 'single':
            # 单连接模式：适合代理轮换，避免连接复用问题
            self.pool_connections = 1
            self.pool_maxsize = 1  
            self.keep_alive = False
        elif connection_mode == 'pooled':
            # 连接池模式：适合固定代理或高性能场景
            self.pool_connections = 10
            self.pool_maxsize = 20
            self.keep_alive = True
        else:  # 'custom'
            # 自定义模式：使用用户提供的参数
            self.pool_connections = pool_connections
            self.pool_maxsize = pool_maxsize
            self.keep_alive = keep_alive
            
        self._session = None
        self._setup_session()
    
    def _setup_session(self):
        """设置Session和连接池配置"""
        self._session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=0.3
        )
        
        # 配置HTTP适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize
        )
        
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
    
    def close(self):
        """关闭Session释放资源"""
        if self._session:
            self._session.close()
            self._session = None
    
    def __del__(self):
        """析构函数，确保资源正确释放"""
        self.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

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
        
        # 生成移动端Cookie用于推荐接口，传入random_params确保某些值一致
        mobile_cookies = gen_mobile_cookies(random_params)
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en',
            'Connection': 'close',
            'Cookie': mobile_cookies,
            'Host': 'm.baidu.com',
            'Referer': 'https://m.baidu.com/',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 baiduboxapp/13.10.0.10',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        }
        try:
            # 智能连接管理：根据代理使用情况自动调整
            should_close_connection = not self.keep_alive
            if proxies and self.connection_mode != 'custom':
                # 使用代理时强制关闭连接，避免代理轮换时的连接复用问题
                should_close_connection = True
            
            # 动态设置Connection头
            if should_close_connection:
                headers["Connection"] = "close"
            else:
                headers.pop("Connection", None)
                
            response = self._session.get(
                url,
                headers=headers,
                params=params,
                proxies=proxies,
                timeout=(self.connect_timeout, self.read_timeout),
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
        except requests.exceptions.RequestException:
            # 推荐词获取失败时返回空列表，不影响主搜索功能
            return []

    def get_baidum_serp(self, keyword, date_range, pn, proxies, random_params, need_ext_recommend=False):
        url = 'https://m.baidu.com/s'
        params = {
            'word': keyword,
            'ts': '0',
            't_kt': '0',
            'ie': 'utf-8',
            'rsv_iqid': random_params['rsv_iqid'],
            'rsv_t': random_params['rsv_t'],
            'sa': 'ib_d',
            'rsv_pq': random_params['rsv_iqid'],  # 通常与rsv_iqid相同
            'rsv_sug4': str(random_params['rsv_sug4']),
            'tj': '1',
            'inputT': str(random_params['inputT']),
            'sugid': random_params['sugid'],
            'ss': '100',
            'rqid': random_params['rqid'],
            'rfrom': '1024439e',
            'rchannel': '1024439k'
        }
        if date_range:
            start_date, end_date = date_range.split(',')
            start_timestamp = int(datetime.strptime(start_date, '%Y%m%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y%m%d').timestamp())
            params['gpc'] = f'stf={start_timestamp},{end_timestamp}|stftype=2'
        if pn:
            params['pn'] = str((int(pn) - 1) * 10)
            
        # 生成移动端Cookie，传入random_params确保某些值一致
        mobile_cookies = gen_mobile_cookies(random_params)
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en',
            'Cache-Control': 'max-age=0',
            'Connection': 'close',
            'Cookie': mobile_cookies,
            'Host': 'm.baidu.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36 baiduboxapp/13.10.0.10',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"'
        }
        try:
            start_time = time.time()
            
            # 智能连接管理：根据代理使用情况自动调整
            should_close_connection = not self.keep_alive
            if proxies and self.connection_mode != 'custom':
                # 使用代理时强制关闭连接，避免代理轮换时的连接复用问题
                should_close_connection = True
            
            # 动态设置Connection头
            if should_close_connection:
                headers["Connection"] = "close"
            else:
                headers.pop("Connection", None)
            
            response = self._session.get(
                url, 
                headers=headers, 
                params=params, 
                proxies=proxies, 
                timeout=(self.connect_timeout, self.read_timeout), 
                verify=certifi.where()
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            response_time = time.time() - start_time
            
            # # 检查302重定向到验证码页面
            # if response.status_code == 302:
            #     location = response.headers.get('Location', '')
            #     if 'wappass.baidu.com/static/captcha' in location or 'captcha' in response.text:
            #         return {"code": 501, "msg": "百度M安全验证"}
            
            # # 检查响应内容中的验证码链接
            # if 'wappass.baidu.com/static/captcha' in response.text:
            #     return {"code": 501, "msg": "百度M安全验证"}

            if need_ext_recommend:
                qid = response.headers.get('qid', None)
                ext_recommend = self.get_ext_recommend(keyword, qid, random_params, proxies) if qid else None
                return {
                    'content': response.text,
                    'response_time': response_time,
                    'status_code': response.status_code
                }, ext_recommend
            else:
                return {
                    'content': response.text,
                    'response_time': response_time,
                    'status_code': response.status_code
                }
            
        except requests.exceptions.ChunkedEncodingError:
            return {'code': 502, 'msg': '响应提前结束'}
        except requests.exceptions.ConnectTimeout:
            return {'code': 503, 'msg': '连接超时'}
        except requests.exceptions.ReadTimeout:
            return {'code': 504, 'msg': '读取超时'}
        except requests.exceptions.ProxyError as e:
            error_str = str(e).lower()
            if 'connection reset by peer' in error_str or 'broken pipe' in error_str:
                return {'code': 505, 'msg': '代理连接被重置'}
            elif 'remote end closed connection' in error_str or 'connection closed' in error_str:
                return {'code': 506, 'msg': '代理连接被远程关闭'}
            elif 'proxy authentication required' in error_str:
                return {'code': 507, 'msg': '代理认证失败'}
            elif 'connection refused' in error_str:
                return {'code': 508, 'msg': '代理连接被拒绝'}
            elif 'timeout' in error_str:
                return {'code': 509, 'msg': '代理连接超时'}
            else:
                return {'code': 510, 'msg': f'代理服务器错误: {str(e)}'}
        except requests.exceptions.SSLError as e:
            error_str = str(e).lower()
            if 'certificate verify failed' in error_str:
                return {'code': 511, 'msg': 'SSL证书验证失败'}
            elif 'ssl handshake' in error_str:
                return {'code': 512, 'msg': 'SSL握手失败'}
            else:
                return {'code': 513, 'msg': f'SSL连接错误: {str(e)}'}
        except requests.exceptions.ConnectionError as e:
            error_str = str(e).lower()
            if 'connection reset by peer' in error_str or 'broken pipe' in error_str:
                return {'code': 514, 'msg': '连接被重置'}
            elif 'remote end closed connection' in error_str or 'connection closed' in error_str:
                return {'code': 515, 'msg': '远程服务器关闭连接'}
            elif 'connection refused' in error_str:
                return {'code': 516, 'msg': '连接被拒绝'}
            elif 'name resolution failed' in error_str or 'nodename nor servname provided' in error_str:
                return {'code': 517, 'msg': 'DNS解析失败'}
            elif 'network is unreachable' in error_str:
                return {'code': 518, 'msg': '网络不可达'}
            else:
                return {'code': 519, 'msg': f'连接错误: {str(e)}'}
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 0
            if status_code == 403:
                return {'code': 520, 'msg': '访问被禁止(403)'}
            elif status_code == 429:
                return {'code': 521, 'msg': '请求过于频繁(429)'}
            elif status_code >= 500:
                return {'code': 522, 'msg': f'服务器错误({status_code})'}
            else:
                return {'code': 523, 'msg': f'HTTP错误({status_code}): {str(e)}'}
        except requests.exceptions.RequestException as e:
            return {'code': 500, 'msg': f'请求异常: {str(e)}'}


    def handle_response(self, response, keyword, recommend, ext_recommend, pn, include_performance=False):
        if isinstance(response, dict) and 'content' in response:
            html_content = response['content']
            response_time = response.get('response_time', 0)
            status_code = response.get('status_code', 200)
            
            # 检查百度安全验证 - 包括原有逻辑和验证码URL检测
            if ('百度安全验证' in html_content):
                return {'code': 501, 'msg': '百度M安全验证'}
            if '未找到相关结果' in html_content:
                return {'code': 404, 'msg': '未找到相关结果'}
            
            # 提前执行数据提取以便进行准确判断
            search_results, match_count = self.extract_baidum_data(html_content, keyword, pn)
            
            # 检查是否有搜索结果（基于实际提取的数据）
            if (
                not search_results
                and 'site:' not in keyword
                and not keyword.startswith(('http://', 'https://', 'www.', 'm.'))
            ):
                return {'code': 405, 'msg': '无搜索结果'}
            
            
            data = {
                'results': search_results,
                'recommend': recommend,
                'ext_recommend': ext_recommend,
                'last_page': 'new-nextpage' not in html_content,
                'match_count': match_count
            }
            
            # 添加性能数据（如果需要）
            if include_performance:
                data["performance"] = {
                    "response_time": round(response_time, 3),
                    "status_code": status_code
                }
            
            keys_to_delete = [key for key in self.exclude]
            for key in keys_to_delete:
                del data[key]
            return {'code': 200, 'msg': 'ok', 'data': data}
        elif isinstance(response, str):
            # 兼容旧格式
            if ('百度安全验证' in response):
                return {'code': 501, 'msg': '百度M安全验证'}
            if '未找到相关结果' in response:
                return {'code': 404, 'msg': '未找到相关结果'}
            
            search_results, match_count = self.extract_baidum_data(response, keyword, pn)
            
            if (
                not search_results
                and 'site:' not in keyword
                and not keyword.startswith(('http://', 'https://', 'www.', 'm.'))
            ):
                return {'code': 405, 'msg': '无搜索结果'}
            
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

    def search(self, keyword, date_range=None, pn=None, proxies=None, exclude=['ext_recommend'], include_performance=False):
        if exclude is not None:
            self.exclude = exclude

        random_params = gen_random_params()

        if 'recommend' in self.exclude and 'ext_recommend' not in self.exclude:
            self.exclude.append('ext_recommend')

        # 判断是否需要获取扩展推荐词
        need_ext_recommend = (pn is None or pn == 1) and 'ext_recommend' not in self.exclude
        
        result = self.get_baidum_serp(keyword.strip(), date_range, pn, proxies, random_params, need_ext_recommend)
        
        # 添加错误处理
        if isinstance(result, dict) and 'code' in result:
            return result
        
        # 根据返回值类型解包数据
        if need_ext_recommend:
            if isinstance(result, tuple):
                response, ext_recommend = result
            else:
                response = result
                ext_recommend = None
        else:
            response = result
            ext_recommend = None
        
        # 处理新的响应格式
        if isinstance(response, dict) and 'content' in response:
            html_content = response['content']
        else:
            html_content = response
        
        # 获取基础推荐词
        recommend = self.get_recommend(html_content)

        return self.handle_response(response, keyword.strip(), recommend, ext_recommend, pn, include_performance)