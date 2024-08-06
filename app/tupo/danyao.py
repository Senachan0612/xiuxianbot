"""突破丹药功能"""

import os
import json
import re
import asyncio
from collections import namedtuple

from nonebot.plugin.on import on_fullmatch, on_keyword, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    DataPath,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""突破丹药"""

# 加载配置
File_Path = r'%s\%s' % (DataPath, 'TuPoDanYao.json')
DanYao = namedtuple('DanYao', 'name count')
# 突破丹药清单
DefaultDanYaoList = {
    '练气境圆满': [
        DanYao('筑基丹', 1),
    ],
    '筑基境圆满': [
        DanYao('聚顶丹', 1),
        DanYao('朝元丹', 1),
    ],
    '结丹境圆满': [
        DanYao('锻脉丹', 1),
        DanYao('护脉丹', 1),
    ],
    '元婴境圆满': [
        DanYao('天命淬体丹', 1),
        DanYao('澄心塑魂丹', 1),
        DanYao('混元仙体丹', 1),
    ],
    '化神境圆满': [
        DanYao('黑炎丹', 1),
        DanYao('金血丸', 1),
    ],
    '炼虚境圆满': [
        DanYao('虚灵丹', 1),
        DanYao('净明丹', 1),
    ],
    '合体境圆满': [
        DanYao('安神灵液', 1),
        DanYao('魇龙之血', 1),
    ],
    '大乘境初期': [
        DanYao('明心丹', 5),
    ],
    '大乘境中期': [
        DanYao('明心丹', 5),
    ],
    '大乘境圆满': [
        DanYao('化劫丹', 1),
    ],
    '渡劫境初期': [
        DanYao('太上玄门丹', 2),
    ],
    '渡劫境中期': [
        DanYao('太上玄门丹', 3),
    ],
    '渡劫境圆满': [
        DanYao('幻心玄丹', 5),
    ],
    '半步真仙': [
        DanYao('太上玄门丹', 1),
    ],
    '真仙境初期': [
        DanYao('鬼面炼心丹', 5),
    ],
    '真仙境中期': [
        DanYao('鬼面炼心丹', 5),
    ],
    '真仙境圆满': [
        DanYao('金仙破厄丹', 1),
    ],
    '金仙境初期': [
        DanYao('少阴清灵丹', 5),
    ],
    '金仙境中期': [
        DanYao('少阴清灵丹', 5),
    ],
    '金仙境圆满': [
        DanYao('太乙炼髓丹', 1),
    ],
    '太乙境初期': [
        DanYao('天命炼心丹', 5),
    ],
    '太乙境中期': [
        DanYao('天命炼心丹', 5),
    ],
}

try:
    if os.path.isfile(File_Path):
        # 加载用户配置
        with open(File_Path, mode='r', encoding='utf-8') as f:
            DanYaoList = {_key: [DanYao(*_v) for _v in _val] for _key, _val in json.load(f).items()}
    else:
        if not os.path.isdir(DataPath):
            os.makedirs(DataPath)

        with open(File_Path, mode='w', encoding='utf-8') as f:
            json.dump(DefaultDanYaoList, f, ensure_ascii=False, indent=2)
        DanYaoList = DefaultDanYaoList
except Exception:
    DanYaoList = DefaultDanYaoList
# 境界
LevelList = list(DanYaoList.keys())


def get_level_index(_level, _default_index):
    """获取境界对应优先级"""
    try:
        _index = LevelList.index(_level)
    except ValueError:
        _index = _default_index
    return _index


# 注册监控器
timing = Monitor(name='突破丹药', time=60)

command = on_fullmatch(('突破丹药', 'tpdy'), rule=to_me(), priority=60, block=True)
exit_command = on_fullmatch(('关闭突破丹药', '!突破丹药', '!tpdy'), rule=to_me(), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '突破丹药': {
        'timing': timing,
        'cmd': command,
        'auto': True,
    },
})


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 启动
    if not timing('start'):
        return

    timing('running')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'init',
    })


"""服用突破丹"""

monitor = Monitor(name='服用丹药监控')

command_fydy = sc_command_success = on_keyword({'恭喜道友突破'}, rule=to_me(), priority=100)


@command_fydy.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    timing(msg='开始服用突破丹')

    pattern = r'突破(\D+)成功'
    match = re.search(pattern, str(msg))
    # 境界
    level = match.group(1).strip()

    # 渡厄丹启用
    if xxBot.get_config('is_use_due'):
        auto_use_due_level = xxBot.get_config('auto_use_due_level', '渡劫境圆满')
        index__auto_use_due_level = get_level_index(auto_use_due_level, float('inf'))
        index__level = get_level_index(level, -1)
        # 设置自动使用渡厄
        xxBot.set_config('is_auto_use_due', index__auto_use_due_level <= index__level)

    # 突破丹药
    drugs = DanYaoList.get(level, [])

    while drugs:
        monitor('init')
        name, count = drugs.pop()
        timing(msg='开始服用突破丹')

        for _ in range(count):
            if monitor.check('is_break'):
                break

            await command_fydy.send(xxBot.msg__at_xxbot + Message(f'服用丹药 {name}'))
            await asyncio.sleep(5)

    monitor('init')
    timing(msg=f'已服用{level}突破丹药')


"""服用突破丹 失败"""

fydy_false_pattern = r'(道友没有该丹药|道友不满足使用条件)'
command_fydy_false = on_regex(pattern=fydy_false_pattern, flags=re.I, permission=GROUP, rule=to_me(), priority=100)


@command_fydy_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('skip')


"""使用渡厄丹"""

DuEDanNamePattern = '渡厄丹|肚饿丹'
ExeCommandTruePattern = '使用|启用'
ExeCommandFalsePattern = '禁用|停用'
ExeTypePattern = '立刻'
command_use_due_pattern = fr'({DuEDanNamePattern})\s*({ExeTypePattern}\s*)?({ExeCommandTruePattern}|{ExeCommandFalsePattern})|\s*({ExeTypePattern}\s*)?({ExeCommandTruePattern}|{ExeCommandFalsePattern})\s*({DuEDanNamePattern})'
command_use_due = on_regex(pattern=command_use_due_pattern, flags=re.I, permission=GROUP, rule=to_me(), priority=100)


@command_use_due.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    str_msg = str(msg)

    # 是否启用
    is_use_due = bool(re.compile(rf'({ExeCommandTruePattern})').search(str_msg))
    # 自动使用境界
    level_pattern = re.compile(rf'({"|".join(LevelList)})')
    auto_use_due_level = level_pattern.findall(str_msg)
    # 立刻自动使用
    is_auto_use_due = bool(
        re.compile(rf'({ExeTypePattern}\s*)({ExeCommandTruePattern}|{ExeCommandFalsePattern})').search(str_msg))

    xxBot.set_config('is_use_due', is_use_due)
    xxBot.set_config('is_auto_use_due', is_auto_use_due)
    if auto_use_due_level:
        xxBot.set_config('auto_use_due_level', auto_use_due_level[0])

    await command_use_due.finish(Message(f'[CQ:at,qq={event.user_id}] ')
                                 + Message(f'渡厄丹设置成功！\n' + xxBot.print_info('due')))


"""日志"""


def due_config_info():
    """肚饿丹相关配置信息"""
    return '肚饿丹配置信息', [
        ['肚饿丹', '启用' if xxBot.get_config('is_use_due') else '禁止', ],
        ['自动使用', '是' if xxBot.get_config('is_auto_use_due') else '否', ],
        ['自动使用境界', xxBot.get_config('auto_use_due_level', ''), ],
    ]


xxBot.load_info('due', due_config_info)
