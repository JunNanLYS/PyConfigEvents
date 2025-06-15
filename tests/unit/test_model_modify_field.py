from pathlib import Path
from pyconfigevents import RootModel, ChildModel


class ConfigModel(RootModel):
    class Theme(ChildModel):
        class Font(ChildModel):
            size: int

        color: str
        font: Font

    version: str
    enable: bool
    theme: Theme


content = {"version": "0.0.0", "enable": False, "theme": {"color": "red", "font": {"size": 0}}}
model = ConfigModel(**content)


def init_env() -> None:
    global model
    model = ConfigModel(**content)


def test_model_modify_field(tmp_path: Path) -> None:
    """测试模型单个字段修改"""
    init_env()
    # 测试字段修改
    model.version = "1.0.0"
    model.theme.color = "blue"
    model.theme.font.size = 12
    # 断言字段值已修改
    assert model.version == "1.0.0"
    assert model.theme.color == "blue"
    assert model.theme.font.size == 12


def test_update_fields(tmp_path: Path) -> None:
    """测试批量更新字段"""
    init_env()
    # 测试批量更新字段
    model.update_fields({"version": "2.0.0", "enable": True, "theme": {"color": "green", "font": {"size": 14}}})
    # 断言字段值已更新
    assert model.version == "2.0.0"
    assert model.enable
    assert model.theme.color == "green"
    assert model.theme.font.size == 14
    
    
