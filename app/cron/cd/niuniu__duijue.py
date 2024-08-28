"""计时任务 牛牛 对决"""

from nonebot.plugin.on import on_startswith
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    xxBot,
    eventCheck,
    Cron,
)

"""对决"""

# 有效反馈
success_tuple = ('对决胜利是', '你已经pk不动了喵, 请等待')
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册计时任务
cron = Cron(
    style='CD',
    name='牛牛对决',
    msg=xxBot.msg__at_xxbot + Message('牛牛对决 ') + Message(xxBot['niuniu_duijue_user', ['']][0]),
    feedback_cmd=command_success,
)
