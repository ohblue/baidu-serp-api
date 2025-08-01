[English](#baidu-serp-api) | [中文](README_CN.md)

# Baidu SERP API

A Python library to extract data from Baidu Search Engine Results Pages (SERP) and output it as JSON objects.

## Installation

```bash
pip install baidu-serp-api
```

## Usage

### Basic Usage

```python
from baidu_serp_api import BaiduPc, BaiduMobile

# Basic usage (default optimized for proxy rotation)
pc_serp = BaiduPc()
results = pc_serp.search('keyword', date_range='20240501,20240531', pn='2', proxies={'http': 'http://your-proxy-server:port'})
print(results)

m_serp = BaiduMobile()
results = m_serp.search('keyword', date_range='day', pn='2', proxies={'http': 'http://your-proxy-server:port'})
print(results)

# Filter the specified content. The following returned results do not contain 'recommend', 'last_page', 'match_count'
results = m_serp.search('关键词', exclude=['recommend', 'last_page', 'match_count'])
```

### Network Connection Optimization

#### Connection Mode Configuration

```python
# Single connection mode (default, suitable for proxy rotation and scraping)
pc = BaiduPc(connection_mode='single')

# Connection pool mode (suitable for fixed proxy or high-performance scenarios)
pc = BaiduPc(connection_mode='pooled')

# Custom mode (fully customizable parameters)
pc = BaiduPc(
    connection_mode='custom',
    connect_timeout=5,
    read_timeout=15,
    pool_connections=5,
    pool_maxsize=20,
    keep_alive=True
)
```

#### Performance Monitoring

```python
# Get performance data
results = pc.search('keyword', include_performance=True)
if results['code'] == 200:
    performance = results['data']['performance']
    print(f"Response time: {performance['response_time']}s")
    print(f"Status code: {performance['status_code']}")
```

#### Resource Management

```python
# Manual resource management
pc = BaiduPc()
try:
    results = pc.search('keyword')
finally:
    pc.close()  # Manually release resources

# Recommended: Use context manager
with BaiduPc() as pc:
    results = pc.search('keyword')
# Automatically release resources
```

## Parameters

### Search Parameters

- `keyword`: The search keyword.
- `date_range` (optional): Search for results within the specified date range. the format should be a time range string like `'20240501,20240531'`, representing searching results between May 1, 2024, and May 31, 2024. 
- `pn` (optional): Search for results on the specified page.
- `proxies` (optional): Use proxies for searching.
- `exclude` (optional): Exclude specified fields, e.g., `['recommend', 'last_page']`.
- `include_performance` (optional): Whether to include performance data, default `False`.

### Connection Configuration Parameters

- `connection_mode`: Connection mode, options:
  - `'single'` (default): Single connection mode, suitable for proxy rotation
  - `'pooled'`: Connection pool mode, suitable for high-performance scenarios
  - `'custom'`: Custom mode, use custom parameters
- `connect_timeout`: Connection timeout in seconds, default 5
- `read_timeout`: Read timeout in seconds, default 10
- `max_retries`: Maximum retry count, default 0
- `pool_connections`: Number of connection pools, default 1
- `pool_maxsize`: Maximum connections per pool, default 1
- `keep_alive`: Whether to enable keep-alive, default `False`

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

### Successful Response

- `{'code': 200, 'msg': 'ok', 'data': {...}}`: Successful response
  - `results`: Search results list
  - `recommend`: Basic recommendation keywords (may be empty array)
  - `ext_recommend`: Extended recommendation keywords (mobile only, may be empty array)
  - `last_page`: Indicates whether it's the last page
  - `match_count`: Number of matching results
  - `performance` (optional): Performance data, contains `response_time` and `status_code`

### Error Response

#### Application Errors (400-499)
- `{'code': 404, 'msg': '未找到相关结果'}`: No relevant results found
- `{'code': 405, 'msg': '无搜索结果'}`: No search results

#### Server Errors (500-523)
- `{'code': 500, 'msg': '请求异常'}`: General network request exception
- `{'code': 501, 'msg': '百度安全验证'}`: Baidu security verification required
- `{'code': 502, 'msg': '响应提前结束'}`: Response data incomplete
- `{'code': 503, 'msg': '连接超时'}`: Connection timeout
- `{'code': 504, 'msg': '读取超时'}`: Read timeout
- `{'code': 505-510}`: Proxy-related errors (connection reset, auth failure, etc.)
- `{'code': 511-513}`: SSL-related errors (certificate verification, handshake failure, etc.)
- `{'code': 514-519}`: Connection errors (connection refused, DNS resolution failure, etc.)
- `{'code': 520-523}`: HTTP errors (403 forbidden, 429 rate limit, server error, etc.)

## Connection Optimization Best Practices

### Proxy Rotation Scenarios
```python
# Recommended configuration: default single mode is already optimized
with BaiduPc() as pc:  # Automatically uses single connection to avoid connection reuse issues
    for proxy in proxy_list:
        results = pc.search('keyword', proxies=proxy)
        # Process results...
```

### High-Performance Fixed Proxy Scenarios
```python
# Use pooled mode for better performance
with BaiduPc(connection_mode='pooled') as pc:
    results = pc.search('keyword', proxies=fixed_proxy)
    # Connection pool automatically manages connection reuse
```

### Error Handling and Retry
```python
def robust_search(keyword, max_retries=3):
    for attempt in range(max_retries):
        with BaiduPc() as pc:
            results = pc.search(keyword, include_performance=True)
            
            if results['code'] == 200:
                return results
            elif results['code'] in [503, 504]:  # Timeout errors
                continue  # Retry
            elif results['code'] in [505, 506, 514, 515]:  # Connection issues
                continue  # Retry
            else:
                break  # Don't retry other errors
    
    return results
```

## Mobile Extended Recommendations

Mobile version supports two types of recommendations:
- `recommend`: Basic recommendation keywords extracted directly from search results page
- `ext_recommend`: Extended recommendation keywords obtained through additional API call

How to get extended recommendations:

```python
# Get all recommendations (including extended recommendations)
results = m_serp.search('keyword', exclude=[])

# Get only basic recommendations (default behavior)
results = m_serp.search('keyword')  # equivalent to exclude=['ext_recommend']

# Get no recommendations
results = m_serp.search('keyword', exclude=['recommend'])  # automatically excludes ext_recommend
```

**Notes**:
- Extended recommendations require an additional network request and are only fetched on the first page (pn=1 or None)
- Extended recommendations depend on basic recommendations; if basic recommendations are excluded, extended recommendations are automatically excluded as well

## Disclaimer
This project is intended for educational purposes only and must not be used for commercial purposes or for large-scale scraping of Baidu data. This project is licensed under the GPLv3 open-source license. If other projects utilize the content of this project, they must be open-sourced and acknowledge the source. Additionally, the author of this project shall not be held responsible for any legal risks resulting from misuse. Violators will bear the consequences at their own risk.
