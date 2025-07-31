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
results = m_serp.search('关键词', date_range='20240501,20240531', pn='2', proxies={'http': 'http://你的代理服务器:端口'})
print(results)

# 过滤指定内容，以下返回的结果不含'recommend', 'last_page', 'match_count'
results = m_serp.search('关键词', exclude=['recommend', 'last_page', 'match_count'])
```

## 参数

- `keyword`: 搜索关键词。
- `date_range` (可选): 在指定日期范围内搜索结果。格式应为一个时间范围字符串，如 `'20240501,20240531'`，表示搜索2024年5月1日至2024年5月31日之间的结果。
- `pn` (可选): 搜索指定页码的结果。
- `proxies` (可选): 使用代理进行搜索。

## 返回值

- `{'code': 500, 'msg': '网络请求错误'}`: 网络请求失败需要重试。
- `{'code': 501, 'msg': '百度安全验证'}`: 需要进行百度安全验证。
- `{'code': 404, 'msg': '未找到相关结果'}`: 未找到相关结果。
- `{'code': 405, 'msg': '无搜索结果'}`: 无搜索结果。
- `{'code': 406, 'msg': '无推荐词'}`: 无推荐词。
- `{'code': 200, 'msg': 'ok', 'data': {'results': [], 'last_page': True}}`: 成功响应。
    - `results` 搜索结果列表。
    - `recommend` 推荐相关搜索词。
    - `last_page` 表示是否为最后一页。

## 免责声明

本项目仅供学习之用，不可用于商业目的或大规模爬取百度数据。本项目采用GPLv3开源许可，若涉及到其他项目使用本项目内容，需开源并注明来源。同时，本项目作者不对滥用行为可能导的法律风险承担责任，违者自负后果。