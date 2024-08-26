"""定时叩拜雕像"""

from nonebot.plugin.on import on_startswith
from nonebot.adapters.onebot.v11 import Message
from nonebot.rule import to_me

from . import (
    xxBot,
    Cron,
)

"""叩拜雕像"""

# 有效反馈
success_tuple = ('神秘的环奈显灵了，你获得', '道友今天已经叩拜过了，明天再来吧。', '你雕像呢？')
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册定时任务
cron = Cron(
    style='Regular',
    name='叩拜雕像',
    msg=xxBot.msg__at_xxbot + Message('叩拜雕像'),
    feedback_cmd=command_success,
)
