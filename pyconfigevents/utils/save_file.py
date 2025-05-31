import json
from typing import Any, Dict, Union
from pathlib import Path

import yaml
import pytomlpp as toml


def save_to_file(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """将字典数据保存到文件，根据文件扩展名选择相应的格式

    Args:
        data: 要保存的字典数据
        file_path: 保存的文件路径

    Raises:
        ValueError: 如果文件格式不支持
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if file_path.suffix == ".json":
        _save_json(data, file_path)
    elif file_path.suffix == ".toml":
        _save_toml(data, file_path)
    elif file_path.suffix == ".yaml":
        _save_yaml(data, file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")


def _save_json(data: Dict[str, Any], file_path: Path) -> None:
    """将字典数据保存为JSON格式

    Args:
        data: 要保存的字典数据
        file_path: 保存的文件路径
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def _save_toml(data: Dict[str, Any], file_path: Path) -> None:
    """将字典数据保存为TOML格式

    Args:
        data: 要保存的字典数据
        file_path: 保存的文件路径
    """
    # 需要添加toml写入支持
    with open(file_path, "w") as f:
        toml.dump(data, f)


def _save_yaml(data: Dict[str, Any], file_path: Path) -> None:
    """将字典数据保存为YAML格式

    Args:
        data: 要保存的字典数据
        file_path: 保存的文件路径
    """
    with open(file_path, "w") as f:
        yaml.dump(data, f, indent=4)
