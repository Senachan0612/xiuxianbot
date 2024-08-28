"""计时任务 突破"""

import re

from nonebot.plugin.on import on_startswith
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    xxBot,
    eventCheck,
    Cron,
)

"""突破"""

# 有效反馈
success_tuple = ('恭喜道友突破', '道友突破失败，')
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册计时任务
cron = Cron(
    style='CD',
    name='突破',
    msg=xxBot.msg__at_xxbot + Message('突破'),
    feedback_cmd=command_success,
)

timing, monitor = cron.timing, cron.monitor

# 无效反馈
false_tuple = (
    '道友状态不佳，无法突破！',
    '道友的修为不足以突破！',
    '你没有丹药！',
    '超过今日上限，道友莫要心急，请先巩固境界。',
    '道友已是最高境界，无法突破！',
)
command_false = on_startswith(false_tuple, rule=to_me(), priority=100, block=True)


@command_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('pause', msg=str(event.message[-1]))


# 无效反馈 - 时间
false_cd_tuple = ('目前无法突破，还需要',)
command_false_cd = on_startswith(false_cd_tuple, rule=to_me(), priority=100, block=True)


@command_false_cd.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    pattern = r'还需要([\d.]+)(\D+)$'
    match = re.search(pattern, str(event.message))
    time, unit = float(match.group(1)), match.group(2).strip()

    if unit == '分钟':
        time = time * 60 + 60

    monitor('regular')
    monitor.set_time(time)


# 无效反馈 - 至高
false_end_tuple = ('道友已是最高境界，无法突破！',)
command_false_end = on_startswith(false_end_tuple, rule=to_me(), priority=100, block=True)


@command_false_end.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return
    monitor('exit', msg='已达最高境界')
