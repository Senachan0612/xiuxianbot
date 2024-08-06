"""悬赏令功能"""

import os
import json
import re

from nonebot.plugin.on import on_fullmatch, on_regex, on_keyword
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    DataPath,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""悬赏令"""

# 加载配置
File_Path = r'%s\%s' % (DataPath, 'XuanShangLing.json')
DefaultTaskList = [
    # 功法 01
    ['冲击之刃', '夏日闪耀之力', ],
    # 九品 性平
    ['离火梧桐芝', '尘磊岩麟果', '太乙碧莹花', '森檀木', '龙须藤', '地龙干', ],
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

try:
    if os.path.isfile(File_Path):
        # 加载用户配置
        with open(File_Path, mode='r', encoding='utf-8') as f:
            TaskList = json.load(f)
    else:
        if not os.path.isdir(DataPath):
            os.makedirs(DataPath)

        with open(File_Path, mode='w', encoding='utf-8') as f:
            json.dump(DefaultTaskList, f, ensure_ascii=False, indent=2)
        TaskList = DefaultTaskList
except Exception:
    TaskList = DefaultTaskList
# 优先级映射
task_mapping = {_v: _i * 100 + _j for (_i, _t) in enumerate(TaskList) for (_j, _v) in enumerate(_t)}


def xsl_format(_task):
    """格式化输出悬赏令"""
    pattern = re.compile(r'预计需(\d+)分钟(?:，可额外获得奖励：([\u4e00-\u9fa5]+))?')
    matches = pattern.findall(_task)
    return [(_i, float(_t) * 60, _n) for _i, (_t, _n) in enumerate(matches, start=1)]


def xsl_get_target(_task):
    """获取最有效悬赏"""
    _format = xsl_format(str(_task))
    # 优先级计算公式>>>
    # 物品优先级 = 等级 * 100
    # 时间优先级 = 每30分 * 100
    # 优先级 = 物品优先级 - 时间优先级
    _map = {task_mapping.get(_n, float('inf')) - _t / (30 * 60) * 100: (_i, _t, _n) for _i, _t, _n in _format}
    return _map[min(_map)]


# 注册监控器
timing = Monitor(name='悬赏令')

command = on_fullmatch(('悬赏令', 'xsl'), rule=to_me(), priority=60, block=True)
exit_command = on_fullmatch(('关闭悬赏令', '!悬赏令', '!xsl'), rule=to_me(), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '悬赏令': {
        'timing': timing,
        'cmd': command,
        'auto': False,
    },
})

monitor = Monitor(name='悬赏令监控')
Message__xsl = xxBot.msg__at_xxbot + Message('悬赏令')
Message__sx = xxBot.msg__at_xxbot + Message('悬赏令刷新')
Message__js = xxBot.msg__at_xxbot + Message('悬赏令结算')


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 功能与出闭关冲突
    cbg_timing = xxBot.get_timing('出闭关')
    if cbg_timing and not cbg_timing.check('is_valid'):
        return await command.send(xxBot.msg__at(event.user_id) + Message('请先关闭自动出闭关功能！'))

    # 启动
    if not timing('start'):
        return

    """监听"""
    while True:
        if timing.check('is_regular'):
            await timing.sleep()

        if timing.check('is_finish'):
            break

        # 执行监听
        timing('running')
        monitor('init')

        """ 悬赏令 初始化 """
        _monitor = await __task_cs(command, event)
        if not _monitor.check('is_done'):
            break

        """ 悬赏令 结算 """
        _monitor = await __task_js(command, event)
        if timing.check('is_finish') or not _monitor.check('is_done'):
            break
        if _monitor.check('is_regular'):
            timing.set_time(_monitor.time)
            timing('regular', msg=timing.dt_string(timing.exec_time))
            continue

        """ 悬赏令 初始化 """
        _monitor = await __task_cs(command, event)
        if not _monitor.check('is_done'):
            break

        """ 悬赏令 接取 """
        _monitor = await __task_jq(command, event, _task=_monitor.msg)
        if not _monitor.check('is_done'):
            break

        if timing.check('is_finish'):
            break

        timing.set_time(_monitor.time)
        timing('regular', msg=timing.dt_string(timing.exec_time))

    timing('init', msg='执行结束')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'exit',
        'msg': '手动结束',
    })


"""悬赏令 初始"""

xsl_cs_monitor = Monitor(name='悬赏令初始监控')

command_cs = on_keyword({'道友的个人悬赏令'}, rule=to_me(), priority=100, block=True)


@command_cs.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, xsl_cs_monitor):
        return
    xsl_cs_monitor('done', msg=msg)


async def __task_cs(_cmd, _event):
    """悬赏令 初始"""
    timing(msg='悬赏令初始')
    xsl_cs_monitor('init')
    loop = LoopEvent(_event, name='xsl_cs_loop')

    went_await = loop.add(loop.loop_await_cmd('xsl cs', monitor=xsl_cs_monitor))
    went_send = loop.add(loop.loop_send_cmd('xsl cs', cmd=_cmd, msg=Message__xsl))

    await went_await
    await went_send

    return xsl_cs_monitor


"""悬赏令 结算"""

xsl_js_monitor = Monitor(name='悬赏令结算监控')

js_ture_pattern = r'(悬赏令结算|道友现在什么都没干呢)'
command_js_ture = on_regex(pattern=js_ture_pattern, flags=re.I, permission=GROUP, rule=to_me(), priority=100)
command_js_false = on_keyword({'进行中的悬赏令'}, rule=to_me(), priority=100, block=True)
js_error_pattern = r'(道友现在在闭关呢|小心走火入魔)'
command_js_error = on_regex(pattern=js_error_pattern, flags=re.I, permission=GROUP, priority=100, rule=to_me())


@command_js_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, xsl_js_monitor):
        return
    xsl_js_monitor('done')


@command_js_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, xsl_js_monitor):
        return

    pattern = r'预计(\d+\.\d+)(分钟)后可结束'
    match = re.search(pattern, str(msg))
    time, unit = float(match.group(1)), match.group(2).strip()
    if unit == '分钟':
        time *= 60

    xsl_js_monitor.set_time(time)
    xsl_js_monitor('regular')


@command_js_error.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, xsl_js_monitor):
        return
    xsl_js_monitor('exit')


async def __task_js(_cmd, _event):
    """悬赏令结算"""
    timing(msg='悬赏令结算')
    xsl_js_monitor('init')
    loop = LoopEvent(_event, name='xsl_js_loop')

    went_await = loop.add(loop.loop_await_cmd('xsl js', monitor=xsl_js_monitor))
    went_send = loop.add(loop.loop_send_cmd('xsl js', cmd=_cmd, msg=Message__js))

    await went_await
    await went_send

    return xsl_js_monitor


"""悬赏令 接取"""

xsl_jq_monitor = Monitor(name='悬赏令接取监控')

command_jq_ture = on_keyword({'接取任务'}, rule=to_me(), priority=100, block=True)
command_jq_false = on_keyword({'道友现在在做悬赏令呢'}, rule=to_me(), priority=100, block=True)


@command_jq_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, xsl_jq_monitor):
        return
    xsl_jq_monitor('done')


@command_jq_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, xsl_jq_monitor):
        return
    xsl_jq_monitor('error')


async def __task_jq(_cmd, _event, _task):
    """悬赏令接取"""
    timing(msg='悬赏令接取')

    _task_id, _task_time, _ = xsl_get_target(_task)
    _reply = xxBot.msg__at_xxbot + Message(f'悬赏令接取 {_task_id}')

    # 处理悬赏接取
    xsl_jq_monitor('init', start=True)

    if timing.check('is_exit'):
        xsl_jq_monitor('exit')
    else:
        loop = LoopEvent(_event, name='xsl_jq_loop')

        went_await = loop.add(loop.loop_await_cmd('xsl js', monitor=xsl_jq_monitor))
        went_send = loop.add(loop.loop_send_cmd('xsl js', cmd=_cmd, msg=_reply))

        await went_await
        await went_send

        xsl_jq_monitor.set_time(_task_time)
    return xsl_jq_monitor
