from pathlib import Path
from typing import Callable, Dict, Optional, Self
from threading import Lock, Timer

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .utils.read_file import read_config


class ConfigFileEventHandler(FileSystemEventHandler):
    """配置文件事件处理器

    这个类主要处理某一个文件下的配置文件变化事件.
    当配置文件发生变化时,会触发相应的事件处理方法.
    例如:
    - on_modified: 当配置文件被修改时触发.
    - on_deleted: 当配置文件被删除时触发.
    - on_moved: 当配置文件被移动时触发.
    - on_created: 当配置文件被创建时触发.
    """

    # 支持的配置文件元组
    SUPPORTED_CONFIG_FILES = (".json", ".yaml", ".toml")

    def __init__(self, delay: float = 1.0) -> None:
        super().__init__()
        self._delay: float = 1.0
        self._timer: Optional[Timer] = None
        self._lock = Lock()
        self._pending_events = set()  # 存储所有未处理的事件
        self.watch_files: Dict[Path, Callable[[Dict], None]] = dict()

    def add_watch_file(self, file_path: Path, callback: Callable[[Dict], None]) -> None:
        """添加要监控的文件.

        Args:
            file_path (Path): 要监控的文件路径.
            callback (Callable[[Dict], None]): 当文件发生变化时触发的回调函数.
        """
        if file_path in self.watch_files:
            return
        self.watch_files[file_path] = callback

    def remove_watch_file(self, file_path: Path) -> None:
        """移除要监控的文件.

        Args:
            file_path (Path): 要移除监控的文件路径.
        """
        if file_path in self.watch_files:
            del self.watch_files[file_path]

    def _trigger_processing(self) -> None:
        with self._lock:
            paths = self._pending_events.copy()
            self._pending_events.clear()
        
        for src_path in paths:
            cur_path = Path(src_path)
            for path, callback in self.watch_files.items():
                if cur_path.samefile(path):
                    callback(read_config(cur_path))
                    break
    
    def on_modified(self, event: FileModifiedEvent) -> None:
        """当配置文件被修改时触发.

        Args:
            event (FileModifiedEvent): 配置文件修改事件.
        """
        if event.is_directory:
            return
        if not event.src_path.endswith(self.SUPPORTED_CONFIG_FILES):
            return
            
        # 将事件添加到待处理集合
        with self._lock:
            self._pending_events.add(event.src_path)
            
            # 如果已经有定时器在运行，不需要创建新的
            # 这样可以确保在防抖时间内的多次修改只会触发一次回调
            if self._timer is None or not self._timer.is_alive():
                # 创建新的定时器
                self._timer = Timer(
                    self._delay,
                    self._trigger_processing
                )
                self._timer.start()
    
    def __del__(self):
        if self._timer:
            self._timer.cancel()


class ObserverManager:
    """全局Observer管理器,用于管理所有的文件监控

    这个类使用单例模式,确保整个应用中只有一个Observer实例。
    """

    _instance: Self = None
    _is_init: bool = False

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._is_init:
            return
        self._observer = Observer()
        self._observer.start()
        self._dir_to_event_handler: Dict[Path, ConfigFileEventHandler] = (
            dict()
        )  # 记录每个目录的事件处理器
        self._dir_count: Dict[Path, int] = (
            dict()
        )  # 记录每个目录有几个模型在监控,0时移除监控
        self._is_init = True

    def watch(self, file_path: Path, callback: Callable[[Dict], None]) -> None:
        """添加文件监控.

        Args:
            file_path (Path): 要监控的文件路径.
            callback (Callable[[Dict], None]): 当文件发生变化时触发的回调函数.
        """
        dir = file_path.absolute().parent
        # 该目录已有处理器在处理,将该文件添加进该目录的事件处理器
        if dir in self._dir_to_event_handler:
            self._dir_to_event_handler[dir].add_watch_file(file_path, callback)
            self._dir_count[dir] += 1
        else:
            # 该目录没有事件处理器,创建一个新的事件处理器
            event_handler = ConfigFileEventHandler()
            event_handler.add_watch_file(file_path, callback)
            self._dir_to_event_handler[dir] = event_handler
            self._dir_count[dir] = 1
            self._observer.schedule(event_handler, dir, recursive=False)

    def unwatch(self, file_path: Path) -> None:
        """移除文件监控.

        Args:
            file_path (Path): 要移除监控的文件路径.
        """
        dir = file_path.absolute().parent
        # 该目录没有事件处理器,直接返回
        if dir not in self._dir_to_event_handler:
            return
        # 该目录有事件处理器,将该文件从事件处理器中移除
        self._dir_to_event_handler[dir].remove_watch_file(file_path)
        self._dir_count[dir] -= 1
        # 如果该目录没有其他模型监控,则移除事件处理器
        if self._dir_count[dir] == 0:
            self._observer.unschedule(self._dir_to_event_handler[dir])
            del self._dir_to_event_handler[dir]
            del self._dir_count[dir]


OBSERVER_MANAGER = ObserverManager()
