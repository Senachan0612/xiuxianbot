"""药草相关"""

import pandas


def register(path, name):
    """生成数据"""
    origin = pandas.read_csv(r'%s\%s' % (path, r'drug\drug.csv'))

    # 重命名
    origin.rename(columns={
        '品级': 'code',
        '名字': 'name',
        '主药': 'first',
        '辅药': 'second',
    }, inplace=True)

    # 转换药性
    origin['药性'] = origin['药性'].map({'平': 0, '寒': -1, '热': 1})

    origin['value'] = 2 ** origin['code']
    origin['first_temp'] = origin['药性'] * 2 ** (origin['code'] - 1)
    origin['second_temp'] = origin['first_temp'] * -1

    target = origin[['code', 'name', 'value', 'first', 'second', 'first_temp', 'second_temp']].T
    target.to_json(name, force_ascii=False, indent=2)

    return target


def load(name):
    """加载数据"""
    return pandas.read_json(name)
