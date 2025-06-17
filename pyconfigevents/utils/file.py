from pathlib import Path
from typing import override, Any, Callable

from pydantic_core import core_schema


class File:
    def __init__(self, path: Path) -> None:
        if isinstance(path, str):
            path = Path(path)
        if not path.is_file():
            raise ValueError("path is not a file")
        self._filename = path.name
        self._folder = path.absolute().parent
        self._path = path.absolute()

    
    @override
    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, File):
            return False
        return self._filename == other._filename and self._folder.samefile(other._folder)
    
    @override
    def __hash__(self) -> int:
        return hash((self._folder, self._filename))
    
    def __str__(self) -> str:
        return str(self.path)
    
    def __repr__(self) -> str:
        return f"File({self.folder}, {self.filename})"
    
    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def folder(self) -> Path:
        return self._folder
    
    @property
    def path(self) -> Path:
        return self._path
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(Path),
            ]),
            serialization=core_schema.to_string_ser_schema(),
        )
    
    @classmethod
    def validate(cls, value: Any) -> Any:
        if isinstance(value, File):
            return value
        elif isinstance(value, str):
            return cls(Path(value))
        elif isinstance(value, Path):
            return cls(value)
        else:
            raise ValueError("value must be a File, str or Path object")

    
    


class ConfigFile(File):
    """配置文件
    
    这个类主要用于表示配置文件, 目前支持的配置文件格式为 JSON, YAML, TOML.

    """
    SUPPORTED_CONFIG_FILES = (".json", ".yaml", ".toml")

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        if not self._filename.endswith(self.SUPPORTED_CONFIG_FILES):
            raise ValueError("path is not a config file")
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(Path),
                core_schema.is_instance_schema(File),
            ]),
            serialization=core_schema.to_string_ser_schema(),
        )
    
    @classmethod
    def validate(cls, value: Any) -> Any:
        if isinstance(value, ConfigFile):
            return value
        elif isinstance(value, File):
            return cls(value.path)
        elif isinstance(value, str):
            return cls(Path(value))
        elif isinstance(value, Path):
            return cls(value)
        else:
            raise ValueError("value must be a ConfigFile, File, str or Path object")
