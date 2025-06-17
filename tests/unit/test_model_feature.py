from pathlib import Path
from pyconfigevents import RootModel, ChildModel


class UIConfig(RootModel):
    class NameCard(ChildModel):
        name: str
    
    class TitleLabel(ChildModel):
        class Font(ChildModel):
            size: int
            color: str
        text: str
        font: Font
    
    label: TitleLabel
    card_list: list[NameCard]
    card_dict: dict[str, NameCard]

class AppConfig(RootModel):
    class Client(ChildModel):
        width: int
        height: int

    version: str
    client: Client

class TestModelFeature:
    def test_child_model_set_root_model(self) -> None:
        """测试在根模型初始化后,子模型是否正确设置根模型"""
        model = UIConfig(
            **{
                "label": {
                    "text": "Hello World",
                    "font": {
                        "size": 12,
                        "color": "red"
                    }
                },
                "card_list": [
                    {"name": "card1"},
                    {"name": "card2"},
                ],
                "card_dict": {
                    "card1": {"name": "card1"},
                    "card2": {"name": "card2"},
                }
            }
        )
        assert model.label.pce_root_model is model
        assert model.label.font.pce_root_model is model
        for card in model.card_list:
            assert card.pce_root_model is model
        for card in model.card_dict.values():
            assert card.pce_root_model is model

    def test_from_file(self, tmp_path: Path) -> None:
        """测试根模型从文件中初始化"""
        import json
        content = {
            "version": "0.0.0",
            "client": {
                "width": 800,
                "height": 600
            }
        }
        with open(tmp_path / "app_config.json", 'w') as f:
            json.dump(content, f)
        model = AppConfig.from_file(tmp_path / "app_config.json")
        assert model.model_dump() == content
        
        
