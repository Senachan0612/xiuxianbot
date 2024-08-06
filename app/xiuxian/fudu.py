"""复读功能"""

import asyncio
import os
import json
import re

from nonebot.plugin.on import on_regex, on_fullmatch, on_startswith, on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    DataPath,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""复读"""

# 注册监控器
timing = Monitor(name='复读')

command = on_fullmatch(('复读', 'fd'), rule=to_me(), priority=50)
exit_command = on_fullmatch(('关闭复读', '!复读', '!fd'), rule=to_me(), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '复读': {
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

    timing('running', msg='正在复读')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'init',
    })


"""执行复读"""

DefaultXiuXianFuDuList = [
    "我的修仙信息",
    "我的存档",
    "重入仙途",
    "我的突破概率",
    "改名",
    "突破",
    "闭关",
    "出关",
    "灵石出关",
    "送灵石",
    "我的状态",
    "我的背包",
    "装备库",
    "供奉物品",
    "灵庄存灵石",
    "灵庄取灵石",
    "灵庄升级会员",
    "灵庄信息",
    "灵庄结算",
    "成为灵庄主",
    "偷灵石",
    "对战记录",
    "抢灵石",
    "切磋",
    "抢劫",
    "强制决斗",
    "我的宗门",
    "升级攻击修炼",
    "宗门任务接取",
    "我的宗门任务",
    "宗门任务完成",
    "宗门任务刷新",
    "宗门功法学习",
    "宗门丹药领取",
    "坊市购买",
    "超市购买",
    "百货购买",
    "坊市上架",
    "装备上架",
    "坊市下架",
    "服用丹药",
    "以身化道",
    "叩拜雕像",
    "悬赏令",
    "悬赏令接取",
    "悬赏令结算",
    "悬赏令刷新",
    "我的杂学造诣",
    "升级收取等级",
    "升级控火等级",
    "灵田收取",
    "学习功法",
    "装备功法",
    "装备道具",
    "卸载辅修功法",
    "卸载主修功法",
    "卸载武器",
    "卸载防具",
    "卸载神通",
    "我的功法",
    "感化首领",
    "讨伐boss",
]

File_Path = r'%s\%s' % (DataPath, 'XiuXianFuDu.json')
try:
    if os.path.isfile(File_Path):
        # 加载用户配置
        with open(File_Path, mode='r', encoding='utf-8') as f:
            XiuXianFuDuList = json.load(f)
    else:
        if not os.path.isdir(DataPath):
            os.makedirs(DataPath)

        with open(File_Path, mode='w', encoding='utf-8') as f:
            json.dump(DefaultXiuXianFuDuList, f, ensure_ascii=False, indent=2)
        XiuXianFuDuList = DefaultXiuXianFuDuList
except Exception:
    XiuXianFuDuList = DefaultXiuXianFuDuList

xiuxian_fudu_pattern = r'(%s)' % '|'.join(DefaultXiuXianFuDuList)
command_fudu = on_message(rule=to_me(), priority=1000, block=True)


@command_fudu.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not timing.check('is_normal'):
        return
    if not eventCheck.api_check__event(event, at_me=True):
        return

    aliases_reply = xxBot.get_config('fudu_aliases_dict', default={}).get(str(msg).strip())
    if aliases_reply:
        aliases_reply = Message(aliases_reply)
    elif re.compile(xiuxian_fudu_pattern).match(str(msg)):
        aliases_reply = msg
    else:
        return

    await command_fudu.send(xxBot.msg__at_xxbot + aliases_reply)


"""复读别名"""

_command_aliases_set = ('设置复读', '添加复读', '设置别名', '添加别名')
command_aliases_set = on_startswith(_command_aliases_set, rule=to_me(), priority=60, block=True)


@command_aliases_set.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__event(event, at_me=True):
        return

    match = re.compile(rf'({"|".join(_command_aliases_set)})\s+(\S+)(?:\s*:\s*(.*))?').match(str(msg))
    if not match:
        await command_aliases_set.finish(
            xxBot.msg__at(event.user_id) +
            Message(f'复读别名设置失败！设置公式：\n(设置|添加)(复读|别名) key : val)\nval为空视为移除别名！')
        )

    _, key, val = match.groups()

    fudu_aliases_dict = xxBot.get_config('fudu_aliases_dict', default={})
    if val:
        fudu_aliases_dict[key] = val
    else:
        fudu_aliases_dict.pop(key, val)

    await command_aliases_set.finish(
        xxBot.msg__at(event.user_id) + Message(f'复读别名设置成功！\n')
        + xxBot.print_info('fudu_aliases')
    )


"""日志"""


def fudu_aliases_config_info():
    """肚饿丹相关配置信息"""
    return '复读别名配置信息', list(xxBot.get_config('fudu_aliases_dict', default={}).items())


xxBot.load_info('fudu_aliases', fudu_aliases_config_info)

# command = on_command("自动灌注", aliases={"自动灌注", "zdgz"}, rule=to_me(), priority=60, block=True)
# exit_command = on_command("关闭自动灌注", aliases={"!自动灌注", "!zdgz"}, rule=to_me(), priority=60, block=True)
#
#
# @command.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     if not api_check_config(event, at_me=True):
#         return
#
#     # 启动
#     if not timing.check('is_usable'):
#         return
#     timing('start')
#
#     _prepare(event, command)
#
#
# """灌注 校验"""
#
# Reply_LSCG = Message(f"[CQ:at,qq={BotId}]") + Message(f" 灵石出关")
# Reply_wdzt = Message(f"[CQ:at,qq={BotId}]") + Message(f" 我的状态")
# check_monitor = Monitor(name='自动灌注 校验监控', start=True)
#
# check_chuguan_pattern = r'(闭关结束|道友现在什么都没干呢)'
# command_check_chuguan = on_regex(pattern=check_chuguan_pattern, flags=re.I, permission=GROUP)
#
#
# def bot_event_monitor_by_start(_event, _monitor):
#     """启动时 监听bot事件"""
#     if not timing.check('is_start'):
#         return True
#     if _monitor.check('is_finish'):
#         return True
#     if not api_check_config(_event, bot_event=True, at_me=True):
#         return True
#
#
# @command_check_chuguan.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     if not bot_event_monitor_by_start(event, check_monitor):
#         return
#     check_monitor('done')
#
#
# def check_fail(_event, _cmd):
#     """校验失败"""
#     await _cmd.send(Message(f"[CQ:at,qq={_event.user_id}]") + Message(f' 自动灌注 {timing.msg} 失败'))
#     timing('done')
#     return True
#
#
# def _prepare(_event, _cmd):
#     """准备工作"""
#     _loop = LoopEvent(_event, name='自动灌注 校验loop')
#     _uid = _event.user_id
#
#     timing(msg='出关校验')
#     went_await = _loop.add(_loop.loop_await_cmd('自动灌注 出关校验', monitor=check_monitor, count=10))
#     went_send = _loop.add(_loop.loop_send_cmd('自动灌注 出关校验', cmd=_cmd, msg=Reply_LSCG))
#     await went_await
#     await went_send
#     if check_monitor.check('is_error'):
#         return check_fail(_event, _cmd)
#
#     timing(msg='状态校验')
#     went_await = _loop.add(_loop.loop_await_cmd('自动灌注 状态校验', monitor=check_monitor))
#     went_send = _loop.add(_loop.loop_send_cmd('自动灌注 状态校验', cmd=_cmd, msg=Reply_LSCG))
