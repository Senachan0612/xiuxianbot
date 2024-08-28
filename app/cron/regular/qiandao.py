"""定时任务 签到"""

from nonebot.plugin.on import on_startswith
from nonebot.adapters.onebot.v11 import Message
from nonebot.rule import to_me

from . import (
    xxBot,
    Cron,
)

"""签到"""

# 有效反馈
success_tuple = ('今天已经签到过啦，再给你看一次哦~', '感谢您完成今天的签到！这是您的奖励：')
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册定时任务
cron = Cron(
    style='Regular',
    name='签到',
    msg=xxBot.msg__at_xxbot + Message('签到'),
    feedback_cmd=command_success,
)
