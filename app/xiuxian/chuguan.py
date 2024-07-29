"""出闭关功能"""

import re
import asyncio

from nonebot.plugin.on import on_command, on_shell_command, on_regex, on_keyword
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword, fullmatch

from . import (
    DataPath,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""出闭关"""

# 注册监控器
timing = Monitor(name='出闭关')

'''

re.compile(r'(出闭关|cbg)\s*(\d+)?\s*(\d+)?')

正则取出出闭关|cbg '2020-02-02'的日期

'''

command_pattern = r'(出闭关|cbg)\s*(\d+)?\s*(\d+)?'
command = on_regex(pattern=command_pattern, flags=re.I, permission=GROUP)
_exit_command = ('关闭出闭关', '!出闭关', '!cbg')
exit_command = on_command('关闭出闭关', aliases=set(_exit_command), rule=fullmatch(_exit_command), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '出闭关': {
        'timing': timing,
        'cmd': command,
        'auto': False,
    },
})


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 启动
    if not timing('start'):
        return

    _, time, count = re.compile(command_pattern).match(str(msg)).groups()
    time, count = time or 0, count or float('inf')

    if time:
        timing.set_time(time)
        timing('regular', msg=timing.dt_string(timing.exec_time))

    """监听"""
    while True:
        if timing.check('is_finish'):
            break

        if timing.check('is_regular'):
            await timing.sleep()

        # 执行监听
        timing('running')

        await command.send(xxBot.msg__at_xxbot + Message('灵石出关'))
        await asyncio.sleep(5)
        await command.send(xxBot.msg__at_xxbot + Message('闭关'))

        count -= 1
        if count <= 0:
            timing('done', msg='出闭关次数上限')
            continue

        # 执行等待
        timing.set_time(xxBot['CD_ChuBiGuan', 1 * 60 * 60])
        timing('regular', msg=timing.dt_string(timing.exec_time))

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'exit',
        'msg': '手动结束',
    })


"""结束闭关 激活部分功能"""

command_cg_true = on_keyword({'闭关结束'}, rule=to_me())

UnpauseApps = ['突破', '宗门任务']


@command_cg_true.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing=False, monitor=False):
        return

    for name in UnpauseApps:
        unpause_timing = xxBot.get_timing(name)

        if unpause_timing.check('is_pause'):
            unpause_timing('unpause', msg='出关激活暂停指令')
