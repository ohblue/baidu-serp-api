import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from .util import gen_random_params, clean_html_tags, convert_date_format, gen_pc_cookies
import re
import certifi

class BaiduPc:

    def __init__(self):
        self.exclude = []

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
        # 生成逼真的PC端Cookie
        pc_cookies = gen_pc_cookies()
        
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
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
                
                recommend = self.get_recommend(response.text)
                return response.text, recommend
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

    def handle_response(self, response, keyword, recommend):
        if isinstance(response, str):
            # 检查百度安全验证 - 包括原有逻辑和验证码URL检测
            if ("百度安全验证" in response or 
                response.strip() == ""):
                return {"code": 501, "msg": "百度PC安全验证"}
            if "未找到相关结果" in response:
                return {"code": 404, "msg": "未找到相关结果"}
            
            # 提前执行数据提取以便进行准确判断
            search_results, match_count = self.extract_baidupc_data(response, keyword)
            
            # 检查是否有搜索结果（基于实际提取的数据）
            if (
                not search_results
                and "site:" not in keyword
                and not keyword.startswith(("http://", "https://", "www.", "m."))
            ):
                return {"code": 405, "msg": "无搜索结果"}
            
            # 检查是否有推荐词
            if (
                not recommend
                and "site:" not in keyword
                and not keyword.startswith(("http://", "https://", "www.", "m."))
            ):
                return {"code": 406, "msg": "无推荐词"}

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

    def search(self, keyword, date_range=None, pn=None, proxies=None, exclude=None):
        if exclude is not None:
            self.exclude = exclude

        random_params = gen_random_params()

        result = self.get_baidupc_serp(
            keyword.strip(), date_range, pn, proxies, random_params
        )

        # 添加错误处理
        if isinstance(result, dict):
            return result

        html_content, recommend = result
        
        return self.handle_response(html_content, keyword.strip(), recommend)
