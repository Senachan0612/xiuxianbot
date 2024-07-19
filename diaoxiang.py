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

timing = xxbot['dx_timing']
monitor = Monitor(name='雕像监控', start=True)

"""雕像"""

command = on_command("雕像", aliases={"雕像", "dx"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭雕像", aliases={"!雕像", "!dx"}, rule=to_me(), priority=60, block=True)

task_finish_pattern = r'(神秘的环奈显灵了|道友今天已经叩拜过了)'
command_ture_task_finish = on_regex(pattern=task_finish_pattern, flags=re.I, permission=GROUP)

"""成功"""


def get_regular_time(_next=False):
    """获得本日定时"""
    now_dt = datetime.datetime.now()
    # 凌晨23:30执行
    next_dt = now_dt.replace(hour=23, minute=30, second=0, microsecond=0) + relativedelta(days=_next and 1 or 0)
    time = (next_dt - now_dt).seconds
    return now_dt, next_dt, time


@command_ture_task_finish.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if api_check_task__exec_by_bot_at(event):
        return

    now_dt, next_dt, time = get_regular_time()

    timing('regular', msg='定时任务')
    timing.set_time(time)
    monitor('regular')


""""core"""


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_config(event, at_me=True):
        return

    # 启动
    if not timing.check('is_usable'):
        return
    timing('start')

    reply = Message(f"[CQ:at,qq={BotId}]") + Message(f" 叩拜雕像")

    # 加载异步监听
    loop = LoopEvent(event)

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        now_dt, next_dt, time = get_regular_time()
        if time >= 5 * 60:
            timing.set_time(time)
            timing('waiting')
            await timing.sleep()
            continue

        went_await = loop.add(loop.loop_await_cmd('雕像', monitor=monitor))
        went_send = loop.add(loop.loop_send_cmd('雕像', cmd=command, msg=reply))

        # 执行监听
        timing('running')
        monitor('init')
        await went_await
        await went_send

        # 执行等待
        if timing.check('is_finish'):
            break

        if timing.check('is_regular'):
            await asyncio.sleep(timing.time)
            continue

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    api_update_state__by_at(event, timing, state={
        'state': 'done',
        'msg': '手动结束',
    })
