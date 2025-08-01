import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
from datetime import datetime
from .util import gen_random_params, clean_html_tags, convert_date_format, gen_pc_cookies
import re
import certifi
import time

class BaiduPc:

    def __init__(self, connect_timeout=5, read_timeout=10, max_retries=0, pool_connections=10, pool_maxsize=10, keep_alive=False):
        self.exclude = []
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout 
        self.max_retries = max_retries
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

    def extract_baidupc_data(self, html_content, keyword):
        soup = BeautifulSoup(html_content, "html.parser")
        search_results = soup.select('div[tpl="www_index"], div[tpl="www_struct"]')
        result_data = []
        match_count = 0
        for result in search_results:
            # 更新标题选择器 - 直接选择h3元素
            title_element = result.select_one("h3")

            url = result.get("mu")

            description = ""
            date_time = ""
            source = ""

            ranking = result.get("id", 0)

            # 更新描述选择器 - 根据实际HTML结构
            summary_element = result.select_one('span.summary-text_560AW')
            if summary_element:
                description = clean_html_tags(summary_element.get_text().strip())

            # 更新日期选择器 - 更精确匹配
            date_time_element = result.select_one("span.cos-space-mr-3xs.cos-color-text-minor")
            if date_time_element:
                date_time = date_time_element.get_text().strip()
                date_time = convert_date_format(date_time)

            # 更新来源选择器 - 根据实际HTML结构  
            source_element = result.select_one("span.cosc-source-text")
            if source_element:
                source = source_element.get_text().strip()

            if title_element and url:
                title_text = clean_html_tags(title_element.get_text().strip())
                if keyword in title_text:
                    match_count += 1
                result_data.append(
                    {
                        "title": title_text,
                        "url": url,
                        "description": description,
                        "date_time": date_time,
                        "source": source,
                        "ranking": ranking,
                    }
                )

        return result_data, match_count

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
                for item in json_data["list"]:
                    keyword_set.add(item["text"])
            elif '"newList"' in comment:
                json_data = json.loads(comment)
                for sublist in json_data["newList"]:
                    for item in sublist:
                        keyword_set.add(item["word"])

        recommend = list(keyword_set)
        return recommend

    def get_baidupc_serp(self, keyword, date_range, pn, proxies, random_params):
        url = "http://www.baidu.com/s"

        params = {
            "wd": keyword,
            "ie": "utf-8",
            "f": "8",
            "rsv_bp": "1",
            "tn": "baidu",
            "oq": keyword,  # 原始查询，与wd相同
            "rsv_pq": random_params["rsv_pq"],
            "rsv_t": random_params["rsv_t"],
            "rqlang": "cn",
            "rsv_dl": "tb",
            "rsv_enter": "0",  # 浏览器使用0
            "rsv_btype": "t",  # 浏览器使用t
        }

        # 搜索词为site:xxx时, 增加si和ct参数
        if "site:" in keyword:
            site = keyword.split("site:")[1].strip()
            params["si"] = site
            params["ct"] = "2097152"

        # 搜索指定日期范围
        if date_range:
            start_date, end_date = date_range.split(",")
            start_timestamp = int(datetime.strptime(start_date, "%Y%m%d").timestamp())
            end_timestamp = int(datetime.strptime(end_date, "%Y%m%d").timestamp())
            params["gpc"] = f"stf={start_timestamp},{end_timestamp}|stftype=2"

        # 搜索指定页码
        if pn:
            params["pn"] = str((int(pn) - 1) * 10)

        # logger.debug(params)
        # 生成逼真的PC端Cookie，传入random_params确保某些值一致
        pc_cookies = gen_pc_cookies(random_params)
        
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "close",
            "Cookie": pc_cookies,
            "Host": "www.baidu.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate", 
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }

        try:
            start_time = time.time()
            
            # 动态设置Connection头
            if not self.keep_alive:
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
            
            response_time = time.time() - start_time
            response.raise_for_status()
            
            # 确保正确的编码处理
            # 由于已安装brotli，requests会自动处理br压缩
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            elif response.apparent_encoding:
                response.encoding = response.apparent_encoding
            
            # # 检查302重定向到验证码页面
            # if response.status_code == 302:
            #     location = response.headers.get('Location', '')
            #     if 'wappass.baidu.com/static/captcha' in location or 'captcha' in response.text:
            #         return {"code": 501, "msg": "百度PC安全验证"}
            
            # # 检查响应内容中的验证码链接
            # if 'wappass.baidu.com/static/captcha' in response.text:
            #     return {"code": 501, "msg": "百度PC安全验证"}
            
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

    def handle_response(self, response, keyword, recommend, include_performance=False):
        if isinstance(response, dict) and 'content' in response:
            html_content = response['content']
            response_time = response.get('response_time', 0)
            status_code = response.get('status_code', 200)
            
            # 检查百度安全验证 - 包括原有逻辑和验证码URL检测
            if ("百度安全验证" in html_content or 
                html_content.strip() == ""):
                return {"code": 501, "msg": "百度PC安全验证"}
            if "未找到相关结果" in html_content:
                return {"code": 404, "msg": "未找到相关结果"}
            
            # 提前执行数据提取以便进行准确判断
            search_results, match_count = self.extract_baidupc_data(html_content, keyword)
            
            # 检查是否有搜索结果（基于实际提取的数据）
            if (
                not search_results
                and "site:" not in keyword
                and not keyword.startswith(("http://", "https://", "www.", "m."))
            ):
                return {"code": 405, "msg": "无搜索结果"}
            

            data = {
                "results": search_results,
                "recommend": recommend,
                "last_page": "下一页" not in html_content,
                "match_count": match_count,
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
            return {"code": 200, "msg": "ok", "data": data}
        elif isinstance(response, str):
            # 兼容旧格式
            if ("百度安全验证" in response or 
                response.strip() == ""):
                return {"code": 501, "msg": "百度PC安全验证"}
            if "未找到相关结果" in response:
                return {"code": 404, "msg": "未找到相关结果"}
            
            search_results, match_count = self.extract_baidupc_data(response, keyword)
            
            if (
                not search_results
                and "site:" not in keyword
                and not keyword.startswith(("http://", "https://", "www.", "m."))
            ):
                return {"code": 405, "msg": "无搜索结果"}

            data = {
                "results": search_results,
                "recommend": recommend,
                "last_page": "下一页" not in response,
                "match_count": match_count,
            }
            keys_to_delete = [key for key in self.exclude]
            for key in keys_to_delete:
                del data[key]
            return {"code": 200, "msg": "ok", "data": data}
        else:
            return response

    def search(self, keyword, date_range=None, pn=None, proxies=None, exclude=None, include_performance=False):
        if exclude is not None:
            self.exclude = exclude

        random_params = gen_random_params()

        response = self.get_baidupc_serp(
            keyword.strip(), date_range, pn, proxies, random_params
        )

        # 添加错误处理
        if isinstance(response, dict) and 'code' in response:
            return response

        # 处理新的响应格式
        if isinstance(response, dict) and 'content' in response:
            html_content = response['content']
        else:
            html_content = response
        
        recommend = self.get_recommend(html_content)
        
        return self.handle_response(response, keyword.strip(), recommend, include_performance)
