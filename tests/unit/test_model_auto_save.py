from pathlib import Path
from pyconfigevents import RootModel, ChildModel, ConfigFile

class ConfigModel(RootModel):
    class Theme(ChildModel):
        class Font(ChildModel):
            size: int

        color: str
        font: Font

    version: str
    theme: Theme

model = None


def init_env(tmp_path) -> None:
    global model
    import json
    content = {"version": "0.0.0", "theme": {"color": "red", "font": {"size": 0}}}
    with open(tmp_path / "config.json", "w") as f:
        json.dump(content, f)
    
    model = ConfigModel(**content)
    model.pce_file = ConfigFile(tmp_path / "config.json")
    

def test_auto_save(tmp_path: Path) -> None:
    import json
    init_env(tmp_path)
    model.enable_auto_save(True)
    model.version = "1.0.0"
    model.theme.color = "blue"
    model.theme.font.size = 20
    
    with open(tmp_path / "config.json", "r") as f:
        data = json.load(f)
    assert model.model_dump() == data
    
    
    