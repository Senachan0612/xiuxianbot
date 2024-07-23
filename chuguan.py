from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword

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

timing = xxbot['cg_timing']
monitor = Monitor(name='出关监控', start=True)
pause_tp_timing = xxbot['tp_timing']
pause_zmrw_timing = xxbot['zmrw_timing']

"""出关"""

command = on_command("出关", aliases={"出关", "cg"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭出关", aliases={"!出关", "!cg"}, rule=to_me(), priority=60, block=True)

command_ture_finish = on_command("", aliases={""}, rule=keyword('闭关结束'), priority=100, block=True)


@command_ture_finish.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_task__exec_by_bot_at(event):
        return

    for t in [pause_tp_timing, pause_zmrw_timing]:
        if t.check('is_pause'):
            t('unpause', msg='出关激活暂停指令')


AtBot = Message(f"[CQ:at,qq={BotId}] ")


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
        # 执行监听
        timing('running')

        await command.send(AtBot + Message('灵石出关'))
        await asyncio.sleep(5)
        await command.send(AtBot + Message('闭关'))

        # 执行等待
        timing('waiting')
        await timing.sleep()

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    api_update_state__by_at(event, timing, state={
        'state': 'done',
        'msg': '手动结束',
    })
