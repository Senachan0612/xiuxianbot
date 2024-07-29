"""突破功能"""

import re

from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword, fullmatch

from . import (
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""突破"""

# 注册监控器
timing = Monitor(name='突破')
_command = ('突破', 'tp')
command = on_command('突破', aliases=set(_command), rule=fullmatch(_command), priority=60, block=True)
_exit_command = ('关闭突破', '!突破', '!tp')
exit_command = on_command('关闭突破', aliases=set(_exit_command), rule=fullmatch(_exit_command), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '突破': {
        'timing': timing,
        'cmd': command,
        'auto': False,
    },
})

monitor = Monitor(name='突破监控')
Message__tp = xxBot.msg__at_xxbot + Message('突破')
Message__tp_sy = xxBot.msg__at_xxbot + Message('突破使用')


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 启动
    if not timing('start'):
        return

    # 加载异步监听
    loop = LoopEvent(event)

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        # 执行监听
        timing('running', msg='正在突破')
        monitor('init')

        if xxBot.get_config('is_use_due') and xxBot.get_config('is_auto_use_due'):
            send_msg = Message__tp_sy
        else:
            send_msg = Message__tp

        went_await = loop.add(loop.loop_await_cmd('tupo', monitor=monitor))
        went_send = loop.add(loop.loop_send_cmd('tupo', cmd=command, msg=send_msg))

        await went_await
        await went_send

        if timing.check('is_finish'):
            break

        if monitor.check('is_pause'):
            # 暂停状态 等待状态解除
            timing('pause', msg=monitor.msg)
            await loop.add(loop.loop_pause_cmd('pause tupo', monitor=timing))
            continue
        elif monitor.check('is_exit'):
            timing('exit', msg=monitor.msg)
            continue

        # 执行等待
        timing.set_time(monitor.time)
        timing('regular', msg=timing.dt_string(timing.exec_time))
        await timing.sleep()

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'exit',
        'msg': '手动结束',
    })


"""突破成功"""

_task_tp_ture_pattern = r'(恭喜道友突破|道友突破失败)'
command_tp_ture = on_regex(pattern=_task_tp_ture_pattern, flags=re.I, permission=GROUP)


@command_tp_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    monitor.set_time(xxBot['CD_TuPo', 1 * 30 * 60])
    monitor('done')


"""突破失败"""

command_tp_false_no_hp = on_command('', rule=keyword('道友状态不佳，无法突破'), priority=100, block=True)
command_tp_false_no_exp = on_command('', rule=keyword('道友的修为不足以突破'), priority=100, block=True)
command_tp_false_no_due = on_command('', rule=keyword('你没有丹药'), priority=100, block=True)
command_tp_false_no_count = on_command('', rule=keyword('超过今日上限，道友莫要心急，请先巩固境界'), priority=100, block=True)

command_tp_false_no_time = on_command('', rule=keyword('目前无法突破'), priority=100, block=True)

command_tp_false = on_command('', rule=keyword('道友已是最高境界'), priority=100, block=True)


@command_tp_false_no_hp.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('pause', msg='状态异常')


@command_tp_false_no_exp.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('pause', msg='修为不足')


@command_tp_false_no_due.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('pause', msg='渡厄丹不足')


@command_tp_false_no_count.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('pause', msg='突破上限')


@command_tp_false_no_time.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    pattern = r'还需要([\d.]+)(\D+)$'
    match = re.search(pattern, str(msg))
    time, unit = float(match.group(1)), match.group(2).strip()

    if unit == '分钟':
        time = time * 60 + 60

    monitor('regular')
    monitor.set_time(time)


@command_tp_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('exit', msg='已达最高境界')
