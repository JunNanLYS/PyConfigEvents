import json
from pathlib import Path
import time
from typing import Any, Dict

from pyconfigevents import ConfigFileEventHandler, ObserverManager, ConfigFile


class TestConfigFileEventHandler:
    def test_add_watch_file(self, tmp_path: Path) -> None:
        """测试添加监控文件"""
        path = tmp_path / "config.json"
        path.touch()
        config_file = ConfigFile(path)
        
        event_handler = ConfigFileEventHandler()
        event_handler.add_watched_file(config_file, lambda x: None)
        assert config_file in event_handler.watched_files

    def test_remove_watch_file(self, tmp_path: Path) -> None:
        """测试移除监控文件"""
        path = tmp_path / "config.json"
        path.touch()
        config_file = ConfigFile(path)

        event_handler = ConfigFileEventHandler()
        event_handler.add_watched_file(config_file, lambda x: None)
        
        # 移除监控后修改文件
        event_handler.remove_watched_file(config_file)

        # 验证监控列表为空
        assert len(event_handler.watched_files) == 0 and config_file not in event_handler.watched_files
    
    def test_is_file_watched(self, tmp_path: Path) -> None:
        """测试判断文件是否在监控中"""
        path = tmp_path / "config.json"
        path.touch()
        config_file = ConfigFile(path)
        
        event_handler = ConfigFileEventHandler()
        assert not event_handler.is_file_watched(config_file)
        event_handler.add_watched_file(config_file, lambda x: None)
        assert event_handler.is_file_watched(config_file)

class TestObserverManager:
    def test_init(self) -> None:
        """测试初始化"""
        assert ObserverManager() is ObserverManager()
    
    def test_watch_unwatch(self, tmp_path: Path) -> None:
        path = tmp_path / "config.json"
        path.touch()
        config_file = ConfigFile(path)
        
        called = 0
        def on_modifyed(data: Dict[str, Any]) -> None:
            nonlocal called
            called += 1

        
        ObserverManager().watch(config_file, on_modifyed)
        assert ObserverManager().is_file_observed(config_file)
        with open(path, 'w') as f:
            json.dump({"name": "test"}, f)
        time.sleep(1.5)  # 监控需要响应时间
        assert called == 1
        
        ObserverManager().unwatch(config_file)
        assert not ObserverManager().is_file_observed(config_file)
    