from pyconfigevents import PyConfigBaseModel, RootModel, ChildModel


# 初始化测试环境
class CallbackCls:
    """该类用于测试模型的订阅功能.

    该类的实例将作为回调函数,用于测试模型的订阅功能.

    """

    def __init__(self):
        self.no_nested = False  # 非嵌套模型的回调
        self.nested = False  # 嵌套模型的回调
        self.nested2 = False  # 多层嵌套模型的回调

    def on_no_nested(self, value: int) -> None:
        self.no_nested = True

    def on_nested(self, value: int) -> None:
        self.nested = True

    def on_nested2(self, value: int) -> None:
        self.nested2 = True


class NoNestedModel(PyConfigBaseModel):
    value: int
    value2: int


class NestedModel(RootModel):
    class Theme(ChildModel):
        class Font(ChildModel):
            size: int

        color: str
        font: Font

    version: str
    theme: Theme


no_nested_model = NoNestedModel(value=0, value2=0)
nested_model = NestedModel(
    **{"version": "0.0.0", "theme": {"color": "red", "font": {"size": 0}}}
)
callback_cls = CallbackCls()
callbacked = False


def on_value_changed(value: int) -> None:
    global callbacked
    callbacked = True


def init_env() -> None:
    """在每个测试开始前调用该函数,将环境还原到初始."""
    global callbacked, callback_cls, no_nested_model, nested_model
    callbacked = False
    callback_cls = CallbackCls()
    no_nested_model = NoNestedModel(value=0, value2=0)
    nested_model = NestedModel(
        **{"version": "0.0.0", "theme": {"color": "red", "font": {"size": 0}}}
    )


def test_subscribe():
    """该测试确保函数回调以及类实例方法被正确调用."""
    init_env()

    no_nested_model.subscribe("value", on_value_changed)
    no_nested_model.subscribe("value", callback_cls.on_no_nested)
    
    no_nested_model.value = 100

    assert callbacked
    assert callback_cls.no_nested


def test_unsubscribe():
    """该测试确保取消订阅后,回调函数不再被调用."""
    init_env()
    no_nested_model.subscribe("value", on_value_changed)
    no_nested_model.subscribe("value", callback_cls.on_no_nested)
    
    no_nested_model.unsubscribe("value", on_value_changed)
    no_nested_model.unsubscribe("value", callback_cls.on_no_nested)
    
    no_nested_model.value = 100

    assert not callbacked
    assert not callback_cls.no_nested


def test_multiple_subscribe():
    init_env()

    no_nested_model.subscribe_multiple(
        {"value": on_value_changed, "value2": callback_cls.on_no_nested}
    )
    
    no_nested_model.value = 100
    no_nested_model.value2 = 100

    assert callbacked
    assert callback_cls.no_nested


def test_multiple_unsubscribe():
    init_env()
    no_nested_model.subscribe_multiple(
        {"value": on_value_changed, "value2": callback_cls.on_no_nested}
    )
    no_nested_model.unsubscribe_multiple(
        {"value": on_value_changed, "value2": callback_cls.on_no_nested}
    )
    
    no_nested_model.value = 100
    no_nested_model.value2 = 100

    assert not callbacked
    assert not callback_cls.no_nested


def test_subscribe_nested_model():
    """该测试确保嵌套模型的字段变化能够触发正确的回调函数."""
    init_env()
    nested_model.subscribe("version", callback_cls.on_no_nested)
    nested_model.theme.subscribe("color", callback_cls.on_nested)
    nested_model.theme.font.subscribe("size", callback_cls.on_nested2)

    nested_model.version = "0.1.0"
    nested_model.theme.color = "green"
    nested_model.theme.font.size = 66

    assert callback_cls.no_nested
    assert callback_cls.nested
    assert callback_cls.nested2


def test_unsubscribe_nested_model():
    """该测试确保取消嵌套模型的字段订阅后,回调函数不再被调用."""
    init_env()
    nested_model.subscribe("version", callback_cls.on_no_nested)
    nested_model.theme.subscribe("color", callback_cls.on_nested)
    nested_model.theme.font.subscribe("size", callback_cls.on_nested2)

    nested_model.unsubscribe("version", callback_cls.on_no_nested)
    nested_model.theme.unsubscribe("color", callback_cls.on_nested)
    nested_model.theme.font.unsubscribe("size", callback_cls.on_nested2)

    nested_model.version = "0.1.0"
    nested_model.theme.color = "green"
    nested_model.theme.font.size = 66
    # 确保回调函数未被调用
    assert not callback_cls.no_nested
    assert not callback_cls.nested
    assert not callback_cls.nested2


def test_subscribe_nested_model_multiple():
    """该测试确保一次性订阅多个嵌套模型的字段回调函数."""
    init_env()
    nested_model.subscribe_multiple({"version": callback_cls.on_no_nested})
    nested_model.theme.subscribe_multiple({"color": callback_cls.on_nested})
    nested_model.theme.font.subscribe_multiple({"size": callback_cls.on_nested2})

    nested_model.version = "0.1.0"
    nested_model.theme.color = "green"
    nested_model.theme.font.size = 66

    assert callback_cls.no_nested
    assert callback_cls.nested
    assert callback_cls.nested2


def test_unsubscribe_nested_model_multiple():
    """该测试确保一次性取消订阅多个嵌套模型的字段回调函数."""
    init_env()
    nested_model.subscribe_multiple({"version": callback_cls.on_no_nested})
    nested_model.theme.subscribe_multiple({"color": callback_cls.on_nested})
    nested_model.theme.font.subscribe_multiple({"size": callback_cls.on_nested2})

    nested_model.unsubscribe_multiple({"version": callback_cls.on_no_nested})
    nested_model.theme.unsubscribe_multiple({"color": callback_cls.on_nested})
    nested_model.theme.font.unsubscribe_multiple({"size": callback_cls.on_nested2})

    nested_model.version = "0.1.0"
    nested_model.theme.color = "green"
    nested_model.theme.font.size = 66

    assert not callback_cls.no_nested
    assert not callback_cls.nested
    assert not callback_cls.nested2
