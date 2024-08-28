"""服务 复读"""

import asyncio
import os
import json
import re

from nonebot.plugin.on import on_regex, on_fullmatch, on_startswith, on_message
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    UserData,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
    Service,
)

"""复读"""

# 注册服务
service = Service(
    style='Service',
    name='复读',
)
timing = service.timing

"""执行复读"""

df_fd = UserData['fudu']
fd_pattern = r'(%s)' % '|'.join(df_fd[0])
command_fd = on_message(rule=to_me(), priority=1000)


@command_fd.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not timing.check('is_normal'):
        return
    if not eventCheck.api_check__event(event, at_me=True):
        return

    # 获取内容 次数
    fd_msg, fd_count = (re.split(r'\s*\*+\s*', str(event.message)) + [0])[:2]

    aliases_reply = xxBot.get_config('fudu_aliases_dict', default={}).get(fd_msg.strip())
    if aliases_reply:
        aliases_reply = Message(aliases_reply)
    elif re.compile(fd_pattern).match(fd_msg):
        aliases_reply = fd_msg
    else:
        return

    fd_count = int(fd_count or 0) or 1
    while fd_count:
        await command_fd.send(xxBot.msg__at_xxbot + aliases_reply)
        await asyncio.sleep(1)

        fd_count -= 1


"""复读别名"""

_command_aliases_set = ('设置复读', '添加复读', '设置别名', '添加别名')
command_aliases_set = on_startswith(_command_aliases_set, rule=to_me(), priority=60, block=True)


@command_aliases_set.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__event(event, at_me=True):
        return

    match = re.compile(rf'({"|".join(_command_aliases_set)})\s+(\S+)(?:\s*:\s*(.*))?').match(str(event.message))
    if not match:
        await command_aliases_set.finish(
            xxBot.msg__at(event.user_id) +
            Message(f'复读别名设置失败！设置公式：\n(设置|添加)(复读|别名) key : val)\nval为空视为移除别名！')
        )

    _, key, val = match.groups()

    fudu_aliases_dict = xxBot.get_config('fudu_aliases_dict', default={})
    if val:
        fudu_aliases_dict[key] = val
    else:
        fudu_aliases_dict.pop(key, val)

    await command_aliases_set.finish(
        xxBot.msg__at(event.user_id) + Message(f'复读别名设置成功！\n')
        + xxBot.print_info('fudu_aliases')
    )


"""日志"""


def fudu_aliases_config_info():
    """肚饿丹相关配置信息"""
    return '复读别名配置信息', list(xxBot.get_config('fudu_aliases_dict', default={}).items())


xxBot.load_info('fudu_aliases', fudu_aliases_config_info)
