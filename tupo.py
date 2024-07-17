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
from . import tp_monitor as monitor
from . import tp_timing as timing

"""突破"""

command = on_command("突破", aliases={"突破", "tp"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭突破", aliases={"!突破", "!tp"}, rule=to_me(), priority=60, block=True)

command_ture_success = on_command("", aliases={""}, rule=keyword('恭喜道友突破'), priority=100, block=True)
command_ture_fail = on_command("", aliases={""}, rule=keyword('道友突破失败'), priority=100, block=True)
# @意 道友突破失败，修为减少551。同时获得神秘的环奈祝福，下次突破成功率增加11道友不要放弃！

command_false_time = on_command("", aliases={""}, rule=keyword('目前无法突破'), priority=100, block=True)
command_false_exp = on_command("", aliases={""}, rule=keyword('道友的修为不足以突破'), priority=100, block=True)
command_false_hp = on_command("", aliases={""}, rule=keyword('道友状态不佳，无法突破'), priority=100, block=True)


def _monitor_command_check(event):
    if not timing.check('is_mutual'):
        return True
    if monitor.check('is_finish'):
        return True
    if not api_check_config(event, bot_event=True, at_me=True):
        return True


"""成功"""


@command_ture_success.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return

    msg_str = str(msg)
    # @金魚 恭喜道友突破练气境初期成功
    pattern = r'突破(\D+)成功'
    match = re.search(pattern, msg_str)

    # todo 吃药
    level = match.group(1).strip()

    monitor.set_time(timing.default_time)
    monitor('done')


@command_ture_fail.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return

    monitor.set_time(timing.default_time)
    monitor('done')


"""失败"""


@command_false_time.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return

    msg_str = str(msg)
    # @金魚 目前无法突破，还需要9分钟
    pattern = r'还需要([\d.]+)(\D+)$'
    match = re.search(pattern, msg_str)
    time, unit = float(match.group(1)), match.group(2).strip()

    if unit == '分钟':
        time = time * 60 + 60

    monitor.set_time(time)
    monitor('done')


@command_false_exp.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return

    # 道友的修为不足以突破！距离下次突破需要598065修为！突破境界为：金仙境初期
    monitor('pause')


@command_false_hp.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return
    # @永乐大帝 道友状态不佳，无法突破！(气血不足)
    monitor('pause')


"""core"""


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not api_check_config(event, at_me=True):
        return

    # 启动
    if not timing.check('is_usable'):
        return
    timing('start')

    reply_01 = Message(f"[CQ:at,qq={BotId}]") + Message(f" 突破")
    reply_02 = Message(f"[CQ:at,qq={BotId}]") + Message(f" 突破使用")

    # 加载异步监听
    loop = LoopEvent(event, name='tp_loop')

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        went_await = loop.add(loop.loop_await_cmd('tupo', monitor=monitor))

        reply = True and reply_01 or reply_02
        went_send = loop.add(loop.loop_send_cmd('tupo', cmd=command, msg=reply))

        # 执行监听
        timing('running')
        monitor('init')
        await went_await
        await went_send

        if monitor.check('is_pause'):
            # 暂停状态 等待状态解除
            timing('pause')
            await loop.add(loop.loop_pause_cmd('pause tupo', monitor=timing))
            continue
        elif monitor.check('is_done'):
            # 正常监听结束 设置等待时间
            timing.set_time(monitor.time)
        else:
            timing.set_time()

        if timing.check('is_finish'):
            break
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
