from pathlib import Path

import pytest

from pyconfigevents import File, ConfigFile


def init_env(tmp_path: Path) -> None:
    """
    用于创建测试环境
    """
    try:
        # 创建测试文件夹
        tmp_path.mkdir()
    except FileExistsError:
        pass
    # 创建测试文件
    (tmp_path / "temp.txt").touch()
    # 创建子测试文件
    (tmp_path / "temp2.txt").touch()
    try:
        # 创建测试子文件夹
        (tmp_path / "temp").mkdir()
    except FileExistsError:
        pass
    # 创建测试子文件
    (tmp_path / "temp" / "temp.txt").touch()


# 测试File类
class TestFile:
    def test_init(self, tmp_path: Path):
        init_env(tmp_path)
        # 只能文件
        with pytest.raises(ValueError):
            File(tmp_path)

        # 测试属性都正确赋值了
        file = File(tmp_path / "temp.txt")
        assert file.filename == "temp.txt"
        assert file.path.samefile(tmp_path / "temp.txt")
        assert file.folder.samefile(tmp_path)

    def test_eq(self, tmp_path: Path):
        """
        测试__eq__方法,确保File类的实例可以正确比较.
        1. 同文件夹下同名文件
        2. 同文件夹下不同名文件
        3. 不同文件夹下同名文件
        """
        init_env(tmp_path)
        file1 = File(tmp_path / "temp.txt")
        file2 = File(tmp_path / "temp.txt")
        file3 = File(tmp_path / "temp2.txt")
        file4 = File(tmp_path / "temp" / "temp.txt")
        assert file1 == file2
        assert file1 != file3
        assert file1 != file4
        assert file3 != file4

    def test_hash(self, tmp_path: Path):
        """
        测试__hash__方法,确保File类的实例可以正确哈希.
        1. 同文件夹下同名文件
        2. 同文件夹下不同名文件
        3. 不同文件夹下同名文件
        """
        init_env(tmp_path)
        file1 = File(tmp_path / "temp.txt")
        file2 = File(tmp_path / "temp2.txt")
        file3 = File(tmp_path / "temp" / "temp.txt")
        file4 = File(tmp_path / "temp" / "temp.txt")
        assert hash(file1) != hash(file2)
        assert hash(file1) != hash(file3)
        assert hash(file2) != hash(file3)
        assert hash(file3) == hash(file4)

        s = set()
        s.add(file1)
        s.add(file2)
        s.add(file3)
        s.add(file4)
        assert len(s) == 3
        assert file1 in s
        assert file2 in s
        assert file3 in s
        assert file4 in s  # 因为file4和file3的哈希值相同且路径相同,所以认为是同一个文件

    def test_validate(self, tmp_path: Path):
        """
        测试validate方法,确保File类的实例可以正确验证.
        1. 验证File类的实例
        2. 验证文件路径字符串
        3. 验证Path类的实例
        4. 非文件类型的Path类实例验证失败
        5. 其余类型验证失败
        """
        init_env(tmp_path)

        # 数据验证通过
        file = File(tmp_path / "temp.txt")
        assert File.validate(file)
        assert File.validate(str(tmp_path / "temp.txt"))
        assert File.validate(tmp_path / "temp.txt")

        # 数据验证不通过
        with pytest.raises(ValueError):
            File.validate(tmp_path)
            File.validate(123)
            File.validate([tmp_path / "temp.txt", tmp_path / "temp" / "temp.txt"])


class TestConfigFile:
    def test_init(self, tmp_path: Path):
        """
        测试ConfigFile类的初始化方法.
        1. 测试支持的几种配置文件能否初始化
        2. 测试除支持的配置文件外的配置文件初始化时能否正确抛出异常
        """
        init_env(tmp_path)
        for end in ConfigFile.SUPPORTED_CONFIG_FILES:
            path = tmp_path / ("temp" + end)
            path.touch()
            file = ConfigFile(path)
            # 验证属性
            assert file.filename == path.name
            assert file.folder.samefile(tmp_path)
            assert file.path.samefile(path)

        # 测试非支持的配置文件
        with pytest.raises(ValueError):
            ConfigFile(tmp_path / "temp.ini")
            ConfigFile(tmp_path / "temp.yml")

    def test_validate(self, tmp_path: Path):
        """
        测试validate方法,确保ConfigFile类的实例可以正确验证.
        1. 验证ConfigFile类的实例
        2. 验证文件路径字符串
        3. 验证Path类的实例
        4. 验证File类的实例
        5. 非文件类型的Path类实例验证失败
        6. 其余类型验证失败
        """
        init_env(tmp_path)

        # 数据验证通过
        (tmp_path / "temp.json").touch()
        file = ConfigFile(tmp_path / "temp.json")
        assert ConfigFile.validate(file)
        assert ConfigFile.validate(File(tmp_path / "temp.json"))
        assert ConfigFile.validate(str(tmp_path / "temp.json"))
        assert ConfigFile.validate(tmp_path / "temp.json")

        # 数据验证不通过
        with pytest.raises(ValueError):
            ConfigFile.validate(tmp_path)
            ConfigFile.validate(123)
            ConfigFile.validate([tmp_path / "temp.json", tmp_path / "temp" / "temp.toml"])
        
