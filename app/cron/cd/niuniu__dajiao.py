"""计时任务 牛牛 打胶"""

from nonebot.plugin.on import on_startswith
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    xxBot,
    eventCheck,
    Cron,
)

"""打胶"""

# 有效反馈
success_tuple = ('打胶结束喵, 鲸木的牛牛很满意喵, 长了', '你已经打不动了喵,')
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册计时任务
cron = Cron(
    style='CD',
    name='牛牛打胶',
    msg=xxBot.msg__at_xxbot + Message('打胶 ') + Message(xxBot['niuniu_dajiao_user', ['']][0]),
    feedback_cmd=command_success,
)
