"""
    药草
"""
import csv
import re
from collections import namedtuple


def package_covert(data: str) -> dict:
    """背包数据提取药材"""
    pattern = re.compile(
        r'名字：(.*?)\n品级：(.*?)\n主药 (.{2})(\d+) (.{2})(\d+)\n药引 (.{2})(\d+)辅药 (.{2})(\d+)\n拥有数：(\d+)（')
    matches = pattern.findall(data)

    Info = namedtuple('YaoCaoTuple', 'level name temp attr main_temp main_attr sub_temp sub_attr count')

    return {rec[0]: Info(rec[1], rec[0], int(rec[3]), int(rec[5]), rec[2], rec[4], rec[6], rec[8], int(rec[10]), )
            for rec in matches}


def update(dataset):
    file_path = r'.\yaocao.csv'

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 写入表头
        head = ['品级', '名字', '冷热值', '效果值', '主药冷热', '主药效果', '药引冷热', '辅药效果']
        writer.writerow(head)

        # 写入匹配到的药材信息
        for match in dataset.values():
            writer.writerow(match[:len(head)])

# # 原始字符串
# data_ = """
# @金魚 星野的背包，持有灵石：45193915枚
# 名字：血玉竹
# 品级：七品药材
# 主药 性平64 聚元128
# 药引 性平64辅药 凝神128
# 拥有数：2（自由）
# 名字：凤血果
# 品级：七品药材
# 主药 性寒64 聚元128
# 药引 性热64辅药 凝神128
# 拥有数：2（自由）
# 名字：冰精芝
# 品级：七品药材
# 主药 性热64 聚元128
# 药引 性寒64辅药 凝神128
# 拥有数：3（自由）
# 名字：狼桃
# 品级：八品药材
# 主药 性平128 聚元256
# 药引 性平128辅药 凝神256
# 拥有数：3（自由）
# 名字：霸王花
# 品级：八品药材
# 主药 性平128 聚元256
# 药引 性平128辅药 凝神256
# 拥有数：8（自由）
# 名字：太清玄灵草
# 品级：八品药材
# 主药 性寒128 聚元256
# 药引 性热128辅药 凝神256
# 拥有数：10（自由）
# 名字：冥胎骨
# 品级：八品药材
# 主药 性热128 聚元256
# 药引 性寒128辅药 凝神256
# 拥有数：5（自由）
# 名字：地龙干
# 品级：九品药材
# 主药 性平256 聚元512
# 药引 性平256辅药 凝神512
# 拥有数：9（自由）
# 名字：龙须藤
# 品级：九品药材
# 主药 性平256 聚元512
# 药引 性平256辅药 凝神512
# 拥有数：5（自由）
# 名字：鬼面花
# 品级：九品药材
# 主药 性寒256 聚元512
# 药引 性热256辅药 凝神512
# 拥有数：3（自由）
# 名字：梧桐木
# 品级：九品药材
# 主药 性热256 聚元512
# 药引 性寒256辅药 凝神512
# 拥有数：7（自由）
# ☆------特殊物品------☆
# 名字：环奈币
# 描述：上面印有环奈头像，肯定能花，据说1环奈币等于3.14美金（虽然没人知道什么是美金）
# 拥有数：1（绑定）
# 名字：桥本盲盒
# 描述：充满仙气的盒子，哪怕是太乙境界的大能也不能窥探其中奥妙
# 拥有数：2（自由）
# 名字：饿肚丹
# 描述：谁买我笑他一坤年--BY 神秘的环奈
# 拥有数：1（自由）
# 当前最大页数12, 目前11页
# """
#
# dataset_ = package_covert(data_)
#
# update(dataset_)
#
# print(f"药材信息已写入")
