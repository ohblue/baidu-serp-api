# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python library for extracting data from Baidu Search Engine Results Pages (SERP) and returning structured JSON data. The library provides separate classes for desktop (`BaiduPc`) and mobile (`BaiduMobile`) Baidu search scraping.

## Architecture

### Core Components
- **`BaiduPc`**: Desktop Baidu search scraper class in `baidu_serp_api/baidu_pc.py`
- **`BaiduMobile`**: Mobile Baidu search scraper class in `baidu_serp_api/baidu_mobile.py`
- **`util.py`**: Shared utilities for parameter generation, HTML cleaning, and date formatting

### Key Functions
- `search()`: Main method in both classes that accepts `keyword`, `date_range`, `pn` (page number), `proxies`, and `exclude` parameters
- `extract_baidupc_data()` / `extract_baidum_data()`: HTML parsing methods that extract search results
- `gen_random_params()`: Generates randomized request parameters to avoid detection

### Response Format
All search methods return standardized JSON responses:
- `{'code': 200, 'msg': 'ok', 'data': {...}}`: Success
- `{'code': 404, 'msg': '未找到相关结果'}`: No results found
- `{'code': 403, 'msg': '疑似违禁词'}`: Suspected prohibited keywords
- `{'code': 500, 'msg': '网络请求错误'}`: Network request error
- `{'code': 501, 'msg': '百度安全验证'}`: Baidu security verification required

## Development Commands

### Testing
```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test files
python -m unittest tests.test_baidu_pc
python -m unittest tests.test_baidu_mobile
python -m unittest tests.test_util

# Run single test method
python -m unittest tests.test_baidu_pc.TestBaiduSerpApi.test_baidu_pc
```

### Local Development
The project runs directly from the local directory without installation. When working in the project root, Python will import from the local `baidu_serp_api/` directory.

For development installation:
```bash
pip install -e .
```

### Package Management
```bash
# Install dependencies
pip install -r requirements.txt

# Build package
python setup.py sdist bdist_wheel
```

## Technical Details

### Dependencies
- `requests`: HTTP client with SSL verification using `certifi.where()`
- `beautifulsoup4`: HTML parsing
- `loguru`: Logging utility
- Standard library: `datetime`, `json`, `re`, `uuid`, `hashlib`

### Security Features
- Random parameter generation to avoid detection patterns
- SSL certificate verification using certifi
- Proxy support for requests
- Session management with per-request isolation

### Data Extraction
- Desktop scraper targets `div[tpl="se_com_default"]` elements
- Mobile scraper targets `div[tpl="www_index"], div[tpl="www_struct"]` elements  
- Extracts title, URL, description, date, source, and ranking for each result
- Supports result filtering via `exclude` parameter

## Important Notes

- **License**: GPLv3 with educational use restriction - commercial use prohibited
- **Rate Limiting**: Implements random delays and parameter variation
- **Error Handling**: Comprehensive exception handling for network and parsing errors
- **Testing Framework**: Uses standard `unittest` (not pytest)