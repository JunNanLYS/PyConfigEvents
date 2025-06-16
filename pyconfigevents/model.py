from collections import defaultdict
from typing import (
    Any,
    Callable,
    Dict,
    override,
    Set,
    Union,
    Self,
    Optional,
)
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from pyconfigevents.event_handler import ObserverManager

from .utils.read_file import read_config
from .utils.save_file import save_to_file
from .utils.file import ConfigFile


class PyConfigBaseModel(BaseModel):
    """
    所有模型的基类,包含一些通用的方法
    """

    __subscribers: Dict[str, Set[Callable]] = defaultdict(set)  # field: callback
    model_config = ConfigDict(strict=True, validate_assignment=True)

    def subscribe(self, field: str, callback: Callable[[Any], None]) -> None:
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

    def update_fields(self, data: Dict[str, Any]) -> None:
        """批量更新字段的值.

        Args:
            data (Dict[str, Any]): 要更新的字段和值的字典.

        Raises:
            AttributeError: 如果字段在模型中不存在.
        """
        for key, value in data.items():
            # 保证字段存在
            if key not in self.__class__.model_fields:
                raise AttributeError(f"Field {key} does not exist")
            # 如果value是dict,则说明是一个子模型,则递归更新
            if isinstance(value, dict):
                # 获取子模型
                sub_model: "PyConfigBaseModel" = getattr(self, key)
                # 递归更新
                sub_model.update_fields(value)
            else:
                setattr(self, key, value)

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
        if value is getattr(self, name, None) or value == getattr(self, name, None):
            return
        if name in self.__class__.model_fields:
            super().__setattr__(name, value)
            for callback in self.__subscribers[name]:
                callback(value)
        else:
            raise AttributeError(
                f"Field <{name}> does not exist in {self.__class__.model_fields}"
            )


def remove_pce_key(data: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """移除包含pce_开头的健,若value为dict则递归移除"""
    if isinstance(data, dict):
        return {
            key: remove_pce_key(value)
            for key, value in data.items()
            if not key.startswith("pce_")
        }
    elif isinstance(data, list):
        return [remove_pce_key(item) for item in data]
    else:
        return data


class AutoSaveConfigModel(PyConfigBaseModel):
    pce_auto_save: bool = False
    pce_file: Optional[ConfigFile] = None

    def enable_auto_save(self, enable: bool = True) -> None:
        """启用或关闭自动保存功能"""
        self.pce_auto_save = enable

    def save_to_file(self, file_path: Union[str, Path] = None) -> None:
        """将模型保存到文件

        Args:
            file_path: 保存的文件路径,如果为None则使用模型的file_path

        Raises:
            ValueError: 如果file_path为None且模型的file_path也为None
            ValueError: 如果文件格式不支持
        """
        if file_path is None:
            file_path = self.pce_file.path

        data = self.model_dump()
        save_to_file(data, file_path)

    @override
    def model_dump(self, **kwargs) -> dict[str, Any]:
        return remove_pce_key(super().model_dump(**kwargs))

    @override
    def __setattr__(self, name: str, value: Any, /) -> None:
        super().__setattr__(name, value)
        if self.pce_auto_save:
            self.save_to_file()


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

    @override
    def model_dump(self, **kwargs) -> dict[str, Any]:
        return remove_pce_key(super().model_dump(**kwargs))



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
        config_data = read_config(file_path)
        file = ConfigFile(file_path)
        config_data["pce_file"] = file
        config_data["pce_auto_save"] = auto_save
        instance = cls(**config_data)
        return instance


class LiveConfigModel(RootModel):
    """实时配置模型,支持监控配置文件变化并自动更新.

    这个类继承自RootModel,并添加了文件监控功能.
    当配置文件发生变化时,会自动读取新的配置并更新模型.
    使用时候需要注意一个配置文件对应一个LiveConfigModel,不要多个Model对应一个配置文件,
    在ConfigFileEventHandler中会将文件路径与Model绑定,当文件变化时会根据绑定的Model来更新.
    """

    def _on_config_changed(self, data: Dict[str, Any]) -> None:
        """当配置文件变化时调用,更新模型字段.
        这个方法会在配置文件发生变化时被调用,并将新的配置数据传递给它.
        子类可以重写这个方法来实现自定义的配置更新逻辑.
        注意: 这个方法会在更新字段期间关闭自动保存以防循环调用.
        """
        if self.pce_auto_save:
            self.enable_auto_save(False)
            self.update_fields(data)
            self.enable_auto_save(True)
        else:
            self.update_fields(data)

    # 默认开启自动保存
    @classmethod
    @override
    def from_file(cls, file_path: Path, auto_save: bool = True) -> Self:
        instance = super().from_file(file_path, auto_save)
        ObserverManager().watch(instance.pce_file, instance._on_config_changed)
        return instance

    def __del__(self) -> None:
        """调用ObserverManager移除文件监控."""
        ObserverManager().unwatch(self.pce_file)
