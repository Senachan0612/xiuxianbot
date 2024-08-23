"""收草功能"""

import re

from nonebot.plugin.on import on_fullmatch, on_keyword, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    UserData,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""扫草"""

# 注册监控器
timing = Monitor(name='扫草')
monitor = Monitor(name='坊市监控')

command = on_fullmatch(('扫草',), rule=to_me(), priority=60, block=True)
exit_command = on_fullmatch(('!扫草',), rule=to_me(), priority=60, block=True)


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 启动
    if not timing('start'):
        return

    # 加载异步监听
    loop = LoopEvent(event)

    page_list = ['']

    """监听"""
    while page_list:
        if not page_list:
            # 首次 生成页码
            ...

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


get_fs_pattern = r'当前(d+)页，共(d+)页'
command_get_fs_status = on_regex(get_fs_pattern, permission=GROUP, priority=1000, block=True)


@command_get_fs_status.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not monitor.check('is_normal'):
        return

    str_msg = str(event.message)
    # todo 未知原因 此处name仅能做模糊查询
    user = re.compile(get_zb_pattern).match(str_msg).groups()[0]
    if gz_config.solve_user and not user.endswith(str(gz_config.solve_user)):
        return
    elif gz_config.solve_user == '':
        if not eventCheck.api_check__xxbot_event(event):
            return
        gz_config.solve_user = user

    if gz_config.solve__get_zb(str_msg):
        monitor('done')
