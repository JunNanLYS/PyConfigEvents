#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基本模型示例

这个示例展示了如何创建和使用PyConfigBaseModel类，包括字段订阅和事件触发机制。
"""

from pyconfigevents import PyConfigBaseModel


# 定义一个继承自PyConfigBaseModel的配置类
class UserConfig(PyConfigBaseModel):
    username: str
    age: int
    is_admin: bool = False
    preferences: dict = {}


def main():
    # 创建配置实例
    config = UserConfig(
        username="张三",
        age=30,
        preferences={"theme": "dark", "language": "zh-CN"}
    )
    
    # 定义回调函数
    def on_username_change(new_value):
        print(f"用户名已更改为: {new_value}")
    
    def on_age_change(new_value):
        print(f"年龄已更改为: {new_value}")
    
    def on_admin_status_change(new_value):
        if new_value:
            print("用户已被提升为管理员")
        else:
            print("用户已被降级为普通用户")
    
    # 订阅字段变化
    config.subscribe("username", on_username_change)
    config.subscribe("age", on_age_change)
    config.subscribe("is_admin", on_admin_status_change)
    
    # 修改字段值，触发回调
    print("\n修改字段值:")
    config.username = "李四"
    config.age = 31
    config.is_admin = True
    
    # 使用subscribe_multiple订阅多个字段
    print("\n使用字典批量订阅字段:")
    
    def on_any_change(new_value):
        print(f"某个字段已更改为: {new_value}")
    
    config.subscribe_multiple({
        "username": on_any_change,
        "age": on_any_change,
        "is_admin": on_any_change
    })
    
    # 再次修改字段值，触发多个回调
    config.username = "王五"
    
    # 取消订阅
    print("\n取消订阅:")
    config.unsubscribe("username", on_username_change)
    config.username = "赵六"  # 只会触发on_any_change，不会触发on_username_change
    
    # 批量取消订阅
    print("\n批量取消订阅:")
    config.unsubscribe_multiple({
        "username": on_any_change,
        "age": on_any_change,
        "is_admin": on_any_change
    })
    config.username = "钱七"  # 不会触发任何回调


if __name__ == "__main__":
    main()