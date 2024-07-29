"""收草功能"""

import re

from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword, fullmatch

from . import (
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""收草"""

# 注册监控器
timing = Monitor(name='收草')
_command = ('收草', 'sc')
command = on_command("收草", aliases=set(_command), rule=fullmatch(_command), priority=60, block=True)
_exit_command = ('关闭收草', '!收草', '!sc')
exit_command = on_command("关闭收草", aliases=set(_exit_command), rule=fullmatch(_exit_command), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '收草': {
        'timing': timing,
        'cmd': command,
        'auto': True,
    },
})

monitor = Monitor(name='收草监控')
Message__sc = xxBot.msg__at_xxbot + Message(f"灵田收取")


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
        timing('running', msg='正在收取')
        monitor('init')

        went_await = loop.add(loop.loop_await_cmd('sc', monitor=monitor))
        went_send = loop.add(loop.loop_send_cmd('sc', cmd=command, msg=Message__sc))

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

        timing('regular', msg=timing.dt_string(timing.exec_time))
        await timing.sleep()

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'exit',
        'msg': '手动结束',
    })


"""收草成功"""
sc_command_success = on_command("", aliases={""}, rule=keyword('成功收获'), priority=100, block=True)


@sc_command_success.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    monitor.set_time(xxBot['CD_ShouCao', 24 * 60 * 60])
    monitor('done')


"""收草失败"""
sc_command_false = on_command("", aliases={""}, rule=keyword('还不能收取'), priority=100, block=True)


@sc_command_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    pattern = r'：([\d.]+)(\D+)之后'
    match = re.search(pattern, str(msg))
    time, unit = float(match.group(1)), match.group(2).strip()

    if unit == '小时':
        time *= 60 * 60 + 60

    monitor.set_time(time)
    monitor('done')
