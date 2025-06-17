# PyConfigEvents

## 语言

- [English](README_EN.md)

PyConfigEvents 是一个基于 Pydantic 的配置管理库，提供了事件驱动的配置变更通知机制。它允许您创建类型安全的配置模型，并在配置值变化时自动触发回调函数。此外，它还支持实时监控配置文件的变化，并自动更新模型。

## 特性

- **类型安全**：基于 Pydantic 的类型验证系统，确保配置数据类型正确
- **事件驱动**：支持字段变化事件的订阅和通知机制
- **批量操作**：支持批量订阅和取消订阅字段变化事件
- **多格式支持**：支持 JSON、TOML 和 YAML 格式的配置文件读写
- **嵌套模型**：支持复杂的嵌套配置结构
- **自动保存**：可选的配置自动保存功能

## 安装

```bash
pip install PyConfigEvents
```

## 快速开始

### 基本用法

```python
from pyconfigevents import PyConfigBaseModel

# 定义配置模型
class AppConfig(PyConfigBaseModel):
    app_name: str
    debug: bool = False
    port: int = 8000

# 创建配置实例
config = AppConfig(app_name="我的应用")

# 订阅字段变化
def on_debug_change(new_value):
    print(f"调试模式已{'开启' if new_value else '关闭'}")

config.subscribe("debug", on_debug_change)

# 修改字段值，触发回调
config.debug = True  # 输出: 调试模式已开启
```

### 从配置文件加载

```python
from pyconfigevents import RootModel, read_config

class ServerConfig(RootModel):
    host: str = "localhost"
    port: int = 8000

# 从JSON文件读取配置
config_dict = read_config("config.json")
server_config = ServerConfig(**config_dict)

# 保存配置到文件
server_config.save_to_file("config.json")
```

## 示例列表

### 1. 基本模型示例 (basic_model.py)

展示了如何创建和使用 PyConfigBaseModel 类，包括：

- 定义继承自 PyConfigBaseModel 的配置类
- 订阅字段变化事件
- 使用回调函数响应字段变化
- 批量订阅和取消订阅

运行方式：

```bash
python examples/basic_model.py
```

### 2. 配置文件转模型示例 (config_to_model.py)

展示了如何从配置文件读取数据并转换为 RootModel 对象，包括：

- 支持 JSON、TOML 和 YAML 格式配置文件
- 嵌套配置模型的定义和使用
- 配置变更事件的订阅

运行方式：

```bash
python examples/config_to_model.py
```

### 3. 嵌套模型示例 (nested_models.py)

展示了如何创建和使用嵌套的配置模型结构，包括：

- 复杂的嵌套模型定义
- 类型验证和类型安全
- 嵌套模型的事件订阅

运行方式：

```bash
python examples/nested_models.py
```

### 4. 应用场景示例 (application_example.py)

展示了在实际应用中如何使用 PyConfigEvents，包括：

- 实时配置更新
- 多组件配置管理
- 事件通知机制

运行方式：

```bash
python examples/application_example.py
```

## 核心功能说明

### 基础模型 (PyConfigBaseModel)

PyConfigBaseModel 是一个基于 Pydantic 的模型类，它提供了字段变化事件的订阅机制。当模型的字段值发生变化时，会自动触发已订阅的回调函数。

```python
# 订阅单个字段
model.subscribe("field_name", callback_function)

# 批量订阅多个字段
model.subscribe_multiple({
    "field1": callback1,
    "field2": callback2
})

# 取消订阅
model.unsubscribe("field_name", callback_function)

# 批量取消订阅
model.unsubscribe_multiple({
    "field1": callback1,
    "field2": callback2
})
```

### 配置文件读写

`read_config` 函数支持从不同格式的配置文件中读取数据，目前支持 JSON、TOML 和 YAML 格式。读取的数据可以直接用于初始化 PyConfigBaseModel、RootModel 或 ChildModel 对象。

```python
from pyconfigevents import read_config

# 读取配置文件
config_data = read_config("config.json")

# 保存配置到文件
from pyconfigevents.utils.save_file import save_to_file
save_to_file(data_dict, "config.json")
```

### 根模型 (RootModel)

RootModel 继承自 AutoSaveConfigModel，提供了从文件加载和保存到文件的功能。它可以包含 ChildModel 类型的子模型。

```python
from pyconfigevents import RootModel, ChildModel

class ServerConfig(ChildModel):
    host: str = "localhost"
    port: int = 8000

class MyConfig(RootModel):
    app_name: str
    debug: bool = False
    server: ServerConfig = ServerConfig()

# 从文件加载
config = MyConfig.from_file("config.json")

# 保存到文件
config.save_to_file()
```

## 最佳实践

1. **类型安全**：利用 Pydantic 的类型检查功能，确保配置数据的类型正确。
2. **运行时类型验证**：PyConfigBaseModel 在修改字段值时会自动进行类型检查，确保数据一致性。
3. **事件驱动**：使用字段订阅机制，实现配置变更的实时响应。
4. **模块化配置**：使用 RootModel 和 ChildModel 组织复杂的配置结构。
5. **配置文件分离**：将配置数据存储在外部文件中，与代码分离。
6. **批量操作**：使用批量订阅和取消订阅功能，简化代码。
7. **自动保存**：利用 RootModel 的自动保存功能，确保配置变更即时保存到文件。
