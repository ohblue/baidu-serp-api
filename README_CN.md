# 百度SERP API

一个用于从百度搜索结果页面（SERP）提取数据并将其输出为JSON对象的Python库。

## 安装

```bash
pip install baidu-serp-api
```

## 使用

### 基本使用

```python
from baidu_serp_api import BaiduPc, BaiduMobile

# 基本用法（默认优化适合代理轮换）
pc_serp = BaiduPc()
results = pc_serp.search('关键词', date_range='20240501,20240531', pn='2', proxies={'http': 'http://你的代理服务器:端口'})
print(results)

m_serp = BaiduMobile()
results = m_serp.search('关键词', date_range='20240501,20240531', pn='2', proxies={'http': 'http://你的代理服务器:端口'})
print(results)

# 过滤指定内容，以下返回的结果不含'recommend', 'last_page', 'match_count'
results = m_serp.search('关键词', exclude=['recommend', 'last_page', 'match_count'])
```

### 网络连接优化

#### 连接模式配置

```python
# 单连接模式（默认，适合代理轮换和爬虫应用）
pc = BaiduPc(connection_mode='single')

# 连接池模式（适合固定代理或高性能应用）
pc = BaiduPc(connection_mode='pooled')

# 自定义模式（完全自定义参数）
pc = BaiduPc(
    connection_mode='custom',
    connect_timeout=5,
    read_timeout=15,
    pool_connections=5,
    pool_maxsize=20,
    keep_alive=True
)
```

#### 性能监控

```python
# 获取性能数据
results = pc.search('关键词', include_performance=True)
if results['code'] == 200:
    performance = results['data']['performance']
    print(f"响应时间: {performance['response_time']}秒")
    print(f"状态码: {performance['status_code']}")
```

#### 资源管理

```python
# 手动管理资源
pc = BaiduPc()
try:
    results = pc.search('关键词')
finally:
    pc.close()  # 手动释放资源

# 推荐：使用上下文管理器
with BaiduPc() as pc:
    results = pc.search('关键词')
# 自动释放资源
```

## 参数

### 搜索参数

- `keyword`: 搜索关键词。
- `date_range` (可选): 在指定日期范围内搜索结果。格式应为一个时间范围字符串，如 `'20240501,20240531'`，表示搜索2024年5月1日至2024年5月31日之间的结果。
- `pn` (可选): 搜索指定页码的结果。
- `proxies` (可选): 使用代理进行搜索。
- `exclude` (可选): 排除指定字段，如 `['recommend', 'last_page']`。
- `include_performance` (可选): 是否包含性能数据，默认 `False`。

### 连接配置参数

- `connection_mode`: 连接模式，可选值：
  - `'single'` (默认): 单连接模式，适合代理轮换
  - `'pooled'`: 连接池模式，适合高性能场景
  - `'custom'`: 自定义模式，使用自定义参数
- `connect_timeout`: 连接超时时间（秒），默认 5
- `read_timeout`: 读取超时时间（秒），默认 10
- `max_retries`: 最大重试次数，默认 0
- `pool_connections`: 连接池数量，默认 1
- `pool_maxsize`: 每个连接池最大连接数，默认 1
- `keep_alive`: 是否启用keep-alive，默认 `False`

## 技术细节

### PC版请求头和Cookie

**主要请求参数：**
- `rsv_pq`: 随机查询参数（64位十六进制）
- `rsv_t`: 随机时间戳哈希
- `oq`: 原始查询词（与搜索关键词相同）

**Cookie参数（自动生成）：**
- `BAIDUID`: 唯一浏览器标识符（32位十六进制）
- `H_PS_645EC`: 与`rsv_t`参数同步
- `H_PS_PSSID`: 包含多个数字段的会话ID
- `BAIDUID_BFESS`: 与BAIDUID相同用于安全验证
- 另外13个Cookie用于完整的浏览器模拟

### 移动版请求头和Cookie

**主要请求参数：**
- `rsv_iqid`: 随机标识符（19位数字）
- `rsv_t`: 随机时间戳哈希
- `sugid`: 建议ID（14位数字）
- `rqid`: 请求ID（与rsv_iqid相同）
- `inputT`: 输入时间戳
- 另外11个参数用于移动端模拟

