"""复读相关"""

import pandas


def register(path, name):
    """生成数据"""
    origin_name = r'%s\%s' % (path, r'fudu\fudu.json')
    origin = load(origin_name)
    origin.to_json(name, force_ascii=False, indent=2)

    return origin


def load(name):
    """加载数据"""
    return pandas.read_json(name)
