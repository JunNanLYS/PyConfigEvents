#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置文件转模型示例

这个示例展示了如何从JSON和TOML配置文件读取数据并转换为RootModel对象。
"""

import os
import tempfile
import json

from pyconfigevents import RootModel, ChildModel, read_config


# 定义应用配置模型
class AppConfig(RootModel):
    name: str
    version: str
    debug: bool = False
    features: list = []
    
    # 嵌套配置
    class ServerConfig(ChildModel):
        host: str = "localhost"
        port: int = 8000
        timeout: int = 30
    
    server: ServerConfig


def create_json_config():
    """创建一个临时的JSON配置文件"""
    config_data = {
        "name": "我的应用",
        "version": "1.0.0",
        "debug": True,
        "features": ["登录", "注册", "用户管理"],
        "server": {
            "host": "127.0.0.1",
            "port": 5000,
            "timeout": 60
        }
    }
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_file.write(json.dumps(config_data, ensure_ascii=False).encode('utf-8'))
        return temp_file.name


def create_toml_config():
    """创建一个临时的TOML配置文件"""
    config_content = '''
    name = "我的应用"
    version = "1.0.0"
    debug = true
    features = ["登录", "注册", "用户管理"]
    
    [server]
    host = "127.0.0.1"
    port = 5000
    timeout = 60
    '''
    
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as temp_file:
        temp_file.write(config_content.encode('utf-8'))
        return temp_file.name


def main():
    # 创建临时配置文件
    json_path = create_json_config()
    toml_path = create_toml_config()
    
    try:
        # 从JSON文件读取配置
        print("\n从JSON文件读取配置:")
        json_config_dict = read_config(json_path)
        json_app_config = AppConfig(**json_config_dict)
        
        # 打印配置信息
        print(f"应用名称: {json_app_config.name}")
        print(f"版本: {json_app_config.version}")
        print(f"调试模式: {json_app_config.debug}")
        print(f"功能列表: {', '.join(json_app_config.features)}")
        print(f"服务器配置: {json_app_config.server.host}:{json_app_config.server.port} (超时: {json_app_config.server.timeout}秒)")
        
        # 订阅配置变更
        def on_debug_change(new_value):
            print(f"调试模式已{'开启' if new_value else '关闭'}")
        
        json_app_config.subscribe("debug", on_debug_change)
        
        # 修改配置并触发事件
        print("\n修改配置:")
        json_app_config.debug = False
        
        # 从TOML文件读取配置
        print("\n从TOML文件读取配置:")
        toml_config_dict = read_config(toml_path)
        toml_app_config = AppConfig(**toml_config_dict)
        
        # 打印配置信息
        print(f"应用名称: {toml_app_config.name}")
        print(f"版本: {toml_app_config.version}")
        print(f"调试模式: {toml_app_config.debug}")
        print(f"功能列表: {', '.join(toml_app_config.features)}")
        print(f"服务器配置: {toml_app_config.server.host}:{toml_app_config.server.port} (超时: {toml_app_config.server.timeout}秒)")
        
    finally:
        # 清理临时文件
        os.unlink(json_path)
        os.unlink(toml_path)


if __name__ == "__main__":
    main()