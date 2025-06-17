from pathlib import Path
from typing import Callable, Dict, Optional, Set
from threading import Lock, Timer

from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .utils.read_file import read_config
from .utils.file import ConfigFile


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

    def __init__(self, delay: float = 1.0) -> None:
        super().__init__()
        self._delay: float = 1.0
        self._timer: Optional[Timer] = None
        self._lock = Lock()
        self._pending_events: Set[str] = set()  # 存储所有未处理的事件
        self.watched_files: Dict[ConfigFile, Callable[[Dict], None]] = dict()

    def __del__(self):
        if self._timer:
            self._timer.cancel()

    def _trigger_processing(self) -> None:
        with self._lock:
            files = self._pending_events.copy()
            self._pending_events.clear()

        for file in files:
            file = ConfigFile(file)
            if file in self.watched_files:
                callback = self.watched_files[file]
                callback(read_config(file.path))

    def add_watched_file(
        self, file: ConfigFile, callback: Callable[[Dict], None]
    ) -> None:
        """添加要监控的文件.
        无法添加已经在监控中的文件.

        Args:
            file (ConfigFile): 要监控的文件.
            callback (Callable[[Dict], None]): 当文件发生变化时触发的回调函数.
        """
        if file in self.watched_files:
            return
        self.watched_files[file] = callback

    def remove_watched_file(self, file: ConfigFile) -> None:
        """移除要监控的文件.

        Args:
            file (ConfigFile): 要移除监控的文件.
        """
        if file in self.watched_files:
            del self.watched_files[file]

    def is_file_watched(self, file: ConfigFile) -> bool:
        """判断文件是否在监控中.

        Args:
            file (ConfigFile): 要判断的文件.

        Returns:
            bool: 如果文件在监控中,返回True,否则返回False.
        """
        return file in self.watched_files

    def on_modified(self, event: FileModifiedEvent) -> None:
        """当配置文件被修改时触发.

        Args:
            event (FileModifiedEvent): 配置文件修改事件.
        """
        if event.is_directory:
            return
        if not event.src_path.endswith(ConfigFile.SUPPORTED_CONFIG_FILES):
            return

        # 将事件添加到待处理集合
        with self._lock:
            self._pending_events.add(event.src_path)

            # 如果已经有定时器在运行，不需要创建新的
            # 这样可以确保在防抖时间内的多次修改只会触发一次回调
            if self._timer is None or not self._timer.is_alive():
                # 创建新的定时器
                self._timer = Timer(self._delay, self._trigger_processing)
                self._timer.start()


class ObserverManager:
    """全局Observer管理器,用于管理所有的文件监控

    这个类使用单例模式,确保整个应用中只有一个Observer实例。
    """

    _instance: Optional["ObserverManager"] = None
    _is_init: bool = False
    _lock: Lock = Lock()

    def __del__(self) -> None:
        self._observer.stop()

    def __new__(cls) -> "ObserverManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """初始化实例变量"""
        self._observer = Observer()
        self._observer.start()
        self._dir_event_handlers: Dict[Path, ConfigFileEventHandler] = dict()
        self._dir_reference_counts: Dict[Path, int] = dict()
        self._event_handler_to_watch: Dict[ConfigFileEventHandler, ObservedWatch] = dict()
        self._manager_lock = Lock()  # 用于保护内部数据结构的锁

    def watch(self, file: ConfigFile, callback: Callable[[Dict], None]) -> None:
        """添加文件监控"""
        dir_path = file.folder

        with self._manager_lock:
            # 如果目录已有处理器，直接添加文件
            if dir_path in self._dir_event_handlers:
                self._dir_event_handlers[dir_path].add_watched_file(file, callback)
                self._dir_reference_counts[dir_path] += 1
                return

            # 新目录，创建处理器并开始监控
            event_handler = ConfigFileEventHandler()
            event_handler.add_watched_file(file, callback)
            watch = self._observer.schedule(event_handler, dir_path, recursive=False)

            self._dir_event_handlers[dir_path] = event_handler
            self._dir_reference_counts[dir_path] = 1
            self._event_handler_to_watch[event_handler] = watch

    def unwatch(self, file: ConfigFile) -> None:
        """移除文件监控"""
        dir_path = file.folder

        with self._manager_lock:
            if dir_path not in self._dir_event_handlers:
                return

            event_handler = self._dir_event_handlers[dir_path]
            event_handler.remove_watched_file(file)
            self._dir_reference_counts[dir_path] -= 1

            # 如果目录没有其他监控文件，移除整个监控
            if self._dir_reference_counts[dir_path] == 0:
                watch = self._event_handler_to_watch.pop(event_handler)
                self._observer.unschedule(watch)
                del self._dir_event_handlers[dir_path]
                del self._dir_reference_counts[dir_path]

    def is_file_observed(self, file: ConfigFile) -> bool:
        """检查文件是否已被监控"""
        dir_path = file.folder

        with self._manager_lock:
            if dir_path not in self._dir_event_handlers:
                return False
            return self._dir_event_handlers[dir_path].is_file_watched(file)

    def shutdown(self) -> None:
        pass
