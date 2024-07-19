from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword, endswith

import re
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

timing = xxbot['gz_timing']
monitor = Monitor(name='复读监控', start=True)

"""灌注"""

command_manual = on_command("复读", aliases={"复读", "复读模式", "fd"}, rule=to_me(), priority=60, block=True)
exit_command_manual = on_command("关闭复读", aliases={"!复读", "!复读模式", "!fd"}, rule=to_me(), priority=60, block=True)
command_monitor = on_command("", aliases={""}, rule=endswith(' '), priority=60, block=True)


@command_manual.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_config(event, at_me=True):
        return

    # 启动
    if not timing.check('is_usable'):
        return

    uid = event.user_id
    AtUser = Message(f"[CQ:at,qq={uid}] ")

    timing('start', '正在复读')
    await command_manual.send(AtUser + Message('复读模式已启动！开始复读任意 (空格)结尾命令'))

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        await asyncio.sleep(5)

    timing('init')
    await command_manual.send(AtUser + Message('复读模式关闭！'))


AtBot = Message(f"[CQ:at,qq={BotId}] ")


@command_monitor.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not timing.check('is_normal'):
        return
    if event.to_me:
        return
    if event.group_id not in GroupIds:
        return
    if event.user_id not in ManagerIds:
        return

    await command_monitor.send(AtBot + Message(msg))


@exit_command_manual.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    api_update_state__by_at(event, timing, state={
        'state': 'done',
        'msg': '手动结束',
    })

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
