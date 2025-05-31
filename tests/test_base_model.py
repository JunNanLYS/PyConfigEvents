import pytest
from typing import Optional, Union

from pydantic import ValidationError

from pyconfigevents import PyConfigBaseModel


class TestPyConfigBaseModel:
    def test_init_and_access(self):
        """测试模型初始化和字段访问"""
        class TestModel(PyConfigBaseModel):
            name: str
            value: int
            flag: bool = False
        
        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42
        assert model.flag is False
    
    def test_field_modification(self):
        """测试字段修改"""
        class TestModel(PyConfigBaseModel):
            name: str
            value: int
        
        model = TestModel(name="test", value=42)
        model.name = "updated"
        model.value = 100
        assert model.name == "updated"
        assert model.value == 100
    
    def test_type_validation(self):
        """测试类型验证"""
        class TestModel(PyConfigBaseModel):
            name: str
            value: int
        
        model = TestModel(name="test", value=42)
        
        # 类型错误应该引发异常
        with pytest.raises(ValidationError):
            model.name = 123
        
        with pytest.raises(ValidationError):
            model.value = "not_an_int"
        
        # 验证原值未被修改
        assert model.name == "test"
        assert model.value == 42
    
    def test_optional_fields(self):
        """测试可选字段"""
        class TestModel(PyConfigBaseModel):
            name: str
            value: Optional[int] = None
        
        model = TestModel(name="test")
        assert model.value is None
        
        # 可以设置为None
        model.value = 42
        assert model.value == 42
        model.value = None
        assert model.value is None
        
        # 但类型仍然需要匹配
        with pytest.raises(ValidationError):
            model.value = "not_an_int"
    
    def test_union_fields(self):
        """测试联合类型字段"""
        class TestModel(PyConfigBaseModel):
            value: Union[str, int]
        
        model = TestModel(value="test")
        assert model.value == "test"
        
        # 可以设置为联合类型中的任何类型
        model.value = 42
        assert model.value == 42
        model.value = "string_again"
        assert model.value == "string_again"
        
        # 但不能设置为联合类型之外的类型
        with pytest.raises(ValidationError):
            model.value = True
    
    def test_nonexistent_field(self):
        """测试访问不存在的字段"""
        class TestModel(PyConfigBaseModel):
            name: str
        
        model = TestModel(name="test")
        
        # 访问不存在的字段应该引发异常
        with pytest.raises(AttributeError):
            model.nonexistent = "value"
    
    def test_subscribe_callback(self):
        """测试订阅回调函数"""
        class TestModel(PyConfigBaseModel):
            name: str
            value: int
        
        model = TestModel(name="test", value=42)
        
        # 创建回调函数和记录变量
        callback_called = False
        callback_value = None
        
        def on_name_change(new_value):
            nonlocal callback_called, callback_value
            callback_called = True
            callback_value = new_value
        
        # 订阅字段变化
        model.subscribe("name", on_name_change)
        
        # 修改字段应该触发回调
        model.name = "updated"
        assert callback_called is True
        assert callback_value == "updated"
        
        # 重置记录变量
        callback_called = False
        callback_value = None
        
        # 设置相同的值不应该触发回调
        model.name = "updated"
        assert callback_called is False
        assert callback_value is None
    
    def test_unsubscribe_callback(self):
        """测试取消订阅回调函数"""
        class TestModel(PyConfigBaseModel):
            name: str
        
        model = TestModel(name="test")
        
        # 创建回调函数和记录变量
        callback_called = False
        
        def on_name_change(new_value):
            nonlocal callback_called
            callback_called = True
        
        # 订阅字段变化
        model.subscribe("name", on_name_change)
        
        # 取消订阅
        model.unsubscribe("name", on_name_change)
        
        # 修改字段不应该触发回调
        model.name = "updated"
        assert callback_called is False
    
    def test_multiple_subscribers(self):
        """测试多个订阅者"""
        class TestModel(PyConfigBaseModel):
            value: int
        
        model = TestModel(value=42)
        
        # 创建回调函数和记录变量
        callback1_called = False
        callback2_called = False
        
        def on_value_change1(new_value):
            nonlocal callback1_called
            callback1_called = True
        
        def on_value_change2(new_value):
            nonlocal callback2_called
            callback2_called = True
        
        # 订阅字段变化
        model.subscribe("value", on_value_change1)
        model.subscribe("value", on_value_change2)
        
        # 修改字段应该触发所有回调
        model.value = 100
        assert callback1_called is True
        assert callback2_called is True
    
    def test_subscribe_multiple(self):
        """测试一次性订阅多个字段"""
        class TestModel(PyConfigBaseModel):
            name: str
            value: int
        
        model = TestModel(name="test", value=42)
        
        # 创建回调函数和记录变量
        name_callback_called = False
        value_callback_called = False
        
        def on_name_change(new_value):
            nonlocal name_callback_called
            name_callback_called = True
        
        def on_value_change(new_value):
            nonlocal value_callback_called
            value_callback_called = True
        
        # 一次性订阅多个字段
        model.subscribe_multiple({
            "name": on_name_change,
            "value": on_value_change
        })
        
        # 修改字段应该触发相应的回调
        model.name = "updated"
        assert name_callback_called is True
        assert value_callback_called is False
        
        # 重置记录变量
        name_callback_called = False
        
        # 修改另一个字段
        model.value = 100
        assert name_callback_called is False
        assert value_callback_called is True
    
    def test_unsubscribe_multiple(self):
        """测试一次性取消订阅多个字段"""
        class TestModel(PyConfigBaseModel):
            name: str
            value: int
        
        model = TestModel(name="test", value=42)
        
        # 创建回调函数和记录变量
        name_callback_called = False
        value_callback_called = False
        
        def on_name_change(new_value):
            nonlocal name_callback_called
            name_callback_called = True
        
        def on_value_change(new_value):
            nonlocal value_callback_called
            value_callback_called = True
        
        # 订阅字段变化
        model.subscribe("name", on_name_change)
        model.subscribe("value", on_value_change)
        
        # 一次性取消订阅多个字段
        model.unsubscribe_multiple({
            "name": on_name_change,
            "value": on_value_change
        })
        
        # 修改字段不应该触发回调
        model.name = "updated"
        model.value = 100
        assert name_callback_called is False
        assert value_callback_called is False
    
    def test_invalid_field_subscription(self):
        """测试订阅不存在的字段"""
        class TestModel(PyConfigBaseModel):
            name: str
        
        model = TestModel(name="test")
        
        # 订阅不存在的字段应该引发异常
        with pytest.raises(ValueError):
            model.subscribe("nonexistent", lambda x: None)