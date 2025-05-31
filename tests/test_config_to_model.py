import json
from typing import List, Dict

import pytomlpp as toml
import yaml

from pyconfigevents import RootModel, ChildModel


class TestConfigToModel:
    def test_json_config_to_model(self, tmp_path):
        """测试JSON配置文件转换为模型"""
        class Config(ChildModel):
            setting: str
            enabled: bool
        
        class AppModel(RootModel):
            name: str
            version: str
            config: Config
        
        # 创建JSON配置文件
        config_data = {
            "name": "TestApp",
            "version": "1.0.0",
            "config": {
                "setting": "default",
                "enabled": True
            }
        }
        
        file_path = tmp_path / "config.json"
        with open(file_path, "w") as f:
            json.dump(config_data, f)
        
        # 从文件加载模型
        model = AppModel.from_file(file_path)
        
        # 验证模型字段
        assert model.name == "TestApp"
        assert model.version == "1.0.0"
        assert model.config.setting == "default"
        assert model.config.enabled is True
        assert model.pce_file_path == file_path
    
    def test_toml_config_to_model(self, tmp_path):
        """测试TOML配置文件转换为模型"""
        class ServerConfig(ChildModel):
            host: str
            port: int
        
        class AppModel(RootModel):
            name: str
            server: ServerConfig
        
        # 创建TOML配置内容
        config_content = """
        name = "TestApp"
        
        [server]
        host = "localhost"
        port = 8080
        """
        
        file_path = tmp_path / "config.toml"
        with open(file_path, "w") as f:
            f.write(config_content)
        
        # 从文件加载模型
        model = AppModel.from_file(file_path)
        
        # 验证模型字段
        assert model.name == "TestApp"
        assert model.server.host == "localhost"
        assert model.server.port == 8080
    
    def test_yaml_config_to_model(self, tmp_path):
        """测试YAML配置文件转换为模型"""
        class Feature(ChildModel):
            name: str
            enabled: bool
        
        class AppModel(RootModel):
            name: str
            features: List[Feature]
        
        # 创建YAML配置数据
        config_data = {
            "name": "TestApp",
            "features": [
                {"name": "feature1", "enabled": True},
                {"name": "feature2", "enabled": False}
            ]
        }
        
        file_path = tmp_path / "config.yaml"
        with open(file_path, "w") as f:
            yaml.dump(config_data, f)
        
        # 从文件加载模型
        model = AppModel.from_file(file_path)
        
        # 验证模型字段
        assert model.name == "TestApp"
        assert len(model.features) == 2
        assert model.features[0].name == "feature1"
        assert model.features[0].enabled is True
        assert model.features[1].name == "feature2"
        assert model.features[1].enabled is False
    
    def test_model_to_config(self, tmp_path):
        """测试模型转换为配置文件"""
        class Config(ChildModel):
            setting: str
        
        class AppModel(RootModel):
            name: str
            version: str
            config: Config
        
        # 创建模型实例
        model = AppModel(
            name="TestApp",
            version="1.0.0",
            config=Config(setting="default"),
            pce_file_path=tmp_path / "config.json"
        )
        
        # 保存到文件
        model.save_to_file()
        
        # 读取文件内容
        with open(tmp_path / "config.json", "r") as f:
            saved_data = json.load(f)
        
        # 验证保存的内容
        assert saved_data["name"] == "TestApp"
        assert saved_data["version"] == "1.0.0"
        assert saved_data["config"]["setting"] == "default"
        
        # 验证pce_开头的字段被移除
        assert "pce_file_path" not in saved_data
        assert "pce_auto_save" not in saved_data
    
    def test_model_to_different_formats(self, tmp_path):
        """测试模型保存为不同格式的配置文件"""
        class AppModel(RootModel):
            name: str
            version: str
        
        # 创建模型实例
        model = AppModel(
            name="TestApp",
            version="1.0.0",
            pce_file_path=tmp_path / "config.json"
        )
        
        # 保存为JSON
        json_path = tmp_path / "config.json"
        model.save_to_file(json_path)
        
        # 保存为TOML
        toml_path = tmp_path / "config.toml"
        model.save_to_file(toml_path)
        
        # 保存为YAML
        yaml_path = tmp_path / "config.yaml"
        model.save_to_file(yaml_path)
        
        # 验证所有文件都已创建
        assert json_path.exists()
        assert toml_path.exists()
        assert yaml_path.exists()
        
        # 读取并验证JSON内容
        with open(json_path, "r") as f:
            json_data = json.load(f)
        assert json_data["name"] == "TestApp"
        assert json_data["version"] == "1.0.0"
        
        # 读取并验证TOML内容
        toml_data = toml.load(toml_path)
        assert toml_data["name"] == "TestApp"
        assert toml_data["version"] == "1.0.0"
        
        # 读取并验证YAML内容
        with open(yaml_path, "r") as f:
            yaml_data = yaml.safe_load(f)
        assert yaml_data["name"] == "TestApp"
        assert yaml_data["version"] == "1.0.0"
    
    def test_complex_nested_config(self, tmp_path):
        """测试复杂嵌套配置的转换"""
        class DeepConfig(ChildModel):
            value: int
        
        class NestedConfig(ChildModel):
            name: str
            deep: DeepConfig
        
        class Config(ChildModel):
            setting: str
            nested: NestedConfig
        
        class AppModel(RootModel):
            name: str
            config: Config
            items: List[str]
            mapping: Dict[str, int]
        
        # 创建复杂配置数据
        config_data = {
            "name": "ComplexApp",
            "config": {
                "setting": "complex",
                "nested": {
                    "name": "nested_config",
                    "deep": {
                        "value": 42
                    }
                }
            },
            "items": ["item1", "item2", "item3"],
            "mapping": {
                "key1": 1,
                "key2": 2
            }
        }
        
        file_path = tmp_path / "complex.json"
        with open(file_path, "w") as f:
            json.dump(config_data, f)
        
        # 从文件加载模型
        model = AppModel.from_file(file_path)
        
        # 验证模型字段
        assert model.name == "ComplexApp"
        assert model.config.setting == "complex"
        assert model.config.nested.name == "nested_config"
        assert model.config.nested.deep.value == 42
        assert model.items == ["item1", "item2", "item3"]
        assert model.mapping == {"key1": 1, "key2": 2}
        
        # 修改模型并保存
        model.config.nested.deep.value = 100
        model.items.append("item4")
        model.mapping["key3"] = 3
        model.save_to_file()
        
        # 重新加载并验证
        reloaded = AppModel.from_file(file_path)
        assert reloaded.config.nested.deep.value == 100
        assert "item4" in reloaded.items
        assert reloaded.mapping["key3"] == 3