from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
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
from . import xxbot

timing = xxbot['tp_timing']
monitor = Monitor(name='突破监控', start=True)

"""突破"""

command = on_command("突破", aliases={"突破", "tp"}, rule=to_me(), priority=60, block=True)
exit_command = on_command("关闭突破", aliases={"!突破", "!tp"}, rule=to_me(), priority=60, block=True)

ture_task_finish_pattern = r'(恭喜道友突破|道友突破失败|你没有丹药)'
command_ture_task_finish = on_regex(pattern=ture_task_finish_pattern, flags=re.I, permission=GROUP)

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


@command_ture_task_finish.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if _monitor_command_check(event):
        return

    if '你没有丹药' in str(msg):
        xxbot.is_use_due = False

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

        reply = reply_02 if xxbot.is_use_due else reply_01
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
