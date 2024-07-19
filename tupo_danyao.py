from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword

import re
import datetime
from dateutil.relativedelta import relativedelta
import asyncio

from . import (
    GroupIds, BotId, ManagerIds,
)
from . import (
    LoopEvent, Monitor,
)
from . import (
    api_check_config,
    api_check_task__exec_by_bot_at,
    api_update_state__by_bot_at,
    api_update_state__by_at,
)
from . import xxbot

timing = xxbot['tpd_timing']
monitor = Monitor(name='突破丹监控', start=True)

# 丹药映射
DrugMapping = {
    '练气境圆满': [
        ('筑基丹', 1),
    ],
    '筑基境圆满': [
        ('聚顶丹', 1),
        ('朝元丹', 1),
    ],
    '结丹境圆满': [
        ('锻脉丹', 1),
        ('护脉丹', 1),
    ],
    '元婴境圆满': [
        ('天命淬体丹', 1),
        ('澄心塑魂丹', 1),
        ('混元仙体丹', 1),
    ],
    '化神境圆满': [
        ('黑炎丹', 1),
        ('金血丸', 1),
    ],
    '炼虚境圆满': [
        ('虚灵丹', 1),
        ('净明丹', 1),
    ],
    '合体境圆满': [
        ('安神灵液', 1),
        ('魇龙之血', 1),
    ],
    '大乘境初期': [
        ('明心丹', 5),
    ],
    '大乘境中期': [
        ('明心丹', 5),
    ],
    '大乘境圆满': [
        ('化劫丹', 1),
    ],
    '渡劫境初期': [
        ('太上玄门丹', 2),
    ],
    '渡劫境中期': [
        ('太上玄门丹', 3),
    ],
    '渡劫境圆满': [
        ('幻心玄丹', 5),
    ],
    '半步真仙': [
        ('太上玄门丹', 1),
    ],
    '真仙境初期': [
        ('鬼面炼心丹', 5),
    ],
    '真仙境中期': [
        ('鬼面炼心丹', 5),
    ],
    '真仙境圆满': [
        ('金仙破厄丹', 1),
    ],
    '金仙境初期': [
        ('少阴清灵丹', 5),
    ],
    '金仙境中期': [
        ('少阴清灵丹', 5),
    ],
    '金仙境圆满': [
        ('太乙炼髓丹', 1),
    ],
    '太乙境初期': [
        ('天命炼心丹', 5),
    ],
    '太乙境中期': [
        ('天命炼心丹', 5),
    ],
}

'''
@金魚 道友成功使用丹药：鬼面炼心丹，下一次突破的成功概率提高1.0%！
@炎发灼眼の恶魔 道友成功使用丹药：金仙破厄丹，下一次突破的成功概率提高20.0%！
@永乐大帝 你没有丹药

'''
command = on_command("突破丹", aliases={"突破丹", "tpd", "tpdy"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭突破丹", aliases={"!突破丹", "!tpd", "!tpdy"}, rule=to_me(), priority=60, block=True)

command_ture_success = on_command("", aliases={""}, rule=keyword('恭喜道友突破'), priority=100, block=True)


@command_ture_success.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_task__exec_by_bot_at(event, timing=timing):
        return

    msg_str = str(msg)
    pattern = r'突破(\D+)成功'
    match = re.search(pattern, msg_str)
    # 境界
    level = match.group(1).strip()

    timing('running', '正在使用突破丹')
    await using(cmd=command_ture_success, level=level)
    timing('waiting', '使用完成')


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_config(event, at_me=True):
        return

    # 启动
    if not timing.check('is_usable'):
        return

    timing('start')

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        await timing.sleep(5)

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    api_update_state__by_at(event, timing, state={
        'state': 'done',
        'msg': '手动结束',
    })


AtBot = Message(f"[CQ:at,qq={BotId}] ")


async def using(cmd, level):
    """服药"""
    drug = DrugMapping.get(level, [])

    for name, count in drug:
        for rec in range(0, count):
            await cmd.send(AtBot + + Message(f'服用丹药 {name}'))
            await asyncio.sleep(2)
