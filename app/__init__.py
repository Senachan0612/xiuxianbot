"""功能"""

from pypinyin import pinyin, Style

from nonebot.plugin.on import on
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from .. import (
    DataPath, UserData,
    Config,
    Monitor, LoopEvent,

    xxBot,  # 加载xxbot
    eventCheck,  # 加载事件校验工具包
)


class Task:
    # 启用命令
    cmd = False
    # 退出命令
    exit_cmd = False

    # 监控器
    timing = False
    # 监听器
    monitor = False

    def __init__(self, style, name, auto=True, **kwargs):
        # 任务类型
        self.style = style
        # 监听映射
        self.handle_map = []

        # 名称 简拼 全拼
        self.name = name
        self.simple_name = self.format_name(pinyin(name, style=Style.FIRST_LETTER))
        self.full_name = self.format_name(pinyin(name, style=Style.NORMAL))

        # 初始项
        self.set_timing()
        self.set_cmd()
        self.set_app(auto=auto)
        self.set_register()

        self.running()

    def running(self):
        """启动"""
        for handle, func in self.handle_map:
            handle(func)

    def register(self, handle, func):
        """注册监听映射"""
        self.handle_map.append((handle, func))

    def set_timing(self):
        """注册监控"""
        self.timing = Monitor(name=self.name)
        self.monitor = Monitor(name=f'{self.name}监控')

    def set_cmd(self):
        """注册命令"""
        self.cmd = on()
        self.exit_cmd = on()

    def set_register(self):
        """默认注册监听映射"""
        # 启动
        self.register(handle=self.cmd.handle(), func=self.handle_cmd)
        # 退出
        self.register(handle=self.exit_cmd.handle(), func=self.handle_exit_cmd)

    def set_app(self, auto):
        """注册应用"""
        xxBot.load_apps({
            self.name: {
                'task': self,
                'timing': self.timing,
                'cmd': self.cmd,
                'auto': auto,
            },
        })

    async def handle_cmd(self, event: GroupMessageEvent, msg: Message = CommandArg()):
        """启动"""
        pass

    async def handle_exit_cmd(self, event: GroupMessageEvent, msg: Message = CommandArg()):
        """退出"""
        pass

    @staticmethod
    def format_name(pinyin_list):
        """格式化拼音内容"""
        return ''.join(item[0] for item in pinyin_list)


# 加载功能
from . import cron
from . import service
from . import zongmen
from . import xuanshang
from . import guanzhu

# xxBot同步配置
xxBot.save_configs()
