"""bot管理"""

import re
import asyncio

import nonebot
from nonebot.plugin.on import on_command, on_shell_command, on_regex
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me, keyword, fullmatch, startswith
from nonebot.rule import TrieRule

from . import (
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

# bot成功连接后自动调用函数钩子
on_bot_connect = nonebot.get_driver().on_bot_connect

admin_event = eventCheck.api_check__app_event


async def super_admin_event(_event, _cmd=False):
    """超管校验"""
    if eventCheck.api_check__app_super_event(_event):
        return True

    if _cmd:
        at_user = Message(f"[CQ:at,qq={_event.user_id}] ")
        await _cmd.finish(at_user + Message('功能仅允许超管执行！'))


"""应用自启动"""


@on_bot_connect
async def auto_exec_command():
    """功能自启"""
    bot = xxBot.bot

    auto_events = []
    for name, (_, matcher, _, msg, at_bot) in xxBot.apps.items():
        if not xxBot.auto_apps.get(name):
            continue

        event = GroupMessageEvent(
            time=0,
            self_id=bot.self_id,
            post_type="message",
            sub_type="normal",
            user_id=xxBot.SuperManagerIds[0],
            group_id=xxBot.GroupIds[0],
            message_type="group",
            message_id=-1,
            message=msg,
            raw_message=str(msg),
            font=0,
            sender={},
            to_me=bool(at_bot)
        )

        auto_events.append(matcher().run(
            bot=bot,
            event=event,
            state={'_prefix': TrieRule.get_value(bot, event, {}), },
            stack=None,
            dependency_cache=None,
        ))

    for event in auto_events:
        await event


"""查看xxbot信息"""

_cmd_status = ('修仙状态', '修仙信息', 'xxzt', 'xxxx')
cmd_status = on_command('修仙信息', aliases=set(_cmd_status), rule=fullmatch(_cmd_status), priority=60, block=True)


@cmd_status.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not admin_event(event):
        return

    msg = xxBot.status()
    await cmd_status.send(msg)


"""设置应用自启动"""
# cmd_set_auto_app = on_command('设置自启', aliases=set(_cmd_status), rule=fullmatch(_cmd_status), priority=60, block=True)
#
#
# @cmd_set_auto_app.handle()
# async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
#     at_user = Message(f"[CQ:at,qq={event.user_id}] ")
#     if not super_admin_event(event):
#         await cmd_set_auto_app.finish(at_user + Message('设置应用自启动仅允许超管执行！'))
#
#     """"""

"""授权"""

cmd_set_config__security = on_command('', rule=startswith(msg=('设置授权', '取消授权')), priority=60, block=True)


@cmd_set_config__security.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not await super_admin_event(event, cmd_set_config__security):
        return

    at_user = Message(f"[CQ:at,qq={event.user_id}] ")

    # 获取授权信息
    pattern = re.compile(r'(设置授权|取消授权)?\s*(用户|群组|超管)?[\s,]*(\d+[\s,]*)+', re.DOTALL)
    match = pattern.search(str(msg))

    try:
        operate = match.group(1)
        tag = match.group(2)
        nums = set(int(n) for n in re.findall(r'\d+', match.group(3)))
    except Exception:
        operate, tag, nums = '', '', []

    if not (operate and tag and nums):
        await cmd_set_config__security.finish(
            at_user + Message(f'{operate}命令执行异常！')
            + Message(f'\n命令模板：(设置授权|取消授权) (用户|群组|超管) 1111, 2222, ...')
            + Message(f'\n异常命令解析：设置授权 {tag} {nums}')
        )

    security = xxBot.set_security(operate, tag, nums)
    await cmd_set_config__security.finish(
        at_user + Message(f'{operate}命令执行成功！')
        + Message(f'\n当前授权{tag}：')
        + Message('\n' + '\n'.join(str(num) for num in security))
    )


"""同步配置"""
_cmd_set_config__save = ('同步配置', '保存配置')
cmd_set_config__save = on_command(
    '同步配置', aliases=set(_cmd_set_config__save), rule=fullmatch(_cmd_set_config__save), priority=60, block=True)


@cmd_set_config__save.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not await super_admin_event(event, cmd_set_config__save):
        return

    at_user = Message(f"[CQ:at,qq={event.user_id}] ")
    xxBot.save_configs()

    await cmd_set_config__save.finish(
        at_user + Message(f'执行成功，配置已同步！')
    )
