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

- `{'code': 500, 'msg': '网络请求错误'}`: 网络请求失败需要重试。
- `{'code': 501, 'msg': '百度安全验证'}`: 需要进行百度安全验证。
- `{'code': 404, 'msg': '未找到相关结果'}`: 未找到相关结果。
- `{'code': 405, 'msg': '无搜索结果'}`: 无搜索结果。
- `{'code': 200, 'msg': 'ok', 'data': {'results': [], 'recommend': [], 'last_page': True}}`: 成功响应。
    - `results` 搜索结果列表。
    - `recommend` 推荐相关搜索词（可能为空数组）。
    - `ext_recommend` 扩展推荐词（仅移动端，可能为空数组）。
    - `last_page` 表示是否为最后一页。

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