from collections import defaultdict
from typing import Any, Callable, Dict, override, Set, Union, Self
from pathlib import Path

from pydantic import BaseModel

from .utils.read_file import read_config
from .utils.save_file import save_to_file


class DataModel(BaseModel):
    __subscribers: Dict[str, Set[Callable]] = defaultdict(set)  # field: callback

    def subscribe(self, field: str, callback: Callable) -> None:
        """订阅字段变化的回调函数。

        Args:
            field: 要订阅的字段名称。
            callback: 当字段值变化时调用的回调函数。

        Raises:
            ValueError: 如果字段在模型中不存在。
        """
        if field not in self.__class__.model_fields:
            raise ValueError(
                f"Field {field} does not exist in {self.__class__.__name__}"
            )
        self.__subscribers[field].add(callback)

    def unsubscribe(self, field: str, callback: Callable) -> None:
        """取消订阅字段变化的回调函数。

        Args:
            field: 要取消订阅的字段名称。
            callback: 要移除的回调函数。
        """
        if field in self.__subscribers:
            self.__subscribers[field].remove(callback)

    def unsubscribe_multiple(self, field_callbacks: Dict[str, Callable]) -> None:
        """一次性取消订阅多个字段的回调函数。

        Args:
            field_callbacks: 字段名称到回调函数的映射字典。
        """
        for field, callback in field_callbacks.items():
            self.unsubscribe(field, callback)

    def subscribe_multiple(self, field_callbacks: Dict[str, Callable]) -> None:
        """一次性订阅多个字段的回调函数。

        Args:
            field_callbacks: 字段名称到回调函数的映射字典。
        """
        for field, callback in field_callbacks.items():
            self.subscribe(field, callback)

    @property
    def subscribers(self) -> Dict[str, Set[Callable]]:
        return self.__subscribers

    @override
    def __setattr__(self, name: str, value: Any, /) -> None:
        """
        不允许修改不存在的字段，
        不允许修改字段类型，
        并在修改字段值时触发回调函数。

        Args:
            name (str): 字段名称
            value (Any): 修改后的值

        Raises:
            TypeError: 新字段类型与旧字段类型不一致
            AttributeError: 字段不存在
        """
        if name in self.__class__.model_fields:
            old_value = getattr(self, name)
            if type(value) is not type(old_value):
                raise TypeError(
                    f"Field <{name}> type {type(value)} is not compatible with {type(old_value)}"
                )
            super().__setattr__(name, value)
            if old_value == value:
                return
            for callback in self.__subscribers[name]:
                callback(value)
        else:
            raise AttributeError(
                f"Field <{name}> does not exist in {self.__class__.model_fields}"
            )


class RootModel(DataModel):
    py_cfg_events_file_path: Path
    py_cfg_events_auto_save: bool

    @classmethod
    def from_file(cls, file_path: Path, auto_save: bool = False) -> Self:
        """从配置文件创建模型实例

        Args:
            file_path: 配置文件路径

        Returns:
            DataModel实例
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        config_data = read_config(file_path)
        config_data["py_cfg_events_file_path"] = file_path
        config_data["py_cfg_events_auto_save"] = auto_save
        instance = cls(**config_data)
        return instance

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典

        Returns:
            Dict[str, Any]: 模型的字典表示
        """
        res = self.model_dump()
        res.pop("py_cfg_events_file_path")
        res.pop("py_cfg_events_auto_save")
        return res

    def save_to_file(self, file_path: Union[str, Path] = None) -> None:
        """将模型保存到文件

        Args:
            file_path: 保存的文件路径，如果为None则使用模型的file_path

        Raises:
            ValueError: 如果file_path为None且模型的file_path也为None
            ValueError: 如果文件格式不支持
        """
        if file_path is None:
            if self.py_cfg_events_file_path is None:
                raise ValueError("No file path specified and model has no file path")
            file_path = self.py_cfg_events_file_path

        data = self.to_dict()
        save_to_file(data, file_path)

    # 自动保存暂时找不到合适的实现方法
    # @override
    # def __setattr__(self, name: str, value: Any, /) -> None:
    #     super().__setattr__(name, value)
    #     if self.py_cfg_events_auto_save:
    #         self.save_to_file()
