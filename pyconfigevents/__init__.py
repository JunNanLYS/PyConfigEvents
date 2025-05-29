from .model import DataModel, RootModel
from .utils.read_file import read_config
from .utils.save_file import save_to_file


__version__ = "0.1.0"

__all__ = [
    "DataModel",
    "RootModel",
    "read_config",
    "save_to_file",
]