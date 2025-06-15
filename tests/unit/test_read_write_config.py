import pytest
import json
from pathlib import Path

import yaml

from pyconfigevents.utils.read_file import read_config
from pyconfigevents.utils.save_file import save_to_file


def test_read_json_config(tmp_path):
    """
    测试读取JSON格式配置文件
    """
    # 创建临时JSON配置文件
    config_data = {
        "project": {
            "name": "test_project",
            "version": "1.0.0",
            "description": "Test project"
        }
    }
    json_file = tmp_path / "config.json"
    with open(json_file, "w") as f:
        json.dump(config_data, f)
    
    # 测试读取JSON文件
    result = read_config(json_file)
    assert result == config_data
    
    # 测试使用字符串路径
    result = read_config(str(json_file))
    assert result == config_data


def test_read_toml_config(tmp_path):
    """
    测试读取TOML格式配置文件
    """
    # 创建临时TOML配置文件
    toml_content = """[project]
    name = "test_project"
    version = "1.0.0"
    description = "Test project"
    """
    toml_file = tmp_path / "config.toml"
    with open(toml_file, "wb") as f:
        f.write(toml_content.encode("utf-8"))
    
    # 测试读取TOML文件
    result = read_config(toml_file)
    assert result["project"]["name"] == "test_project"
    assert result["project"]["version"] == "1.0.0"
    assert result["project"]["description"] == "Test project"


def test_read_yaml_config(tmp_path):
    """
    测试读取YAML格式配置文件
    """
    # 创建临时YAML配置文件
    yaml_content = {
        "project": {
            "name": "test_project",
            "version": "1.0.0",
            "description": "Test project"
        }
    }
    yaml_file = tmp_path / "config.yaml"
    with open(yaml_file, 'w') as f:
        yaml.dump(yaml_content, f)

    # 测试读取YAML文件
    result = read_config(yaml_file)
    assert result["project"]["name"] == "test_project"
    assert result["project"]["version"] == "1.0.0"
    assert result["project"]["description"] == "Test project"
    

def test_file_not_found():
    """
    测试文件不存在的情况
    """
    non_existent_file = Path("non_existent_file.json")
    with pytest.raises(FileNotFoundError):
        read_config(non_existent_file)


def test_unsupported_file_format(tmp_path):
    """
    测试读取不支持的文件格式
    """
    # 创建临时文本文件
    txt_file = tmp_path / "config.txt"
    with open(txt_file, "w") as f:
        f.write("This is a text file")
    
    # 测试读取不支持的文件格式应该抛出ValueError异常
    with pytest.raises(ValueError):
        read_config(txt_file)


def test_save_json_config(tmp_path: Path):
    """
    测试保存JSON格式配置文件
    """
    # 准备测试数据
    config_data = {
        "project": {
            "name": "test_project",
            "version": "1.0.0",
            "description": "Test project"
        }
    }
    json_file = tmp_path / "config.json"
    
    # 保存为JSON文件
    save_to_file(config_data, json_file)
    
    # 验证文件已创建
    assert json_file.exists()
    
    # 读取文件内容并验证
    with open(json_file, "r") as f:
        saved_data = json.load(f)
    assert saved_data == config_data


def test_save_toml_config(tmp_path: Path):
    """
    测试保存TOML格式配置文件
    """
    # 准备测试数据
    config_data = {
        "project": {
            "name": "test_project",
            "version": "1.0.0",
            "description": "Test project"
        }
    }
    toml_file = tmp_path / "config.toml"
    
    # 保存为TOML文件
    save_to_file(config_data, toml_file)
    
    # 验证文件已创建
    assert toml_file.exists()
    
    # 读取文件内容并验证
    result = read_config(toml_file)
    assert result == config_data


def test_save_yaml_config(tmp_path: Path):
    """
    测试保存YAML格式配置文件
    """
    # 准备测试数据
    config_data = {
        "project": {
            "name": "test_project",
            "version": "1.0.0",
            "description": "Test project"
        }
    }
    yaml_file = tmp_path / "config.yaml"
    
    # 保存为YAML文件
    save_to_file(config_data, yaml_file)
    
    # 验证文件已创建
    assert yaml_file.exists()
    
    # 读取文件内容并验证
    result = read_config(yaml_file)
    assert result == config_data


def test_save_unsupported_format(tmp_path):
    """
    测试保存为不支持的文件格式
    """
    # 准备测试数据
    config_data = {"key": "value"}
    txt_file = tmp_path / "config.txt"
    
    # 测试保存为不支持的文件格式应该抛出ValueError异常
    with pytest.raises(ValueError):
        save_to_file(config_data, txt_file)