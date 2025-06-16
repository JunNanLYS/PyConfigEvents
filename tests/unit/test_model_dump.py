from pyconfigevents import RootModel, ChildModel

"""
测试模型的model_dump方法
由于RootModel继承了AutoSaveConfigModel所以且未重写model_dump,所以无需单独测试AutoSaveConfigModel
1. 测试RootModel
2. 测试ChildModel
"""


class ConfigModel(RootModel):
    class Theme(ChildModel):
        class Font(ChildModel):
            size: int

        color: str
        font: Font

    version: str
    theme: Theme


model = None
content = {
    "version": "0.0.0",
    "theme": {"color": "red", "font": {"size": 0}},
}


def init_env() -> None:
    global model
    model = ConfigModel(**content)


def test_root_model_dump() -> None:
    init_env()
    assert model.model_dump() == content


def test_child_model_dump() -> None:
    init_env()
    assert model.theme.model_dump() == content["theme"]
