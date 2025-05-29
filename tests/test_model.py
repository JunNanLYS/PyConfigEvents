from pyconfigevents import DataModel


def test_change_field():
    """
    测试字段的变化
    """

    class Test1(DataModel):
        version: str

    model1, model2 = Test1(version="1.0.0"), Test1(version="1.0.0")

    assert model1 is not model2

    model1.version = "1.0.1"
    assert model1.version != model2.version

    class Test2(Test1):
        name: str

    model1, model2 = Test2(version="1.0.0", name="test"), Test1(version="1.0.0")

    assert model1 is not model2

    model1.version = "1.0.1"
    assert model1.version != model2.version


def test_single_field_subscription():
    """
    测试单个字段的订阅和取消订阅
    """

    class Config(DataModel):
        name: str
        age: int

    config = Config(name="Alice", age=30)
    callback_count = 0

    def on_name_change(new_value):
        nonlocal callback_count
        callback_count += 1
        assert new_value == "Bob"

    # 订阅name字段
    config.subscribe("name", on_name_change)

    # 修改name字段，应该触发回调
    config.name = "Bob"
    assert callback_count == 1

    # 取消订阅
    config.unsubscribe("name", on_name_change)

    # 再次修改name字段，不应该触发回调
    config.name = "Charlie"
    assert callback_count == 1  # 计数器不应该增加


def test_field_callback():
    """
    测试订阅多个字段的回调函数和实例方法
    """

    class Config(DataModel):
        name: str
        age: int
        height: float
        is_male: bool

    person = Config(name="John", age=25, height=1.75, is_male=True)
    function_count = 0

    def on_field_change(new_value):
        nonlocal function_count
        function_count += 1

    person.subscribe_multiple({
        "name": on_field_change,
        "age": on_field_change,
        "height": on_field_change,
        "is_male": on_field_change
    })

    class Instance(object):
        def __init__(self):
            super().__init__()
            self.count = 0

        def on_field_change(self, new_value):
            self.count += 1

    instance = Instance()

    person.subscribe_multiple({
        "name": instance.on_field_change,
        "age": instance.on_field_change,
        "height": instance.on_field_change,
        "is_male": instance.on_field_change
    })

    person.name = "Jane"
    person.age = 30
    person.height = 1.80
    person.is_male = False

    # 测试订阅多个字段的回调函数
    assert function_count == 4
    # 测试订阅多个字段的实例方法
    assert instance.count == 4


def test_unsubscribe_multiple():
    """
    测试取消多个字段的订阅
    """

    class Config(DataModel):
        name: str
        age: int
        height: float

    config = Config(name="Alice", age=25, height=1.65)
    callback_count = 0

    def on_field_change(new_value):
        nonlocal callback_count
        callback_count += 1

    # 订阅多个字段
    config.subscribe_multiple({
        "name": on_field_change,
        "age": on_field_change,
        "height": on_field_change
    })

    # 修改所有字段，应该触发3次回调
    config.name = "Bob"
    config.age = 30
    config.height = 1.75
    assert callback_count == 3

    # 取消订阅多个字段
    config.unsubscribe_multiple({
        "name": on_field_change,
        "age": on_field_change
    })

    # 再次修改所有字段，只有height应该触发回调
    config.name = "Charlie"
    config.age = 35
    config.height = 1.80
    assert callback_count == 4  # 只增加了1次


def test_inheritance_and_default_values():
    """
    测试模型继承和默认值
    """

    class BaseConfig(DataModel):
        version: str = "1.0.0"
        name: str

    class UserConfig(BaseConfig):
        age: int = 18
        is_admin: bool = False

    class ExtendedUserConfig(UserConfig):
        height: float = 1.75
        weight: float

    # 测试默认值
    base = BaseConfig(name="Base")
    assert base.version == "1.0.0"

    user = UserConfig(name="User")
    assert user.version == "1.0.0"  # 继承的默认值
    assert user.age == 18
    assert user.is_admin is False

    # 测试多级继承
    extended = ExtendedUserConfig(name="Extended", weight=70.0)
    assert extended.version == "1.0.0"  # 继承的默认值
    assert extended.age == 18  # 继承的默认值
    assert extended.is_admin is False  # 继承的默认值
    assert extended.height == 1.75  # 默认值
    assert extended.weight == 70.0  # 设置的值

    # 测试覆盖默认值
    custom = ExtendedUserConfig(name="Custom", version="2.0.0", age=25, is_admin=True, height=1.85, weight=75.0)
    assert custom.version == "2.0.0"
    assert custom.age == 25
    assert custom.is_admin is True
    assert custom.height == 1.85
    assert custom.weight == 75.0


def test_conditional_callback():
    """
    测试条件回调函数
    """

    class UserSettings(DataModel):
        username: str
        age: int
        level: int = 1
        score: int = 0

    user = UserSettings(username="player1", age=20)
    level_up_count = 0
    score_milestone_count = 0

    # 定义条件回调函数
    def on_level_up(new_value):
        nonlocal level_up_count
        level_up_count += 1
        assert new_value > 1  # 确保等级提升了

    def on_score_milestone(new_value):
        nonlocal score_milestone_count
        if new_value >= 100:  # 只在分数达到100或更高时触发
            score_milestone_count += 1

    # 订阅字段变化
    user.subscribe("level", on_level_up)
    user.subscribe("score", on_score_milestone)

    # 测试等级提升
    user.level = 2
    assert level_up_count == 1

    user.level = 3
    assert level_up_count == 2

    # 测试分数里程碑
    user.score = 50  # 不应触发回调
    assert score_milestone_count == 0

    user.score = 100  # 应触发回调
    assert score_milestone_count == 1

    user.score = 150  # 应触发回调
    assert score_milestone_count == 2

    # 测试取消订阅后的行为
    user.unsubscribe("level", on_level_up)
    user.level = 4  # 不应触发回调
    assert level_up_count == 2  # 计数不变


def test_nested_models():
    """
    测试嵌套模型结构
    """

    class Address(DataModel):
        city: str
        street: str
        postal_code: str = "000000"

    class User(DataModel):
        name: str
        age: int
        address: Address

    # 创建嵌套模型实例
    address = Address(city="北京", street="长安街")
    user = User(name="张三", age=30, address=address)

    # 测试嵌套模型的字段访问
    assert user.address.city == "北京"
    assert user.address.street == "长安街"
    assert user.address.postal_code == "000000"  # 默认值

    # 测试修改嵌套模型的字段
    user.address.city = "上海"
    assert user.address.city == "上海"

    # 测试嵌套模型的字段订阅
    city_change_count = 0

    def on_city_change(new_value):
        nonlocal city_change_count
        city_change_count += 1
        assert new_value == "广州"

    # 订阅嵌套模型的字段
    user.address.subscribe("city", on_city_change)

    # 修改嵌套模型的字段，应该触发回调
    user.address.city = "广州"
    assert city_change_count == 1

    # 测试替换整个嵌套模型
    new_address = Address(city="深圳", street="南山大道", postal_code="518000")
    user.address = new_address

    # 验证新的嵌套模型字段值
    assert user.address.city == "深圳"
    assert user.address.street == "南山大道"
    assert user.address.postal_code == "518000"
