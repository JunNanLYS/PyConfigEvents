"""
使用场景1
"""
from pathlib import Path

import pytest

from pyconfigevents import RootModel, ChildModel, read_config, save_to_file

class ConfigModel(RootModel):
    class _Theme(ChildModel):
        color: str
        font: str
        size: int
    
    class _Personal(ChildModel):
        language: str
        author: str
        version: str
    
    Theme: _Theme
    Personal: _Personal


def create_config_file(file_path: Path) -> None:
    config_content = {
        "Theme": {
            "color": "red",
            "font": "Arial",
            "size": 12,
        },
        "Personal": {
            "language": "English",
            "author": "John Doe",
            "version": "0.1.0",
        }
    }
    save_to_file(config_content, file_path)

def check_content(model: RootModel, file_path: Path):
    content1 = model.to_dict()
    content2 = read_config(file_path)
    assert content1 is not content2
    assert content1 == content2

def test_scenario_1(tmp_path: Path):
    file_path = tmp_path / "config.json"
    create_config_file(file_path)
    model = ConfigModel.from_file(file_path)  # 配置文件自动加载
    check_content(model, file_path)  # 确保内容一致
    
    # 进行字段修改
    model.Theme.color = "blue"
    model.Personal.author = "Nann"
    assert model.Theme.color == "blue"
    assert model.Personal.author == "Nann"
    
    # 确保类型检查正常运行
    with pytest.raises(TypeError):
        model.Theme.size = "12"
    # 确保在类型不正确时不会修改原字段
    assert model.Theme.size == 12
    
    # 手动保存，确保内容一致
    model.save_to_file()
    check_content(model, file_path)
    
    # 自动保存（暂未实现）
    # model.py_cfg_events_auto_save = True
    model.Theme.color = "green"
    model.Personal.language = "Chinese"
    # check_content(model, file_path)
    
    class InfoCard:
        def __init__(self, model: ConfigModel) -> None:
            self._model = model
            self.author = model.Personal.author
            self.language = model.Personal.language
            self.size = model.Theme.size
            
            # 订阅字段变化事件
            self._model.Personal.subscribe_multiple({
                "author": self.on_author_change,
                "language": self.on_language_change,
            })
            self._model.Theme.subscribe("size", self.on_size_change)
        
        def on_author_change(self, value: str) -> None:
            self.author = value
        
        def on_language_change(self, value: str) -> None:
            self.language = value
        
        def on_size_change(self, value: int) -> None:
            self.size = value
        
        def __del__(self) -> None:
            # 在析构时取消订阅
            self._model.Personal.unsubscribe_multiple({
                "author": self.on_author_change,
                "language": self.on_language_change,
            })
            self._model.Theme.unsubscribe("size", self.on_size_change)
            assert self._model.Personal.subscribers["author"] == set()
            assert self._model.Personal.subscribers["language"] == set()
            assert self._model.Theme.subscribers["size"] == set()
            del self._model
    # 测试订阅字段变化事件
    card = InfoCard(model)
    assert card.author == "Nann"
    assert card.language == "Chinese"
    assert card.size == 12
    model.Theme.size = 14
    assert card.size == 14
    model.Personal.author = "Nannn"
    assert card.author == "Nannn"
    model.Personal.language = "Chinesee"
    assert card.language == "Chinesee"
    
    # 测试取消订阅字段变化事件
    del card
    