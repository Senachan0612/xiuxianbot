from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword

import re
import datetime
from dateutil.relativedelta import relativedelta
import asyncio

from . import (
    GroupIds, BotId, ManagerIds, Task_Level,
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

AtBot = Message(f"[CQ:at,qq={BotId}] ")

timing = xxbot['xsl_timing']
monitor = Monitor(name='宗门任务监控', start=True)
cg_timing = xxbot['cg_timing']

TaskList = [
    # 九品 性平
    ['离火梧桐芝', '尘磊岩麟果', '太乙碧莹花', '森檀木', '龙须藤', '地龙干', ],
    # 功法 01
    ['冲击之刃', '夏日闪耀之力', ],
    # 八品 性平
    ['鎏鑫天晶草', '木灵三针花', '阴阳黄泉花', '厉魂血珀', '狼桃', '霸王花', ],
    # 功法 02
    ['魔力迸发', '真龙九变', ],
    # 九品 冷热
    ['剑魄竹笋', '明心问道果', '炼心芝', '重元换血草', '鬼面花', '梧桐木', ],
    # 五品 性平
    ['地心火芝', '天蝉灵叶', '灯心草', '天灵果', '伴妖草', '剑心竹', ],
    # 七品 性平
    ['地心淬灵乳', '天麻翡石精', '渊血冥花', '天问花', '肠蚀草', '血玉竹', ],
    # 五品 冷热
    ['雪玉骨参', '腐骨灵花', '穿心莲', '龙鳞果', '绝魂草', '月灵花', ],
    # 功法 03
    ['金刚移山诀', ],
    # 八品 冷热
    ['剑魄竹笋', '明心问道果', '炼心芝', '重元换血草', '鬼面花', '梧桐木', ],
    # 六品 性平
    ['三叶青芝', '七彩月兰', '白沉脂', '苦曼藤', '混元果', '皇龙花', ],
    # 七品 冷热
    ['八角玄冰草', '奇茸通天菊', '芒焰果', '问道花', '凤血果', '冰精芝', ],
    # 六品 冷热
    ['三尾风叶', '冰灵焰草', '血菩提', '诱妖草', '天剑笋', '黑天麻', ],
    # 四品 性平
    ['血莲精', '鸡冠草', '乌稠木', '菩提花', '锦地罗', '石龙芮', ],
    # 三品 性平
    ['紫猴花', '九叶芝', '轻灵草', '龙葵', '炼魂珠', '枫香脂', ],
    # 四品 冷热
    ['银精芝', '玉髓芝', '雪凝花', '龙纹草', '冰灵果', '玉龙参', ],
    # 二品 性平
    ['天元果', '五柳根', '流莹草', '蛇涎果', '伏龙参', '风灵花', ],
    # 三品 冷热
    ['幻心草', '鬼臼草', '弗兰草', '玄参', '玄冰花', '炼血珠', ],
    # 一品 性平
    ['恒心草', '红绫草', '宁心草', '凝血草', '火精枣', '地黄参', ],
    # 二品 冷热
    ['何首乌', '夜交藤', '夏枯草', '百草露', '凌风花', '补天芝', ],
    # 一品 冷热
    ['罗犀草', '天青花', '银月花', '宁神花', '剑芦', '七星草', ],
]
task_mapping = {_v: _i * 100 + _j for (_i, _t) in enumerate(TaskList) for (_j, _v) in enumerate(_t)}


def xsl_format(_task):
    """格式化输出悬赏令"""
    pattern = re.compile(r'预计需(\d+)分钟(?:，可额外获得奖励：([\u4e00-\u9fa5]+))?')
    matches = pattern.findall(_task)
    return [(_i, float(_t) * 60, _n) for _i, (_t, _n) in enumerate(matches, start=1)]


def xsl_get_target(_task):
    """获取最有效悬赏"""
    _format = xsl_format(str(_task))
    _map = {task_mapping.get(_n, float('inf')): (_i, _t, _n) for _i, _t, _n in _format}
    return _map[min(_map)]


"""悬赏令 初始"""

Reply_xsl_cs = AtBot + Message(f'悬赏令')

xsl_cs_monitor = Monitor(name='悬赏令初始监控', start=True)

command_cs = on_command("", aliases={""}, rule=keyword('道友的个人悬赏令'), priority=100, block=True)


@command_cs.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, xsl_cs_monitor):
        return
    xsl_cs_monitor('done', msg=msg)


async def _xsl_cs(_cmd, _event):
    """悬赏令初始"""
    timing(msg='悬赏令初始')
    xsl_cs_monitor('init', start=True)
    loop = LoopEvent(_event, name='xsl_cs_loop')

    went_await = loop.add(loop.loop_await_cmd('xsl cs', monitor=xsl_cs_monitor))
    went_send = loop.add(loop.loop_send_cmd('xsl cs', cmd=_cmd, msg=Reply_xsl_cs))

    await went_await
    await went_send

    return xsl_cs_monitor


