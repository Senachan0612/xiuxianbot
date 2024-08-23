"""存放一些持久性性数据"""

__all__ = [
    'DataPath',
    'UserData',  # 用户数据
]

import os

DataPath = os.path.dirname(__file__)

# 加载数据
from . import drug


class Data:
    # 数据
    _data = {}
    # 根路径
    path = DataPath
    # 映射
    DataMap = {
        'Drug': drug
    }

    def __init__(self):
        ...

    def __getitem__(self, name):
        """获取数据"""
        title = name.title()
        if title not in self._data:
            self.load(title)

        return self._data[title]

    def load(self, name: str, reload=False):
        """加载数据"""
        title = name.title()
        if title not in self.DataMap:
            self._data[title] = {}
            return

        filename = r'%s\%s.json' % (self.path, title)
        app = self.DataMap[title]

        if reload or not os.path.isfile(filename):
            # 生成数据
            if not os.path.isdir(self.path):
                os.makedirs(self.path)

            self._data[title] = app.register(self.path, filename)
        else:
            # 读取数据
            self._data[title] = app.load(filename)


UserData = Data()
