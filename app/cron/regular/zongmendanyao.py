"""定时任务 宗门丹药"""

from nonebot.plugin.on import on_startswith
from nonebot.adapters.onebot.v11 import Message
from nonebot.rule import to_me

from . import (
    xxBot,
    Cron,
)

"""宗门丹药"""

# 有效反馈
success_tuple = ('道友成功领取到丹药：', '道友已经领取过了，不要贪心哦~')
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册定时任务
cron = Cron(
    style='Regular',
    name='宗门丹药',
    msg=xxBot.msg__at_xxbot + Message('宗门丹药领取'),
    feedback_cmd=command_success,
)