"""悬赏令 结算"""

Reply_xsl_js = AtBot + Message(f'悬赏令结算')

xsl_js_monitor = Monitor(name='悬赏令结算监控', start=True)

js_ture_pattern = r'(悬赏令结算|道友现在什么都没干呢)'
command_js_ture = on_regex(pattern=js_ture_pattern, flags=re.I, permission=GROUP, priority=100, block=True)
command_js_false = on_command("", aliases={""}, rule=keyword('进行中的悬赏令'), priority=100, block=True)
js_error_pattern = r'(道友现在在闭关呢|小心走火入魔)'
command_js_error = on_regex(pattern=js_error_pattern, flags=re.I, permission=GROUP, priority=100, block=True)


@command_js_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, xsl_js_monitor):
        return
    xsl_js_monitor.set_time(0)
    xsl_js_monitor('done')


@command_js_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, xsl_js_monitor):
        return

    msg_str = str(msg)
    pattern = r'预计(\d+\.\d+)(分钟)后可结束'
    match = re.search(pattern, msg_str)
    time, unit = float(match.group(1)), match.group(2).strip()
    if unit == '分钟':
        time *= 60

    xsl_js_monitor.set_time(time)
    xsl_js_monitor('next')


@command_js_error.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, xsl_js_monitor):
        return

    xsl_js_monitor('error')


async def _xsl_js(_cmd, _event):
    """悬赏令结算"""
    timing(msg='悬赏令结算')
    xsl_js_monitor('init', start=True)
    loop = LoopEvent(_event, name='xsl_js_loop')

    went_await = loop.add(loop.loop_await_cmd('xsl js', monitor=xsl_js_monitor))
    went_send = loop.add(loop.loop_send_cmd('xsl js', cmd=_cmd, msg=Reply_xsl_js))

    await went_await
    await went_send

    return xsl_js_monitor


"""悬赏令 接取"""

xsl_jq_monitor = Monitor(name='悬赏令接取监控', start=True)

command_jq_ture = on_command("", aliases={""}, rule=keyword('接取任务'), priority=100, block=True)
command_jq_false = on_command("", aliases={""}, rule=keyword('道友现在在做悬赏令呢'), priority=100, block=True)


@command_jq_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, xsl_jq_monitor):
        return

    xsl_jq_monitor('done')


@command_jq_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event, timing, xsl_jq_monitor):
        return

    xsl_jq_monitor('error')


async def _xsl_jq(_cmd, _event, _task):
    """悬赏令接取"""
    timing(msg='悬赏令接取')

    _task_id, _task_time, _ = xsl_get_target(_task)
    _reply = AtBot + Message(f'悬赏令接取 {_task_id}')

    # 处理悬赏接取
    xsl_jq_monitor('init', start=True)
    loop = LoopEvent(_event, name='xsl_jq_loop')

    went_await = loop.add(loop.loop_await_cmd('xsl js', monitor=xsl_jq_monitor))
    went_send = loop.add(loop.loop_send_cmd('xsl js', cmd=_cmd, msg=_reply))

    await went_await
    await went_send

    xsl_jq_monitor.set_time(_task_time)
    return xsl_jq_monitor


"""悬赏令"""

command = on_command("悬赏令", aliases={"悬赏令", "xsl"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭悬赏令", aliases={"!悬赏令", "!xsl"}, rule=to_me(), priority=60, block=True)


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_config(event, at_me=True):
        return

    # 功能与出闭关冲突
    if not cg_timing.check('is_usable'):
        await command.send(Message(f"[CQ:at,qq={event.user_id}]") + Message(f" 请先关闭自动出闭关功能"))
        return

    # 启动
    if not timing.check('is_usable'):
        return
    timing('start')

    """监听"""
    while True:
        # 等待悬赏完成
        await timing.sleep()

        timing('running')
        monitor('init', start=True)

        # 初始化
        _monitor = await _xsl_cs(command, event)
        if not _monitor.check('is_done'):
            break

        # 结算
        _monitor = await _xsl_js(command, event)
        if _monitor.check('is_next'):
            timing.set_time(_monitor.time)
            timing('waiting', msg='悬赏令结算CD')
            continue
        elif not _monitor.check('is_done'):
            break

        # 初始化
        _monitor = await _xsl_cs(command, event)
        if not _monitor.check('is_done'):
            break

        # 走完结算后视为完成单次流程 再此处结束
        if timing.check('is_finish'):
            break

        # 接取
        _monitor = await _xsl_jq(command, event, _task=_monitor.msg)
        if not _monitor.check('is_done'):
            break

        timing.set_time(_monitor.time)
        timing('waiting', msg='悬赏令接取成功')

    timing.init()


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    api_update_state__by_at(event, timing, state={
        'state': 'done',
        'msg': '手动结束',
    })
