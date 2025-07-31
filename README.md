[English](#baidu-serp-api) | [中文](README_CN.md)

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

# Filter the specified content. The following returned results do not contain 'recommend', 'last_page', 'match_count'
results = m_serp.search('关键词', exclude=['recommend', 'last_page', 'match_count'])
```

## Parameters

- `keyword`: The search keyword.
- `date_range` (optional): Search for results within the specified date range. the format should be a time range string like `'20240501,20240531'`, representing searching results between May 1, 2024, and May 31, 2024. 
- `pn` (optional): Search for results on the specified page.
- `proxies` (optional): Use proxies for searching.

## Technical Details

### PC Version Request Headers & Cookies

**Key Request Parameters:**
- `rsv_pq`: Random query parameter (64-bit hex)
- `rsv_t`: Random timestamp hash
- `oq`: Original query (same as search keyword)

**Cookie Parameters (automatically generated):**
- `BAIDUID`: Unique browser identifier (32-char hex)
- `H_PS_645EC`: Synchronized with `rsv_t` parameter
- `H_PS_PSSID`: Session ID with multiple numeric segments
- `BAIDUID_BFESS`: Same as BAIDUID for security
- Plus 13 additional cookies for complete browser simulation

### Mobile Version Request Headers & Cookies

**Key Request Parameters:**
- `rsv_iqid`: Random identifier (19 digits)
- `rsv_t`: Random timestamp hash
- `sugid`: Suggestion ID (14 digits)
- `rqid`: Request ID (same as rsv_iqid)
- `inputT`: Input timestamp
- Plus 11 additional parameters for mobile simulation

**Cookie Parameters (automatically generated):**
- `BAIDUID`: Synchronized with internal parameters
- `H_WISE_SIDS`: Mobile-specific session with 80 numeric segments
- `rsv_i`: Complex encoded string (64 chars)
- `__bsi`: Special session ID format
- `FC_MODEL`: Feature model parameters
- Plus 14 additional cookies for mobile browser simulation

All parameters are automatically generated and synchronized to ensure realistic browser behavior.

## Return Values

- `{'code': 500, 'msg': '网络请求错误'}`: Network request exception.
- `{'code': 501, 'msg': '百度安全验证'}`: Baidu security verification required.
- `{'code': 404, 'msg': '未找到相关结果'}`: No relevant results found.
- `{'code': 405, 'msg': '无搜索结果'}`: No search results.
- `{'code': 406, 'msg': '无推荐词'}`: No recommended keywords.
- `{'code': 200, 'msg': 'ok', 'data': {'results': [], 'recommend': [], last_page': True}}`: Successful response. 
    - `results` search results list.
    - `recommend` recommend keywords.
    - `last_page` indicates whether it's the last page.

## Disclaimer
This project is intended for educational purposes only and must not be used for commercial purposes or for large-scale scraping of Baidu data. This project is licensed under the GPLv3 open-source license. If other projects utilize the content of this project, they must be open-sourced and acknowledge the source. Additionally, the author of this project shall not be held responsible for any legal risks resulting from misuse. Violators will bear the consequences at their own risk.
