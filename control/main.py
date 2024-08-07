"""bot管理"""

import re
import asyncio
from collections import namedtuple

import nonebot
from nonebot.plugin.on import on_fullmatch, on_startswith, on_regex
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

    def _func():
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
                raw_message=str(event.message),
                font=0,
                sender={},
                to_me=bool(at_bot)
            )

            yield matcher().run(
                bot=bot,
                event=event,
                state={'_prefix': TrieRule.get_value(bot, event, {}), },
                stack=None,
                dependency_cache=None,
            )

    await asyncio.gather(*_func())


"""查看xxbot信息"""

_cmd_status = ('修仙状态', '修仙信息', 'xxzt', 'xxxx')
cmd_status = on_fullmatch(_cmd_status, rule=to_me(), priority=60, block=True)


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

_cmd_cmd_set_config__security = ('设置授权', '取消授权')
cmd_set_config__security = on_startswith(_cmd_cmd_set_config__security, rule=to_me(), priority=60, block=True)


@cmd_set_config__security.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not await super_admin_event(event, cmd_set_config__security):
        return

    at_user = Message(f"[CQ:at,qq={event.user_id}] ")

    # 获取授权信息
    pattern = re.compile(r'(设置授权|取消授权)?\s*(用户|群组|超管)?[\s,]*(\d+[\s,]*)+', re.DOTALL)
    match = pattern.search(str(event.message))

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
cmd_set_config__save = on_fullmatch(_cmd_set_config__save, rule=to_me(), priority=60, block=True)


@cmd_set_config__save.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not await super_admin_event(event, cmd_set_config__save):
        return

    at_user = Message(f"[CQ:at,qq={event.user_id}] ")
    xxBot.save_configs()

    await cmd_set_config__save.finish(
        at_user + Message(f'执行成功，配置已同步！')
    )


"""修改配置"""
_cmd_set_config__update = ('修改配置', '修改参数', '设置参数')
_cmd_set_config__update_pattern = rf'({"|".join(_cmd_set_config__update)})\s*(\S*)\s*:\s*(.*)'
cmd_set_config__update = on_regex(_cmd_set_config__update_pattern, rule=to_me(), priority=60, block=True)
_cmd_set_config__update_help = ('配置帮助', '参数帮助', '配置help', '参数help', '配置?', '参数?')
cmd_set_config__update_help = on_fullmatch(_cmd_set_config__update_help, rule=to_me(), priority=60, block=True)


# 配置映射字典
def print_local_config(_config):
    """输出配置信息"""
    return xxBot[_config["key"]]


Config__CD = {
    'print': '单位：秒',
    'func': lambda value: int(eval(value))
}
Config__Regular = {
    'print': '[时, 分]',
    'func': lambda value: [int(x) for x in eval(value)[:2]]
}

ConfigMap = {
    # CD
    '收草': {
        'key': 'CD_ShouCao',
        'val': Config__CD,
    },
    '出闭关': {
        'key': 'CD_ChuBiGuan',
        'val': Config__CD,
    },
    '突破': {
        'key': 'CD_TuPo',
        'val': Config__CD,
    },
    '宗门任务刷新': {
        'key': 'CD_ZongMenRenWu_ShuaXin',
        'val': Config__CD,
    },
    '宗门任务完成': {
        'key': 'CD_ZongMenRenWu_WanChen',
        'val': Config__CD,
    },
    # Regular
    '宗门任务定时': {
        'key': 'Regular_ZongMenRenWu',
        'val': Config__Regular,
    },
    '宗门丹药定时': {
        'key': 'Regular_ZongMenDanYao',
        'val': Config__Regular,
    },
    '叩拜雕像定时': {
        'key': 'Regular_KouBaiDiaoXiang',
        'val': Config__Regular,
    },
    # 其他
    '宗门任务等级': {
        'key': 'ZongMen_Task_Level',
        'val': {
            'print': '[1, 2, 3, 4]',
            'func': lambda value: list({int(x) for x in eval(value)} & {1, 2, 3, 4})
        },
    },
}


@cmd_set_config__update.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not await super_admin_event(event, cmd_set_config__security):
        return

    # 获取配置信息
    _, config_name, config_val = re.compile(_cmd_set_config__update_pattern).search(str(event.message)).groups()
    # 修复[]的转义
    config_val = config_val.replace('&#91;', '[').replace('&#93;', ']')

    def _f():
        config = ConfigMap.get(config_name)
        if not config:
            return '未知参数！发送"配置帮助"获取帮助...'

        key = config['key']
        # 执行更新
        try:
            value = config['val']['func'](config_val)
        except Exception:
            return ('参数解析异常！'
                    f'\n本次：{config_val}'
                    f'\n当前：{print_local_config(config)}')

        xxBot.update_configs({key: value})
        return ('参数更新成功！'
                f'\n当前：{print_local_config(config)}')

    await cmd_set_config__update.finish(xxBot.msg__at(event.user_id) + Message(_f()))


@cmd_set_config__update_help.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not admin_event(event):
        return

    await cmd_set_config__update.finish(xxBot.msg__at(event.user_id) + Message(
        '支持维护的参数列表：\n' +
        '\n'.join(f'{name} : {config["val"]["print"]}；{print_local_config(config)}'
                  for name, config in ConfigMap.items())
    ))
