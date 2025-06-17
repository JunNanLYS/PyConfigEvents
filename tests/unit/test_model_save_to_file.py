import json
from pathlib import Path

from pyconfigevents import RootModel, ConfigFile


class ConfigModel(RootModel):
    version: str
    card_color: str

def init_env(tmp_path: Path) -> None:
    """初始化环境"""
    (tmp_path / "config.json").touch()
    (tmp_path / "config2.json").touch()
    


def test_no_file_path(tmp_path: Path) -> None:
    """测试无file_path参数"""
    init_env(tmp_path)
    model = ConfigModel(version="1.0.0", card_color="red")
    model.pce_file = ConfigFile(tmp_path / "config.json")
    model.save_to_file()  # 默认保存到config.json中
    
    with open(tmp_path / "config.json", 'r') as f:
        assert json.load(f) == {"version": "1.0.0", "card_color": "red"}


def test_has_file_path(tmp_path: Path) -> None:
    """测试有file_path参数"""
    init_env(tmp_path)
    model = ConfigModel(version="2.1.0", card_color="blue")
    model.save_to_file(tmp_path / "config2.json")  # 保存到指定文件
    
    with open(tmp_path / "config2.json", 'r') as f:
        assert json.load(f) == {"version": "2.1.0", "card_color": "blue"}
