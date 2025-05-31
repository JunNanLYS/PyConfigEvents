import weakref
from collections import defaultdict
from typing import (
    Any,
    Callable,
    Dict,
    get_origin,
    override,
    Set,
    Union,
    Self,
    get_args,
    Optional,
)
from pathlib import Path

from pydantic import BaseModel

from .utils.read_file import read_config
from .utils.save_file import save_to_file


class PyConfigBaseModel(BaseModel):
    """
    所有模型的基类,包含一些通用的方法
    """

    __subscribers: Dict[str, Set[Callable]] = defaultdict(set)  # field: callback

    def _is_valid_type(self, value: Any, field_type: type) -> bool:
        """
        检查值是否符合字段类型定义,处理Optional/Union类型,支持处理弱引用
        """
        if isinstance(value, weakref.ReferenceType):
            value = value()
        # 处理None值
        if value is None:
            # 检查字段是否允许None(Optional[T] 或 Union[T, None])
            origin = get_origin(field_type)
            if origin is Union:
                return type(None) in get_args(field_type)
            return field_type is type(None)  # 直接是None类型
        
        # 基本类型严格检查（按出现频率排序优化）
        strict_types = (str, int, float, bool, list, tuple, dict)
        if field_type in strict_types:
            return type(value) is field_type
        
        # 处理Union类型
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
        # 对Union内的基本类型也严格检查
        if type(value) in strict_types:
            return type(value) in args
        return isinstance(value, args)

    def subscribe(self, field: str, callback: Callable) -> None:
        """订阅字段变化的回调函数.

        Args:
            field: 要订阅的字段名称.
            callback: 当字段值变化时调用的回调函数.

        Raises:
            ValueError: 如果字段在模型中不存在.
        """
        if field not in self.__class__.model_fields:
            raise ValueError(
                f"Field {field} does not exist in {self.__class__.__name__}"
            )
        self.__subscribers[field].add(callback)

    def unsubscribe(self, field: str, callback: Callable) -> None:
        """取消订阅字段变化的回调函数.

        Args:
            field: 要取消订阅的字段名称.
            callback: 要移除的回调函数.
        """
        if field in self.__subscribers:
            self.__subscribers[field].remove(callback)

    def unsubscribe_multiple(self, field_callbacks: Dict[str, Callable]) -> None:
        """一次性取消订阅多个字段的回调函数.

        Args:
            field_callbacks: 字段名称到回调函数的映射字典.
        """
        for field, callback in field_callbacks.items():
            self.unsubscribe(field, callback)

    def subscribe_multiple(self, field_callbacks: Dict[str, Callable]) -> None:
        """一次性订阅多个字段的回调函数.

        Args:
            field_callbacks: 字段名称到回调函数的映射字典.
        """
        for field, callback in field_callbacks.items():
            self.subscribe(field, callback)

    @property
    def subscribers(self) -> Dict[str, Set[Callable]]:
        return self.__subscribers

    @override
    def __setattr__(self, name: str, value: Any, /) -> None:
        """
        不允许修改不存在的字段,
        不允许修改字段类型,
        允许None值(如果字段定义为Optional[T]或Union[T, None]),
        并在修改字段值时触发回调函数.

        Args:
            name (str): 字段名称
            value (Any): 修改后的值

        Raises:
            TypeError: 字段类型不匹配
            AttributeError: 字段不存在
        """
        # 如果值没有变化则不触发回调
        if value is getattr(self, name, None):
            return
        if name in self.__class__.model_fields:
            field_type = self.__class__.model_fields[name].annotation  # 获取字段类型
            # 检查新值是否符合字段类型
            if not self._is_valid_type(value, field_type):
                raise TypeError(
                    f"Field <{name}> type {type(value)} is not compatible with {field_type}"
                )
            super().__setattr__(name, value)
            for callback in self.__subscribers[name]:
                callback(value)
        else:
            raise AttributeError(
                f"Field <{name}> does not exist in {self.__class__.model_fields}"
            )


class AutoSaveConfigModel(PyConfigBaseModel):
    pce_auto_save: bool = False
    pce_file_path: Path

    def _remove_pce_key(self, data: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """移除包含pce_开头的健,若value为dict则递归移除"""
        if isinstance(data, dict):
            return {
                key: self._remove_pce_key(value)
                for key, value in data.items()
                if not key.startswith("pce_")
            }
        elif isinstance(data, list):
            return [self._remove_pce_key(item) for item in data]
        else:
            return data

    def enable_auto_save(self, enable: bool = True) -> None:
        """启用或关闭自动保存功能"""
        self.pce_auto_save = enable

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典,移除pce开头的健

        Returns:
            Dict[str, Any]: 模型的字典表示
        """
        return self._remove_pce_key(self.model_dump())

    def save_to_file(self, file_path: Union[str, Path] = None) -> None:
        """将模型保存到文件

        Args:
            file_path: 保存的文件路径,如果为None则使用模型的file_path

        Raises:
            ValueError: 如果file_path为None且模型的file_path也为None
            ValueError: 如果文件格式不支持
        """
        if file_path is None:
            if self.pce_file_path is None:
                raise ValueError("No file path specified and model has no file path")
            file_path = self.pce_file_path

        data = self.to_dict()
        save_to_file(data, file_path)


class ChildModel(PyConfigBaseModel):
    """
    子模型,放置在RootModel下
    """

    pce_root_model: Optional[AutoSaveConfigModel] = None

    def setup_root_model(self, root_model: AutoSaveConfigModel) -> None:
        self.pce_root_model = root_model
        for _, value in self.__dict__.items():
            if isinstance(value, ChildModel):
                value.setup_root_model(root_model)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ChildModel):
                        item.setup_root_model(root_model)
            elif isinstance(value, dict):
                for _, item in value.items():
                    if isinstance(item, ChildModel):
                        item.setup_root_model(root_model)

    @override
    def __setattr__(self, name: str, value: Any, /) -> None:
        super().__setattr__(name, value)
        if self.pce_root_model is not None and self.pce_root_model.pce_auto_save:
            self.pce_root_model.save_to_file()


class RootModel(AutoSaveConfigModel):
    """
    根模型,可以放置子模型
    支持嵌套模型
    """

    def __init__(self, **data) -> None:
        super().__init__(**data)
        for _, value in self.__dict__.items():
            if isinstance(value, ChildModel):
                value.setup_root_model(self)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ChildModel):
                        item.setup_root_model(self)
            elif isinstance(value, dict):
                for _, item in value.items():
                    if isinstance(item, ChildModel):
                        item.setup_root_model(self)

    @classmethod
    def from_file(cls, file_path: Path, auto_save: bool = False) -> Self:
        """从配置文件创建模型实例

        Args:
            file_path: 配置文件路径
            auto_save: 是否自动保存

        Returns:
            Self
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
        config_data = read_config(file_path)
        config_data["pce_file_path"] = file_path
        config_data["pce_auto_save"] = auto_save
        instance = cls(**config_data)
        return instance
