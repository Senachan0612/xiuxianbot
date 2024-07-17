from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword

import re

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
from . import sc_monitor as monitor
from . import sc_timing as timing

"""收草"""

command = on_command("收草", aliases={"收草", "sc"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭收草", aliases={"!收草", "!sc"}, rule=to_me(), priority=60, block=True)

sc_command_success = on_command("", aliases={""}, rule=keyword('成功收获'), priority=100, block=True)

sc_command_false = on_command("", aliases={""}, rule=keyword('还不能收取'), priority=100, block=True)


def _monitor_command_check(event):
    if not timing.check('is_normal'):
        return True
    if monitor.check('is_finish'):
        return True
    if not api_check_config(event, bot_event=True, at_me=True):
        return True


"""成功"""


@sc_command_success.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return

    monitor.set_time(timing.default_time)
    monitor('done')


"""失败"""


@sc_command_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return

    msg_str = str(msg)

    pattern = r'：([\d.]+)(\D+)之后'
    match = re.search(pattern, msg_str)
    time, unit = float(match.group(1)), match.group(2).strip()

    if unit == '小时':
        time *= 60 * 60

    monitor.set_time(time)
    monitor('done')


"""core"""


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_config(event, at_me=True):
        return

    # 启动
    if not timing.check('is_usable'):
        return
    timing('start')

    reply = Message(f"[CQ:at,qq={BotId}]") + Message(f" 灵田收取")

    # 加载异步监听
    loop = LoopEvent(event)

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        went_await = loop.add(loop.loop_await_cmd('shoucao', monitor=monitor))
        went_send = loop.add(loop.loop_send_cmd('shoucao', cmd=command, msg=reply))

        # 执行监听
        timing('running')
        monitor('init')
        await went_await
        await went_send

        if monitor.check('is_done'):
            # 循环等待
            timing.set_time(monitor.time)
        else:
            timing.set_time()

        # 执行等待
        if timing.check('is_finish'):
            break
        timing('waiting', msg='程序睡眠')
        await timing.sleep()

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    api_update_state__by_at(event, timing, state={
        'state': 'done',
        'msg': '手动结束',
    })
