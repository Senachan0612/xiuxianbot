"""叩拜雕像功能"""

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

"""雕像"""

# 注册监控器
timing = Monitor(name='叩拜雕像')

_command = ('叩拜雕像', 'kbdx')
command = on_command("收草", aliases=set(_command), rule=fullmatch(_command), priority=60, block=True)
_exit_command = ('关闭叩拜雕像', '!叩拜雕像', '!kbdx')
exit_command = on_command("关闭收草", aliases=set(_exit_command), rule=fullmatch(_exit_command), priority=60, block=True)

# 添加自启动
xxBot.load_apps({
    '叩拜雕像': {
        'timing': timing,
        'cmd': command,
        'auto': True,
    },
})

monitor = Monitor(name='叩拜雕像监控')
Message__kbdx = xxBot.msg__at_xxbot + Message('叩拜雕像')


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 启动
    if not timing('start'):
        return

    # 校验执行时间
    _, _, time = xxBot.get_regular_time('Regular_KouBaiDiaoXiang', default=[23, 30], days=0)
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
        went_send = loop.add(loop.loop_send_cmd('dy lq', cmd=command, msg=Message__kbdx))

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


"""雕像叩拜"""

task_finish_pattern = r'(神秘的环奈显灵了|道友今天已经叩拜过了)'
command_dx_kb_ture = on_regex(pattern=task_finish_pattern, flags=re.I, permission=GROUP)


@command_dx_kb_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    _, _, time = xxBot.get_regular_time('Regular_KouBaiDiaoXiang', default=[23, 30], days=1)

    monitor('regular')
    monitor.set_time(time)
