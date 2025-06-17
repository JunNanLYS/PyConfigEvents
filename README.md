# PyConfigEvents

## Language

- [Chinese](README_CN.md)

PyConfigEvents is a configuration management library based on Pydantic, providing an event-driven configuration change notification mechanism. It allows you to create type-safe configuration models and automatically triggers callback functions when configuration values change. Additionally, it supports real-time monitoring of configuration file changes and automatically updates the model.

## Features

- **Type Safety**: Based on Pydantic's type validation system, ensuring correct configuration data types
- **Event-Driven**: Supports subscription and notification mechanisms for field changes
- **Batch Operations**: Supports batch subscription and unsubscription of field change events
- **Multi-Format Support**: Supports reading and writing configuration files in JSON, TOML, and YAML formats
- **Nested Models**: Supports complex nested configuration structures
- **Auto-Save**: Optional configuration auto-save functionality

## Installation

```bash
pip install PyConfigEvents
```

## Quick Start

### Basic Usage

```python
from pyconfigevents import PyConfigBaseModel

# Define configuration model
class AppConfig(PyConfigBaseModel):
    app_name: str
    debug: bool = False
    port: int = 8000

# Create configuration instance
config = AppConfig(app_name="My Application")

# Subscribe to field changes
def on_debug_change(new_value):
    print(f"Debug mode has been {'enabled' if new_value else 'disabled'}")

config.subscribe("debug", on_debug_change)

# Modify field value, trigger callback
config.debug = True  # Output: Debug mode has been enabled
```

### Loading from Configuration File

```python
from pyconfigevents import RootModel, read_config

class ServerConfig(RootModel):
    host: str = "localhost"
    port: int = 8000

# Read configuration from JSON file
config_dict = read_config("config.json")
server_config = ServerConfig(**config_dict)

# Save configuration to file
server_config.save_to_file("config.json")
```

## Example List

### 1. Basic Model Example (basic_model.py)

Demonstrates how to create and use the PyConfigBaseModel class, including:

- Defining a configuration class that inherits from PyConfigBaseModel
- Subscribing to field change events
- Using callback functions to respond to field changes
- Batch subscription and unsubscription

How to run:

```bash
python examples/basic_model.py
```

### 2. Configuration File to Model Example (config_to_model.py)

Demonstrates how to read data from configuration files and convert it to RootModel objects, including:

- Support for JSON, TOML, and YAML format configuration files
- Definition and use of nested configuration models
- Subscription to configuration change events

How to run:

```bash
python examples/config_to_model.py
```

### 3. Nested Models Example (nested_models.py)

Demonstrates how to create and use nested configuration model structures, including:

- Complex nested model definitions
- Type validation and type safety
- Event subscription for nested models

How to run:

```bash
python examples/nested_models.py
```

### 4. Application Scenario Example (application_example.py)

Demonstrates how to use PyConfigEvents in actual applications, including:

- Real-time configuration updates
- Multi-component configuration management
- Event notification mechanism

How to run:

```bash
python examples/application_example.py
```

## Core Functionality Description

### Base Model (PyConfigBaseModel)

PyConfigBaseModel is a Pydantic-based model class that provides a field change event subscription mechanism. When a model's field value changes, it automatically triggers subscribed callback functions.

```python
# Subscribe to a single field
model.subscribe("field_name", callback_function)

# Batch subscribe to multiple fields
model.subscribe_multiple({
    "field1": callback1,
    "field2": callback2
})

# Unsubscribe
model.unsubscribe("field_name", callback_function)

# Batch unsubscribe
model.unsubscribe_multiple({
    "field1": callback1,
    "field2": callback2
})
```

### Configuration File Reading and Writing

The `read_config` function supports reading data from different format configuration files, currently supporting JSON, TOML, and YAML formats. The read data can be directly used to initialize PyConfigBaseModel, RootModel, or ChildModel objects.

```python
from pyconfigevents import read_config

# Read configuration file
config_data = read_config("config.json")

# Save configuration to file
from pyconfigevents.utils.save_file import save_to_file
save_to_file(data_dict, "config.json")
```

### Root Model (RootModel) and Child Model (ChildModel)

RootModel inherits from AutoSaveConfigModel and adds file loading and saving capabilities. It can automatically load configuration data from a file during initialization and save changes back to the file.

ChildModel is designed for nested models within a RootModel, providing event propagation and automatic saving through the parent model.

```python
from pyconfigevents import RootModel, ChildModel

class ServerConfig(ChildModel):
    host: str = "localhost"
    port: int = 8000

class AppConfig(RootModel):
    app_name: str
    debug: bool = False
    server: ServerConfig = ServerConfig()

# Load from file
config = AppConfig.from_file("config.json")

# Modify and automatically save
config.debug = True  # Automatically saved to config.json
config.server.port = 9000  # Changes propagate and save through the root model
```

## Best Practices

1. **Type Safety**: Leverage Pydantic's type checking to ensure configuration data is of the correct type.
2. **Runtime Type Validation**: PyConfigBaseModel automatically performs type checking when modifying field values to ensure data consistency.
3. **Event-Driven**: Use the field subscription mechanism to implement real-time response to configuration changes.
4. **Modular Configuration**: Use RootModel and ChildModel to organize complex configuration structures.
5. **Configuration File Separation**: Store configuration data in external files, separate from code.
6. **Batch Operations**: Use batch subscription and unsubscription to simplify code.
7. **Auto-Save**: Utilize RootModel's auto-save functionality to ensure configuration changes are immediately saved to file.
