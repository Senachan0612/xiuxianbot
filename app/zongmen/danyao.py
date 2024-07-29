"""宗门丹药功能"""

import re
import asyncio
import datetime
from collections import namedtuple

from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword, fullmatch

from . import (
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""宗门丹药"""

# 注册监控器
timing = Monitor(name='宗门丹药')
_command = ('宗门丹药', 'zmdy')
command = on_command('宗门丹药', aliases=set(_command), rule=fullmatch(_command), priority=60, block=True)
_exit_command = ('关闭宗门丹药', '!宗门丹药', '!zmdy')
exit_command = on_command('关闭宗门丹药', aliases=set(_exit_command), rule=fullmatch(_exit_command), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '宗门丹药': {
        'timing': timing,
        'cmd': command,
        'auto': True,
    },
})

monitor = Monitor(name='宗门丹药监控')
Message__lq = xxBot.msg__at_xxbot + Message('宗门丹药领取')


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 启动
    if not timing('start'):
        return

    # 校验执行时间
    _, _, time = xxBot.get_regular_time('Regular_ZongMenDanYao', default=[23, 30], days=0)
    if time > 0:
        timing.set_time(time)
        timing('regular', msg=timing.dt_string(timing.exec_time))

    # 加载异步监听
    loop = LoopEvent(event)

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        if timing.check('is_regular'):
            await timing.sleep()

        went_await = loop.add(loop.loop_await_cmd('dy lq', monitor=monitor))
        went_send = loop.add(loop.loop_send_cmd('dy lq', cmd=command, msg=Message__lq))

        # 执行监听
        timing('running')
        monitor('init')
        await went_await
        await went_send

        if monitor.check('is_regular'):
            timing.set_time(monitor.time)
            timing('regular', msg=timing.dt_string(timing.exec_time))

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'exit',
        'msg': '手动结束',
    })


"""宗门丹药领取"""

task_finish_pattern = r'(道友成功领取到丹药|道友已经领取过了，不要贪心哦)'
command_zmdy_lq_ture = on_regex(pattern=task_finish_pattern, flags=re.I, permission=GROUP)


@command_zmdy_lq_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    _, _, time = xxBot.get_regular_time('Regular_ZongMenDanYao', default=[23, 30], days=1)

    monitor('regular')
    monitor.set_time(time)
