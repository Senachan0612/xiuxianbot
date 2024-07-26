import re
import os

# import datetime
# from dateutil.relativedelta import relativedelta
#
# # 每日凌晨00:30开始
# now_dt = datetime.datetime.now()
# next_dt = now_dt.replace(hour=0, minute=30, second=0, microsecond=0)
# next_day_early_morning = current_time + relativedelta(days=1)
# print(1)

# class XiuXianBot:
#     def __init__(self):
#
#         self.tasks = {
#             '1': 1,
#             '2': 2,
#         }
#
#     def __getitem__(self, item):
#         return self.tasks[item]
#
#
#
# xxbot = XiuXianBot()
#
# print(1)

# text = """
# @惠 ☆------道友的个人悬赏令------☆
# 重伤真仙马良,完成机率100%,基础报酬3115灵石,预计需114分钟，可额外获得奖励：阴阳黄泉花！
# 击杀冥罗阴鬼王,完成机率100%,基础报酬3115灵石,预计需114分钟！
# 寻找菩提定魂香,完成机率100%,基础报酬2088灵石,预计需72分钟，可额外获得奖励：明心问道果！
# (悬赏令每小时更新一次)
# """
#
# # 正则表达式模式，用于匹配特定时间和奖励的组合
# pattern = re.compile(r'预计需(\d+)分钟(?:，可额外获得奖励：([\u4e00-\u9fa5]+))?')
#
# matches = pattern.findall(text)
#
# # 输出特定的内容
# for match in matches:
#     print(match[0], match[1])

# if match[0] == '114' and match[1]:
#     print(match[0], match[1])
# elif match[0] == '114' and not match[1]:
#     print(match[0])
# elif match[0] == '72' and match[1]:
#     print(match[0], match[1])

# TaskList = [
#     # 九品 性平
#     ['离火梧桐芝', '尘磊岩麟果', '太乙碧莹花', '森檀木', '龙须藤', '地龙干', ],
#     # 功法 01
#     ['冲击之刃', '夏日闪耀之力', ],
#     # 八品 性平
#     ['鎏鑫天晶草', '木灵三针花', '阴阳黄泉花', '厉魂血珀', '狼桃', '霸王花', ],
#     # 功法 02
#     ['魔力迸发', '真龙九变', ],
#     # 九品 冷热
#     ['剑魄竹笋', '明心问道果', '炼心芝', '重元换血草', '鬼面花', '梧桐木', ],
#     # 五品 性平
#     ['地心火芝', '天蝉灵叶', '灯心草', '天灵果', '伴妖草', '剑心竹', ],
#     # 七品 性平
#     ['地心淬灵乳', '天麻翡石精', '渊血冥花', '天问花', '肠蚀草', '血玉竹', ],
#     # 五品 冷热
#     ['雪玉骨参', '腐骨灵花', '穿心莲', '龙鳞果', '绝魂草', '月灵花', ],
#     # 功法 03
#     ['金刚移山诀', ],
#     # 八品 冷热
#     ['剑魄竹笋', '明心问道果', '炼心芝', '重元换血草', '鬼面花', '梧桐木', ],
#     # 六品 性平
#     ['三叶青芝', '七彩月兰', '白沉脂', '苦曼藤', '混元果', '皇龙花', ],
#     # 七品 冷热
#     ['八角玄冰草', '奇茸通天菊', '芒焰果', '问道花', '凤血果', '冰精芝', ],
#     # 六品 冷热
#     ['三尾风叶', '冰灵焰草', '血菩提', '诱妖草', '天剑笋', '黑天麻', ],
#     # 四品 性平
#     ['血莲精', '鸡冠草', '乌稠木', '菩提花', '锦地罗', '石龙芮', ],
#     # 三品 性平
#     ['紫猴花', '九叶芝', '轻灵草', '龙葵', '炼魂珠', '枫香脂', ],
#     # 四品 冷热
#     ['银精芝', '玉髓芝', '雪凝花', '龙纹草', '冰灵果', '玉龙参', ],
#     # 二品 性平
#     ['天元果', '五柳根', '流莹草', '蛇涎果', '伏龙参', '风灵花', ],
#     # 三品 冷热
#     ['幻心草', '鬼臼草', '弗兰草', '玄参', '玄冰花', '炼血珠', ],
#     # 一品 性平
#     ['恒心草', '红绫草', '宁心草', '凝血草', '火精枣', '地黄参', ],
#     # 二品 冷热
#     ['何首乌', '夜交藤', '夏枯草', '百草露', '凌风花', '补天芝', ],
#     # 一品 冷热
#     ['罗犀草', '天青花', '银月花', '宁神花', '剑芦', '七星草', ],
# ]
# task_mapping = {_v: _i * 100 + _j for (_i, _t) in enumerate(TaskList) for (_j, _v) in enumerate(_t)}
# print(task_mapping
#
# )

#
# d = {
#     1: 11,
#     2: 22,
# }
#
# print(min(d))

# print(os.path.isfile('D:/__env__/bot/autoxx-bot/autoxx_bot/plugins/xiuxianbot/data\\Config.json'))

from itertools import chain

#
# class X:
#     def __getitem__(self, item, default=None):
#         if isinstance(item, tuple):
#             item, default, *_ = *item, None, None
#
#         return 1
#
#
# x = X()
# x[1, 1]

text = '''
    "设置授权 11111",
    "设置授权 11111",
    "设置授权 11111 , 2222 adsa"
    
    精确到设置授权之后的数字
'''

pattern = re.compile(r'\d+')
pattern.findall(text)

print(1)

