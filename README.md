[English](#baidu-serp-api) | [中文](#百度SERP-API)

# Baidu SERP API

A Python library to extract data from Baidu Search Engine Results Pages (SERP) and output it as JSON objects.

## Installation

```bash
pip install baidu-serp-api
```

## Usage

```python
from baidu_serp_api import BaiduPc, BaiduMobile

pc_serp = BaiduPc()
results = pc_serp.search('keyword', date_range='20240501,20240531', pn='2', proxies={'http': 'http://your-proxy-server:port'})
print(results)

m_serp = BaiduMobile()
results = m_serp.search('keyword', date_range='day', pn='2', proxies={'http': 'http://your-proxy-server:port'})
print(results)
```

### Parameters

- `keyword`: The search keyword.
- `date_range` (optional): Search for results within the specified date range. the format should be a time range string like `'20240501,20240531'`, representing searching results between May 1, 2024, and May 31, 2024. 
- `pn` (optional): Search for results on the specified page.
- `proxies` (optional): Use proxies for searching.

### Return Values

- `{'code': 40001, 'msg': '百度安全验证'}`: Baidu security verification required.
- `{'code': 40002, 'msg': '未找到相关结果'}`: No relevant results found.
- `{'code': 40003, 'msg': '疑似违禁词'}`: Suspected prohibited word.
- `{'code': 20000, 'msg': 'ok', 'data': {'results': [], 'recommend': [], last_page': True}}`: Successful response. 
    - `results` search results list.
    - `recommend` recommend keywords.
    - `last_page` indicates whether it's the last page.




# 百度SERP API

一个用于从百度搜索结果页面（SERP）提取数据并将其输出为JSON对象的Python库。

## 安装

```bash
pip install baidu-serp-api
```

## 使用

```python
from baidu_serp_api import BaiduPc, BaiduMobile

pc_serp = BaiduPc()
results = pc_serp.search('关键词', date_range='20240501,20240531', pn='2', proxies={'http': 'http://你的代理服务器:端口'})
print(results)

m_serp = BaiduMobile()
results = m_serp.search('关键词', date_range='day', pn='2', proxies={'http': 'http://你的代理服务器:端口'})
print(results)
```

### 参数

- `keyword`: 搜索关键词。
- `date_range` (可选): 在指定日期范围内搜索结果。格式应为一个时间范围字符串，如 `'20240501,20240531'`，表示搜索2024年5月1日至2024年5月31日之间的结果。
- `pn` (可选): 搜索指定页码的结果。
- `proxies` (可选): 使用代理进行搜索。

### 返回值

- `{'code': 40001, 'msg': '百度安全验证'}`: 需要进行百度安全验证。
- `{'code': 40002, 'msg': '未找到相关结果'}`: 未找到相关结果。
- `{'code': 40003, 'msg': '疑似违禁词'}`: 疑似违禁词。
- `{'code': 20000, 'msg': 'ok', 'data': {'results': [], 'last_page': True}}`: 成功响应。
    - `results` 搜索结果列表。
    - `recommend` 推荐相关搜索词。
    - `last_page` 表示是否为最后一页。
