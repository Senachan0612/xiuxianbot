"""服务任务相关"""

from nonebot.plugin.on import on_fullmatch
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from .. import (
    Task,
    UserData,
    Monitor, LoopEvent,
    xxBot,  # 加载xxbot
    eventCheck,  # 加载事件校验工具包
)


class Service(Task):

    def set_cmd(self):
        """注册命令"""
        self.cmd = on_fullmatch(
            (self.name, self.simple_name), rule=to_me(), priority=70, block=True)
        self.exit_cmd = on_fullmatch(
            (f'关闭{self.name}', f'!{self.name}', f'!{self.simple_name}'), rule=to_me(), priority=70, block=True)

    async def handle_cmd(self, event: GroupMessageEvent, msg: Message = CommandArg()):
        """启动"""
        if not eventCheck.api_check__app_event(event):
            return

        # 启动
        if not self.timing('start'):
            return

        self.timing('running', msg='执行中...')

    async def handle_exit_cmd(self, event: GroupMessageEvent, msg: Message = CommandArg()):
        """退出"""
        if not eventCheck.api_check__app_event(event) and not self.timing.check('is_init'):
            return

        self.timing('init')


from . import tupodan
from . import fudu
