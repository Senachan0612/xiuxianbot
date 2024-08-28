"""计时任务 灵田收取"""

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

"""灵田收取"""

# 有效反馈
success_tuple = ('道友成功收获药材：',)
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册计时任务
cron = Cron(
    style='CD',
    name='灵田收取',
    msg=xxBot.msg__at_xxbot + Message('灵田收取'),
    feedback_cmd=command_success,
)

timing, monitor = cron.timing, cron.monitor
# 无效反馈
false_tuple = ('道友的灵田还不能收取，下次收取时间为：',)
command_false = on_startswith(false_tuple, rule=to_me(), priority=100, block=True)


@command_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    pattern = r'：([\d.]+)(\D+)之后'
    match = re.search(pattern, str(event.message))
    time, unit = float(match.group(1)), match.group(2).strip()

    if unit == '小时':
        time *= 60 * 60 + 60

    monitor.set_time(time)
    monitor('regular')
