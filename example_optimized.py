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
    # 基本使用（使用默认single模式，适合代理轮换）
    print("=== 基本使用示例（单连接模式）===")
    pc = BaiduPc()  # 默认为single模式，适合代理轮换
    result = pc.search("Python编程")
    print(f"搜索结果数量: {len(result.get('data', {}).get('results', []))}")
    pc.close()  # 手动释放资源
    
    # 连接池模式（适合固定代理或高性能场景）
    print("\n=== 连接池模式示例 ===")
    pc_pooled = BaiduPc(connection_mode='pooled')
    result = pc_pooled.search("机器学习")
    print(f"连接池模式搜索结果: {len(result.get('data', {}).get('results', []))}")
    pc_pooled.close()
    
    # 自定义配置模式
    print("\n=== 自定义配置示例 ===")
    pc_custom = BaiduPc(
        connection_mode='custom',  # 使用自定义参数
        connect_timeout=3,         # 连接超时3秒
        read_timeout=15,           # 读取超时15秒
        max_retries=2,             # 最大重试2次
        pool_connections=5,        # 连接池大小
        pool_maxsize=20,           # 连接池最大连接数
        keep_alive=True            # 启用keep-alive
    )
    
    # 获取性能数据
    result = pc_custom.search("Python编程", include_performance=True)
    if result.get('code') == 200:
        performance = result.get('data', {}).get('performance', {})
        if performance:
            print(f"响应时间: {performance.get('response_time', 0)}秒")
            print(f"状态码: {performance.get('status_code', 'N/A')}")
    pc_custom.close()
    
    # 智能代理管理示例
    print("\n=== 智能代理管理示例 ===")
    proxy = {'http': 'http://proxy.example.com:8080', 'https': 'https://proxy.example.com:8080'}
    
    # 使用代理时，即使是pooled模式也会自动启用单连接
    with BaiduPc(connection_mode='pooled') as pc_proxy:
        result = pc_proxy.search("深度学习", proxies=proxy, include_performance=True)
        print("使用代理时自动启用单连接模式以避免连接复用问题")
    
    # 使用上下文管理器（推荐方式）
    print("\n=== 上下文管理器示例 ===")
    with BaiduMobile() as mobile:  # 默认single模式
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
    
    print("\n=== 连接模式对比 ===")
    print("🔹 single模式 (默认):")
    print("  - 适合: 代理轮换、爬虫应用")
    print("  - 特点: 每次新连接，避免连接复用问题")
    print("  - 参数: pool_connections=1, pool_maxsize=1, keep_alive=False")
    
    print("\n🔹 pooled模式:")
    print("  - 适合: 固定代理、高性能应用")
    print("  - 特点: 连接池复用，提升性能")
    print("  - 参数: pool_connections=10, pool_maxsize=20, keep_alive=True")
    
    print("\n🔹 custom模式:")
    print("  - 适合: 需要精确控制的场景")
    print("  - 特点: 完全自定义所有参数")
    
    print("\n=== 优化功能总结 ===")
    print("1. ✅ 智能连接模式 - 根据使用场景自动优化")
    print("2. ✅ 代理智能管理 - 使用代理时自动启用单连接")
    print("3. ✅ 类级别Session复用 - 提升连接效率")
    print("4. ✅ 分离连接和读取超时 - 精确控制超时行为")
    print("5. ✅ 连接池配置 - 优化并发性能")
    print("6. ✅ Keep-alive选项 - 减少连接开销")
    print("7. ✅ 性能数据监控 - 响应时间统计")
    print("8. ✅ 细分错误处理 - 精确的错误分类")
    print("9. ✅ 资源管理 - 自动和手动资源释放")
    print("10. ✅ 上下文管理器 - 确保资源正确清理")

if __name__ == "__main__":
    main()