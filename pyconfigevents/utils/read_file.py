import json
from typing import Union
from pathlib import Path

import pytomlpp as toml
import yaml


def read_config(file_path: Union[str, Path]) -> dict:
    """Currently supports toml and json format configuration files

    Args:
        file_path (_type_): config file path
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file {file_path} not found")
    if file_path.suffix == ".toml":
        return _read_toml(file_path)
    elif file_path.suffix == ".json":
        return _read_json(file_path)
    elif file_path.suffix == ".yaml":
        return _read_yaml(file_path)
    else:
        raise ValueError(f"Config file {file_path} is not a toml or json file")


def _read_toml(file_path: Path) -> dict:
    with open(file_path, "r") as f:
        return toml.load(f)


def _read_json(file_path: Path) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def _read_yaml(file_path: Path) -> dict:
    with open(file_path, "r") as f:
        return yaml.load(f, yaml.Loader)
