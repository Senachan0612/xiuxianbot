"""计时任务 出闭关"""

from nonebot.plugin.on import on_startswith
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    xxBot,
    eventCheck,
    Cron,
)

"""出闭关"""

# 效反馈
success_tuple = ('进入闭关状态，如需出关，发送【出关】！', '道友现在在做悬赏令呢，小心走火入魔！', '欠这么多钱还想着出关？',
                 '道友现在正在秘境中，分身乏术！',)
command_success = on_startswith(success_tuple, rule=to_me(), priority=100, block=True)

# 注册计时任务
cron = Cron(
    style='CD',
    name='出闭关',
    msg=[
        xxBot.msg__at_xxbot + Message('灵石出关'),
        xxBot.msg__at_xxbot + Message('闭关'),
    ],
    feedback_cmd=command_success,
)

"""结束闭关 激活部分功能"""

success_extend_tuple = ('闭关结束！',)
command_success_extend = on_startswith(success_extend_tuple, rule=to_me(), priority=100)

UnpauseApps = ['突破', '宗门任务']


@command_success_extend.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing=False, monitor=False):
        return

    for name in UnpauseApps:
        unpause_timing = xxBot.get_timing(name)

        if unpause_timing.check('is_pause'):
            unpause_timing('unpause', msg='出关激活暂停')
