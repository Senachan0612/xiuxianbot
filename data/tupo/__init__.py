"""突破相关"""

import pandas


def register(path, name):
    """生成数据"""
    origin = pandas.read_csv(r'%s\%s' % (path, r'tupo\tupo.csv'))

    # 重命名
    origin.rename(columns={
        '境界': 'code',
        '丹药': 'name',
        '数量': 'count',
    }, inplace=True)

    # # 更新渡厄丹使用范围
    # first_is_used_index = origin[origin['is_used'] == True].index.min()
    # if first_is_used_index is not None:  # 确保找到这样的行
    #     origin.loc[first_is_used_index:, 'is_used'] = True

    origin.to_json(name, orient='index', force_ascii=False, indent=2)

    return origin


def load(name):
    """加载数据"""
    return pandas.read_json(name).T