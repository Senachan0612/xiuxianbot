"""服务 突破丹"""

import re
import asyncio

from nonebot.plugin.on import on_startswith, on_regex
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

DefaultUseDueCode = '渡劫境中期'

"""突破丹"""

# 注册服务
service = Service(
    style='Service',
    name='突破丹',
)
timing = service.timing

"""服用丹药"""

monitor = Monitor(name='服用丹药监控')
command_fydy = sc_command_success = on_startswith({'恭喜道友突破'}, rule=to_me(), priority=100)

tp_task = xxBot.get_task('突破')


def set_tp_due_msg(is_use):
    """设置突破是否使用渡厄丹"""
    if is_use and str(tp_task.msg[-1]) != '使用':
        tp_task.msg += Message('使用')
    elif not is_use and str(tp_task.msg[-1]) == '使用':
        tp_task.msg.pop()


tp_use_msg = xxBot.msg__at_xxbot + Message('突破')
tp_no_use_msg = tp_use_msg + Message('使用')


@command_fydy.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    timing(msg='开始服用突破丹')

    # 境界
    code, = re.search(r'突破(\D+)成功', str(event.message)).groups()
    df_tp = UserData['tupo']
    code_df = df_tp[df_tp['code'] == code]

    if not code_df.empty:
        """渡厄丹"""
        is_use = False
        if xxBot.get_config('is_use_due'):
            df_tp = UserData['tupo']
            auto_code = xxBot.get_config('auto_use_due_code', DefaultUseDueCode)

            auto_code_index = df_tp[df_tp['code'] == auto_code].index.min() or float('inf')
            code_index = code_df.index.min() or 0
            is_use = auto_code_index <= code_index

        set_tp_due_msg(is_use)

        """突破丹"""
        for _, tp_drug in code_df.iterrows():
            monitor('init')
            _, name, count = tp_drug
            timing(msg='开始服用突破丹')

            for _ in range(int(count)):
                if monitor.check('is_break'):
                    break

                await command_fydy.send(xxBot.msg__at_xxbot + Message(f'服用丹药 {name}'))
                await asyncio.sleep(5)

    monitor('init')
    timing(msg=f'已服用{code}突破丹药')


"""服用突破丹 失败"""

fydy_false_pattern = r'(道友没有该丹药|道友不满足使用条件)'
command_fydy_false = on_regex(pattern=fydy_false_pattern, flags=re.I, permission=GROUP, rule=to_me(), priority=100)


@command_fydy_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('skip')


"""使用渡厄丹"""

DuEDanNamePattern = '渡厄丹|肚饿丹'
ExeCommandTruePattern = '使用|启用'
ExeCommandFalsePattern = '禁用|停用'
ExeTypePattern = '立刻'
command_use_due_pattern = (
    fr'^({DuEDanNamePattern})\s*({ExeTypePattern}\s*)?({ExeCommandTruePattern}|{ExeCommandFalsePattern})'
    fr'|\s*({ExeTypePattern}\s*)?({ExeCommandTruePattern}|{ExeCommandFalsePattern})\s*({DuEDanNamePattern})'
)
command_use_due = on_regex(pattern=command_use_due_pattern, flags=re.I, permission=GROUP, rule=to_me(), priority=100)


@command_use_due.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    str_msg = str(event.message)
    df_tp = UserData['tupo']

    # 是否启用
    is_use_due = bool(re.compile(rf'({ExeCommandTruePattern})').search(str_msg))
    # 自动使用境界
    auto_code_pattern = re.compile(rf'({"|".join(df_tp["code"].drop_duplicates())})')
    auto_use_code = auto_code_pattern.findall(str_msg + DefaultUseDueCode)
    # 立刻自动使用
    is_auto_use_due = bool(
        re.compile(rf'({ExeTypePattern}\s*)({ExeCommandTruePattern}|{ExeCommandFalsePattern})').search(str_msg))

    xxBot.set_config('is_use_due', is_use_due)
    xxBot.set_config('auto_use_due_level', auto_use_code[0])

    set_tp_due_msg(is_auto_use_due)

    await command_use_due.finish(Message(f'[CQ:at,qq={event.user_id}] ')
                                 + Message(f'渡厄丹设置成功！\n' + xxBot.print_info('due')))


def due_config_info():
    """肚饿丹相关配置信息"""
    return '肚饿丹配置信息', [
        ['肚饿丹', '启用' if xxBot.get_config('is_use_due') else '禁止', ],
        ['自动使用境界', xxBot.get_config('auto_use_due_level', '渡劫境圆满'), ],
    ]


xxBot.load_info('due', due_config_info)
