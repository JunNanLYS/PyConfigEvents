#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
应用场景示例

这个示例展示了如何在实际应用中使用PyConfigEvents库，
实现实时配置更新和事件通知功能。
"""

import time
from threading import Thread
from typing import List, Optional

from pyconfigevents import DataModel


# 定义应用配置模型
class LogConfig(DataModel):
    level: str = "INFO"
    file_path: Optional[str] = None
    console_output: bool = True
    max_size: int = 10  # MB


class DatabaseConfig(DataModel):
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = ""
    database: str = "app_db"
    pool_size: int = 5
    timeout: int = 30


class AppConfig(DataModel):
    app_name: str = "示例应用"
    debug: bool = False
    log: LogConfig = LogConfig()
    database: DatabaseConfig = DatabaseConfig()
    allowed_ips: List[str] = ["127.0.0.1"]
    max_connections: int = 100


# 模拟应用组件
class Logger:
    def __init__(self, config: LogConfig):
        self.config = config
        self._setup_logger()
        
        # 订阅配置变更
        self.config.subscribe("level", self._on_level_change)
        self.config.subscribe("file_path", self._on_file_path_change)
        self.config.subscribe("console_output", self._on_console_output_change)
    
    def _setup_logger(self):
        print(f"[Logger] 初始化日志系统: 级别={self.config.level}, 文件路径={self.config.file_path}, 控制台输出={self.config.console_output}")
    
    def _on_level_change(self, new_level):
        print(f"[Logger] 日志级别已更改为: {new_level}")
    
    def _on_file_path_change(self, new_path):
        if new_path:
            print(f"[Logger] 日志文件路径已更改为: {new_path}")
        else:
            print("[Logger] 已禁用文件日志")
    
    def _on_console_output_change(self, enabled):
        print(f"[Logger] 控制台日志输出已{'启用' if enabled else '禁用'}")
    
    def log(self, message):
        print(f"[{self.config.level}] {message}")


class DatabaseConnection:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connected = False
        self._setup_connection()
        
        # 订阅配置变更
        self.config.subscribe_multiple({
            "host": self._on_connection_change,
            "port": self._on_connection_change,
            "username": self._on_connection_change,
            "password": self._on_connection_change,
            "database": self._on_connection_change,
        })
        self.config.subscribe("pool_size", self._on_pool_size_change)
        self.config.subscribe("timeout", self._on_timeout_change)
    
    def _setup_connection(self):
        print(f"[Database] 连接到数据库: {self.config.username}@{self.config.host}:{self.config.port}/{self.config.database}")
        print(f"[Database] 连接池大小: {self.config.pool_size}, 超时: {self.config.timeout}秒")
        self.connected = True
    
    def _on_connection_change(self, _):
        print("[Database] 数据库连接参数已更改，重新连接...")
        self.connected = False
        self._setup_connection()
    
    def _on_pool_size_change(self, new_size):
        print(f"[Database] 连接池大小已更改为: {new_size}")
    
    def _on_timeout_change(self, new_timeout):
        print(f"[Database] 连接超时已更改为: {new_timeout}秒")
    
    def execute_query(self, query):
        if not self.connected:
            print("[Database] 数据库未连接")
            return None
        print(f"[Database] 执行查询: {query}")
        return {"result": "模拟查询结果"}


class Application:
    def __init__(self):
        # 初始化应用配置
        self.config = AppConfig(
            app_name="生产环境应用",
            debug=False,
            log=LogConfig(
                level="WARNING",
                file_path="/var/log/app.log"
            ),
            database=DatabaseConfig(
                host="db.example.com",
                database="production_db",
                password="secure_password"
            ),
            allowed_ips=["192.168.1.1", "10.0.0.1"],
            max_connections=200
        )
        
        # 初始化组件
        self.logger = Logger(self.config.log)
        self.db = DatabaseConnection(self.config.database)
        
        # 订阅应用级配置变更
        self.config.subscribe("debug", self._on_debug_change)
        self.config.subscribe("allowed_ips", self._on_allowed_ips_change)
        self.config.subscribe("max_connections", self._on_max_connections_change)
    
    def _on_debug_change(self, enabled):
        self.logger.log(f"调试模式已{'启用' if enabled else '禁用'}")
        if enabled:
            # 在调试模式下自动调整日志级别
            self.config.log.level = "DEBUG"
    
    def _on_allowed_ips_change(self, ips):
        self.logger.log(f"已更新允许的IP列表: {', '.join(ips)}")
    
    def _on_max_connections_change(self, max_conn):
        self.logger.log(f"最大连接数已更改为: {max_conn}")
    
    def run(self):
        self.logger.log(f"应用 '{self.config.app_name}' 已启动")
        self.db.execute_query("SELECT version()")


# 模拟配置更新线程
class ConfigUpdater(Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.daemon = True
    
    def run(self):
        # 等待应用启动
        time.sleep(1)
        
        # 模拟配置更新
        print("\n[配置更新] 模拟运行时配置更改...")
        
        # 更新日志配置
        self.app.config.log.level = "INFO"
        time.sleep(0.5)
        
        # 更新数据库配置
        self.app.config.database.pool_size = 10
        time.sleep(0.5)
        
        # 启用调试模式（这会级联更改日志级别）
        self.app.config.debug = True
        time.sleep(0.5)
        
        # 更新允许的IP
        self.app.config.allowed_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
        time.sleep(0.5)
        
        # 更改数据库连接参数（触发重连）
        self.app.config.database.host = "replica.example.com"


def main():
    # 创建并运行应用
    app = Application()
    
    # 启动配置更新线程
    updater = ConfigUpdater(app)
    updater.start()
    
    # 运行应用
    app.run()
    
    # 等待配置更新完成
    time.sleep(3)
    print("\n[应用] 演示完成")


if __name__ == "__main__":
    main()