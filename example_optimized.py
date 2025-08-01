#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版本使用示例

展示新的网络连接优化功能：
- 自定义超时配置
- 连接池参数调整
- 性能数据获取
- 资源管理
"""

from baidu_serp_api import BaiduPc, BaiduMobile

def main():
    # 基本使用（使用默认配置）
    print("=== 基本使用示例 ===")
    pc = BaiduPc()
    result = pc.search("Python编程")
    print(f"搜索结果数量: {len(result.get('data', {}).get('results', []))}")
    pc.close()  # 手动释放资源
    
    # 自定义网络配置
    print("\n=== 自定义网络配置示例 ===")
    pc_custom = BaiduPc(
        connect_timeout=3,       # 连接超时3秒
        read_timeout=15,         # 读取超时15秒
        max_retries=2,           # 最大重试2次
        pool_connections=5,      # 连接池大小
        pool_maxsize=20,         # 连接池最大连接数
        keep_alive=True          # 启用keep-alive
    )
    
    # 获取性能数据
    result = pc_custom.search("Python编程", include_performance=True)
    if result.get('code') == 200:
        performance = result.get('data', {}).get('performance', {})
        if performance:
            print(f"响应时间: {performance.get('response_time', 0)}秒")
            print(f"状态码: {performance.get('status_code', 'N/A')}")
    pc_custom.close()
    
    # 使用上下文管理器（推荐方式）
    print("\n=== 上下文管理器示例 ===")
    with BaiduMobile(connect_timeout=5, read_timeout=12) as mobile:
        result = mobile.search("机器学习", include_performance=True)
        if result.get('code') == 200:
            results = result.get('data', {}).get('results', [])
            performance = result.get('data', {}).get('performance', {})
            print(f"移动端搜索结果: {len(results)} 条")
            if performance:
                print(f"响应时间: {performance.get('response_time', 0)}秒")
    
    # 错误处理示例
    print("\n=== 错误处理示例 ===")
    with BaiduPc(connect_timeout=1, read_timeout=1) as pc_timeout:
        result = pc_timeout.search("测试超时")
        if result.get('code') != 200:
            print(f"错误码: {result.get('code')}")
            print(f"错误信息: {result.get('msg')}")
    
    print("\n=== 优化功能总结 ===")
    print("1. ✅ 类级别Session复用 - 提升连接效率")
    print("2. ✅ 分离连接和读取超时 - 精确控制超时行为")
    print("3. ✅ 连接池配置 - 优化并发性能")
    print("4. ✅ Keep-alive选项 - 减少连接开销")
    print("5. ✅ 性能数据监控 - 响应时间统计")
    print("6. ✅ 细分错误处理 - 精确的错误分类")
    print("7. ✅ 资源管理 - 自动和手动资源释放")
    print("8. ✅ 上下文管理器 - 确保资源正确清理")

if __name__ == "__main__":
    main()