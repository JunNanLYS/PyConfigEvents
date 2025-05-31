#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
嵌套模型和类型验证示例

这个示例展示了如何使用PyConfigEvents库创建嵌套模型结构，
以及如何利用Pydantic的类型验证功能确保配置数据的正确性。
"""

from typing import List, Optional
from datetime import datetime

from pydantic import ValidationError

from pyconfigevents import RootModel, ChildModel


# 定义嵌套模型
class Address(ChildModel):
    street: str
    city: str
    postal_code: str
    country: str = "中国"


class Contact(ChildModel):
    email: str
    phone: Optional[str] = None
    address: Address


class Role(ChildModel):
    name: str
    permissions: List[str]
    level: int


class User(RootModel):
    id: int
    username: str
    full_name: str
    active: bool = True
    contact: Contact
    roles: List[Role] = []
    last_login: Optional[datetime] = None


def print_user_info(user: User):
    """打印用户信息"""
    print(f"用户ID: {user.id}")
    print(f"用户名: {user.username}")
    print(f"姓名: {user.full_name}")
    print(f"状态: {'活跃' if user.active else '禁用'}")
    print(f"邮箱: {user.contact.email}")
    
    if user.contact.phone:
        print(f"电话: {user.contact.phone}")
    
    addr = user.contact.address
    print(f"地址: {addr.country} {addr.city} {addr.street} {addr.postal_code}")
    
    if user.roles:
        print("角色:")
        for role in user.roles:
            print(f"  - {role.name} (级别: {role.level})")
            print(f"    权限: {', '.join(role.permissions)}")
    
    if user.last_login:
        print(f"最后登录时间: {user.last_login}")


def main():
    # 创建嵌套模型实例
    user = User(
        id=1001,
        username="zhangsan",
        full_name="张三",
        contact=Contact(
            email="zhangsan@example.com",
            phone="13800138000",
            address=Address(
                street="中关村大街1号",
                city="北京",
                postal_code="100080"
            )
        ),
        roles=[
            Role(
                name="管理员",
                permissions=["read", "write", "delete", "admin"],
                level=9
            ),
            Role(
                name="编辑",
                permissions=["read", "write"],
                level=5
            )
        ],
        last_login=datetime.now()
    )
    
    # 打印用户信息
    print("初始用户信息:")
    print_user_info(user)
    
    # 定义回调函数
    def on_address_change(new_address):
        print(f"\n地址已更新: {new_address.country} {new_address.city} {new_address.street} {new_address.postal_code}")
    
    def on_role_change(new_roles):
        print(f"\n角色已更新: {', '.join(role.name for role in new_roles)}")
    
    # 订阅嵌套模型的变化
    user.contact.address.subscribe("city", lambda city: print(f"\n城市已更改为: {city}"))
    user.subscribe("contact", lambda contact: print(f"\n联系信息已更新: {contact.email}"))
    user.subscribe("roles", on_role_change)
    
    # 修改嵌套模型的字段
    print("\n更新用户信息:")
    user.contact.address.city = "上海"
    
    # 替换整个嵌套模型
    new_address = Address(
        street="南京路1号",
        city="上海",
        postal_code="200001"
    )
    user.contact.address = new_address
    
    # 添加新角色
    user.roles.append(
        Role(
            name="审核员",
            permissions=["read", "approve"],
            level=6
        )
    )
    
    # 更新整个角色列表（触发事件）
    user.roles = [
        Role(
            name="超级管理员",
            permissions=["read", "write", "delete", "admin", "system"],
            level=10
        )
    ]
    
    # 打印更新后的用户信息
    print("\n更新后的用户信息:")
    print_user_info(user)
    
    # 演示类型验证
    try:
        print("\n尝试设置无效的邮箱地址:")
        user.contact.email = "invalid-email"  # 这会引发Pydantic的验证错误
    except ValueError as e:
        print(f"验证错误: {e}")
    
    try:
        print("\n尝试设置错误类型的字段:")
        user.active = "yes"
    except ValidationError as e:
        print(f"类型错误: {e}")


if __name__ == "__main__":
    main()