**Cookie参数（自动生成）：**
- `BAIDUID`: 与内部参数同步
- `H_WISE_SIDS`: 移动端专用会话，包含80个数字段
- `rsv_i`: 复杂编码字符串（64位字符）
- `__bsi`: 特殊会话ID格式
- `FC_MODEL`: 功能模型参数
- 另外14个Cookie用于移动端浏览器模拟

所有参数都会自动生成并同步，以确保逼真的浏览器行为。

## 返回值

### 成功响应

- `{'code': 200, 'msg': 'ok', 'data': {...}}`: 成功响应
  - `results`: 搜索结果列表
  - `recommend`: 推荐相关搜索词（可能为空数组）
  - `ext_recommend`: 扩展推荐词（仅移动端，可能为空数组）
  - `last_page`: 表示是否为最后一页
  - `match_count`: 匹配结果数量
  - `performance` (可选): 性能数据，包含 `response_time` 和 `status_code`

### 错误响应

#### 应用级错误（400-499）
- `{'code': 404, 'msg': '未找到相关结果'}`: 未找到相关结果
- `{'code': 405, 'msg': '无搜索结果'}`: 无搜索结果

#### 服务器错误（500-523）
- `{'code': 500, 'msg': '请求异常'}`: 一般网络请求异常
- `{'code': 501, 'msg': '百度安全验证'}`: 需要进行百度安全验证
- `{'code': 502, 'msg': '响应提前结束'}`: 响应数据不完整
- `{'code': 503, 'msg': '连接超时'}`: 连接建立超时
- `{'code': 504, 'msg': '读取超时'}`: 数据读取超时
- `{'code': 505-510}`: 代理相关错误（连接重置、认证失败等）
- `{'code': 511-513}`: SSL相关错误（证书验证、握手失败等）
- `{'code': 514-519}`: 连接错误（连接被拒绝、DNS解析失败等）
- `{'code': 520-523}`: HTTP错误（403禁止、429频率限制、服务器错误等）

## 连接优化最佳实践

### 代理轮换场景
```python
# 推荐配置：默认single模式已经优化
with BaiduPc() as pc:  # 自动使用单连接，避免连接复用问题
    for proxy in proxy_list:
        results = pc.search('关键词', proxies=proxy)
        # 处理结果...
```

### 高性能固定代理场景
```python
# 使用连接池模式提升性能
with BaiduPc(connection_mode='pooled') as pc:
    results = pc.search('关键词', proxies=fixed_proxy)
    # 连接池会自动管理连接复用
```

### 错误处理和重试
```python
def robust_search(keyword, max_retries=3):
    for attempt in range(max_retries):
        with BaiduPc() as pc:
            results = pc.search(keyword, include_performance=True)
            
            if results['code'] == 200:
                return results
            elif results['code'] in [503, 504]:  # 超时错误
                continue  # 重试
            elif results['code'] in [505, 506, 514, 515]:  # 连接问题
                continue  # 重试
            else:
                break  # 其他错误不重试
    
    return results
```

## 移动端扩展推荐词

移动端支持两种推荐词：
- `recommend`: 从搜索结果页面直接提取的基础推荐词
- `ext_recommend`: 通过额外API调用获取的扩展推荐词

获取扩展推荐词的方式：

```python
# 获取所有推荐词（包括扩展推荐词）
results = m_serp.search('关键词', exclude=[])

# 只获取基础推荐词（默认行为）
results = m_serp.search('关键词')  # 等同于 exclude=['ext_recommend']

# 不获取任何推荐词
results = m_serp.search('关键词', exclude=['recommend'])  # 自动排除ext_recommend
```

**注意**：
- 扩展推荐词需要额外的网络请求，仅在第一页(pn=1或None)时获取
- 扩展推荐词依赖基础推荐词，如果排除了基础推荐词，扩展推荐词也会被自动排除

## 免责声明

本项目仅供学习之用，不可用于商业目的或大规模爬取百度数据。本项目采用GPLv3开源许可，若涉及到其他项目使用本项目内容，需开源并注明来源。同时，本项目作者不对滥用行为可能导的法律风险承担责任，违者自负后果。