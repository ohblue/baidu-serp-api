import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from .util import gen_random_params, clean_html_tags, convert_date_format
import re
import certifi

class BaiduPc:

    def __init__(self):
        self.exclude = []

    def extract_baidupc_data(self, html_content, keyword):
        soup = BeautifulSoup(html_content, "html.parser")
        search_results = soup.select('div[tpl="se_com_default"]')
        result_data = []
        match_count = 0
        for result in search_results:
            title_element = result.select_one("h3.c-title")

            url = result.get("mu")

            description = ""
            date_time = ""
            source = ""

            ranking = result.get("id", 0)

            summary_element = result.select_one('span[class^="content-right_"]')
            if summary_element:
                description = clean_html_tags(summary_element.get_text().strip())

            date_time_element = result.select_one("span.c-color-gray2")
            if date_time_element:
                date_time = date_time_element.get_text().strip()
                date_time = convert_date_format(date_time)

            source_element = result.select_one("span.c-color-gray")
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
            "rsv_idx": "1",
            "tn": "baidu",
            "fenlei": "256",
            "rqlang": "cn",
            "rsv_enter": "1",
            "rsv_dl": "tb",
            "rsv_btype": "i",
            "inputT": "2751",
            "mod": "1",
            "isbd": "1",
            "isid": random_params["isid"],
            "rsv_pq": random_params["rsv_pq"],
            "rsv_t": random_params["rsv_t"],
            "tfflag": "1",
            "bs": keyword,
            "rsv_sid": random_params["rsv_sid"],
            "_ss": "1",
            "clist": random_params["clist"],
            "hsug": "",
            "f4s": "1",
            "csor": "20",
            "_cr1": random_params["_cr1"],
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
        headers = {
            "cookie": f'BAIDUID={random_params["baiduid"]}:FG=1; BAIDUID_BFESS={random_params["baiduid"]}:FG=1; '
            f'BDUSS={random_params["bduss"]}; H_PS_645EC={random_params["rsv_t"]}; H_PS_PSSID={random_params["rsv_sid"]}',
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Connection": "close",
        }

        try:
            with requests.Session() as session:
                response = session.get(
                    url,
                    headers=headers,
                    params=params,
                    proxies=proxies,
                    timeout=10,
                    verify=certifi.where(),
                    allow_redirects=False,
                )
                response.raise_for_status()
                response.encoding = "utf-8"
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
            if "百度安全验证" in response or response.strip() == "":
                return {"code": 501, "msg": "百度PC安全验证"}
            if "未找到相关结果" in response:
                return {"code": 404, "msg": "未找到相关结果"}
            if (
                "相关搜索" not in response
                and "site:" not in keyword
                and not keyword.startswith(("http://", "https://", "www.", "m."))
            ):
                return {"code": 403, "msg": "疑似违禁词或推荐词为空"}

            # 从 extract_baidum_data 获取搜索结果和匹配计数
            search_results, match_count = self.extract_baidupc_data(response, keyword)

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
