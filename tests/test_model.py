from pathlib import Path
from typing import List, Dict

from pyconfigevents import RootModel, ChildModel
from pyconfigevents.utils.save_file import save_to_file


class TestChildModel:
    def test_child_model_init(self):
        """测试ChildModel的初始化"""
        class Model(ChildModel):
            name: str
        child = Model(name="test_child")
        assert child.name == "test_child"
        assert child.pce_root_model is None
    
    def test_child_model_setup_root_model(self):
        """测试设置根模型"""
        class TestRoot(RootModel):
            pass
        
        root = TestRoot(pce_file_path=Path("test.json"))
        child = ChildModel(name="test_child")
        child.setup_root_model(root)
        assert child.pce_root_model is root
    
    def test_child_model_auto_save(self, tmp_path):
        """测试子模型自动保存功能"""
        class ConfigModel(RootModel):
            class _Item(ChildModel):
                name: str
            item: _Item
        
        file_path = tmp_path / "test.json"
        save_to_file({"item": {"name": "test"}}, Path(file_path))
        root = ConfigModel.from_file(file_path)
        root.pce_file_path = file_path
        root.pce_auto_save = True
        
        # 修改子模型应该触发自动保存
        root.item.name = "updated_child"
        
        # 重新加载文件验证是否保存成功
        reloaded = ConfigModel.from_file(file_path)
        assert reloaded.item.name == "updated_child"


class TestRootModel:
    def test_root_model_init(self):
        """测试RootModel的初始化"""
        root = RootModel(pce_file_path=Path("test.json"))
        assert root.pce_file_path == Path("test.json")
        assert root.pce_auto_save is False
    
    def test_root_model_from_file(self, tmp_path):
        """测试从文件加载RootModel"""
        # 创建测试配置文件
        file_path = tmp_path / "test.json"
        with open(file_path, "w") as f:
            f.write('{"name": "test_root"}')
        
        class TestRoot(RootModel):
            name: str
        
        # 从文件加载
        root = TestRoot.from_file(file_path)
        assert root.name == "test_root"
        assert root.pce_file_path == file_path
        assert root.pce_auto_save is False
        
        # 测试auto_save参数
        root_auto_save = TestRoot.from_file(file_path, auto_save=True)
        assert root_auto_save.pce_auto_save is True
    
    def test_root_model_to_dict(self):
        """测试转换为字典"""
        class TestRoot(RootModel):
            name: str
            value: int
        
        root = TestRoot(name="test", value=123, pce_file_path=Path("test.json"))
        data = root.to_dict()
        
        # 验证pce_开头的字段被移除
        assert "name" in data
        assert "value" in data
        assert "pce_file_path" not in data
        assert "pce_auto_save" not in data
    
    def test_root_model_save_to_file(self, tmp_path):
        """测试保存到文件"""
        class TestRoot(RootModel):
            name: str
        
        file_path = tmp_path / "test.json"
        root = TestRoot(name="test_root", pce_file_path=file_path)
        root.save_to_file()
        
        # 验证文件已创建
        assert file_path.exists()
        
        # 重新加载验证内容
        reloaded = TestRoot.from_file(file_path)
        assert reloaded.name == "test_root"
    
    def test_nested_child_models(self, tmp_path):
        """测试嵌套的子模型"""
        class NestedChild(ChildModel):
            value: int
        
        class TestChild(ChildModel):
            name: str
            nested: NestedChild
        
        class TestRoot(RootModel):
            child: TestChild
        
        file_path = tmp_path / "test.json"
        root = TestRoot(
            pce_file_path=file_path,
            child=TestChild(
                name="test_child",
                nested=NestedChild(value=42)
            )
        )
        
        # 验证根模型已正确设置到所有子模型
        assert root.child.pce_root_model is root
        assert root.child.nested.pce_root_model is root
        
        # 启用自动保存
        root.pce_auto_save = True
        
        # 修改嵌套子模型应该触发自动保存
        root.child.nested.value = 100
        
        # 重新加载验证
        reloaded = TestRoot.from_file(file_path)
        assert reloaded.child.nested.value == 100
    
    def test_list_dict_child_models(self, tmp_path):
        """测试列表和字典中的子模型"""
        class ListDictChild(ChildModel):
            value: int
        
        class TestRoot(RootModel):
            list_children: List[ListDictChild]
            dict_children: Dict[str, ListDictChild]
        
        file_path = tmp_path / "test.json"
        test_content = {
            "list_children": [{"value": 1}, {"value": 2}],
            "dict_children": {"a": {"value": 3}, "b": {"value": 4}}
        }
        save_to_file(test_content, file_path)
        root = TestRoot.from_file(file_path)
        
        # 验证根模型已正确设置到所有子模型
        for child in root.list_children:
            assert child.pce_root_model is root
        
        for child in root.dict_children.values():
            assert child.pce_root_model is root
        
        # 启用自动保存
        root.pce_auto_save = True
        
        # 修改列表和字典中的子模型应该触发自动保存
        print(root.list_children)
        root.list_children[0].value = 10
        root.dict_children["a"].value = 30
        
        # 重新加载验证
        reloaded = TestRoot.from_file(file_path)
        assert reloaded.list_children[0].value == 10
        assert reloaded.dict_children["a"].value == 30