import os
import json
import tempfile

from pyconfigevents import DataModel, read_config


def test_read_config_to_model():
    """
    测试从配置文件读取并转换为DataModel
    """
    # 定义测试用的模型类
    class TestConfig(DataModel):
        name: str
        version: str
        settings: dict
        features: list
        enabled: bool
    
    # 创建临时JSON配置文件
    json_data = {
        "name": "测试应用",
        "version": "1.0.0",
        "settings": {"theme": "dark", "language": "zh-CN"},
        "features": ["feature1", "feature2", "feature3"],
        "enabled": True
    }
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        temp_json.write(json.dumps(json_data).encode('utf-8'))
        json_path = temp_json.name
    
    try:
        # 读取JSON配置并转换为模型
        json_config_dict = read_config(json_path)
        json_model = TestConfig(**json_config_dict)
        
        # 验证JSON转换后的模型字段
        assert json_model.name == "测试应用"
        assert json_model.version == "1.0.0"
        assert json_model.settings == {"theme": "dark", "language": "zh-CN"}
        assert json_model.features == ["feature1", "feature2", "feature3"]
        assert json_model.enabled is True
    finally:
        # 清理临时文件
        os.unlink(json_path)
    
    # 创建临时TOML配置文件
    toml_content = '''
    name = "测试应用"
    version = "1.0.0"
    enabled = true
    features = ["feature1", "feature2", "feature3"]
    
    [settings]
    theme = "dark"
    language = "zh-CN"
    '''
    
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as temp_toml:
        temp_toml.write(toml_content.encode('utf-8'))
        toml_path = temp_toml.name
    
    try:
        # 读取TOML配置并转换为模型
        toml_config_dict = read_config(toml_path)
        toml_model = TestConfig(**toml_config_dict)
        
        # 验证TOML转换后的模型字段
        assert toml_model.name == "测试应用"
        assert toml_model.version == "1.0.0"
        assert toml_model.settings == {"theme": "dark", "language": "zh-CN"}
        assert toml_model.features == ["feature1", "feature2", "feature3"]
        assert toml_model.enabled is True
    finally:
        # 清理临时文件
        os.unlink(toml_path)


def test_read_config_to_nested_model():
    """
    测试从配置文件读取并转换为嵌套的DataModel
    """
    # 定义嵌套的模型类
    class Address(DataModel):
        city: str
        street: str
        postal_code: str = "000000"
    
    class User(DataModel):
        name: str
        age: int
        address: Address
    
    # 创建临时JSON配置文件
    json_data = {
        "name": "张三",
        "age": 30,
        "address": {
            "city": "北京",
            "street": "长安街",
            "postal_code": "100000"
        }
    }
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        temp_json.write(json.dumps(json_data).encode('utf-8'))
        json_path = temp_json.name
    
    try:
        # 读取JSON配置
        json_config_dict = read_config(json_path)
        
        # 手动处理嵌套模型
        address_data = json_config_dict.pop("address")
        address = Address(**address_data)
        user = User(**json_config_dict, address=address)
        
        # 验证嵌套模型字段
        assert user.name == "张三"
        assert user.age == 30
        assert user.address.city == "北京"
        assert user.address.street == "长安街"
        assert user.address.postal_code == "100000"
    finally:
        # 清理临时文件
        os.unlink(json_path)


def test_read_config_with_default_values():
    """
    测试读取配置文件时使用默认值
    """
    # 定义带默认值的模型类
    class ServerConfig(DataModel):
        host: str = "localhost"
        port: int = 8080
        debug: bool = False
        max_connections: int = 100
    
    # 创建只包含部分字段的JSON配置
    json_data = {
        "host": "127.0.0.1",
        "debug": True
    }
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        temp_json.write(json.dumps(json_data).encode('utf-8'))
        json_path = temp_json.name
    
    try:
        # 读取配置并转换为模型
        config_dict = read_config(json_path)
        server_config = ServerConfig(**config_dict)
        
        # 验证字段值，包括默认值
        assert server_config.host == "127.0.0.1"  # 从配置文件读取
        assert server_config.port == 8080  # 使用默认值
        assert server_config.debug is True  # 从配置文件读取
        assert server_config.max_connections == 100  # 使用默认值
    finally:
        # 清理临时文件
        os.unlink(json_path)


def test_read_config_with_inheritance():
    """
    测试读取配置文件并转换为继承关系的模型
    """
    # 定义继承关系的模型类
    class BaseConfig(DataModel):
        version: str = "1.0.0"
        app_name: str
    
    class DatabaseConfig(BaseConfig):
        db_host: str = "localhost"
        db_port: int = 3306
        db_name: str
    
    # 创建配置文件
    json_data = {
        "app_name": "测试应用",
        "version": "2.0.0",
        "db_name": "test_db",
        "db_host": "db.example.com"
    }
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        temp_json.write(json.dumps(json_data).encode('utf-8'))
        json_path = temp_json.name
    
    try:
        # 读取配置并转换为模型
        config_dict = read_config(json_path)
        db_config = DatabaseConfig(**config_dict)
        
        # 验证字段值
        assert db_config.app_name == "测试应用"
        assert db_config.version == "2.0.0"  # 覆盖默认值
        assert db_config.db_name == "test_db"
        assert db_config.db_host == "db.example.com"  # 覆盖默认值
        assert db_config.db_port == 3306  # 使用默认值
    finally:
        # 清理临时文件
        os.unlink(json_path)
