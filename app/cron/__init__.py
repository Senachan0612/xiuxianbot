"""定时任务相关"""

from pypinyin import pinyin, Style

from nonebot.plugin.on import on_fullmatch
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from .. import (
    Monitor, LoopEvent,

    xxBot,  # 加载xxbot
    eventCheck,  # 加载事件校验工具包
)


class Cron:
    # 启用命令
    cmd = False
    # 退出命令
    exit_cmd = False
    # 反馈命令
    feedback_cmd = False

    # 监控器
    timing = False
    # 监听器
    monitor = False

    # 监听映射
    handle_map = []

    def __init__(self, style, name, msg, feedback_cmd):
        # 任务类型
        self.style = style

        # 名称 简拼 全拼
        self.name = name
        self.simple_name = self.format_name(pinyin(name, style=Style.FIRST_LETTER))
        self.full_name = self.format_name(pinyin(name, style=Style.NORMAL))

        # 内容及反馈
        self.msg = msg
        self.feedback_cmd = feedback_cmd

        # 初始项
        self.set_timing()
        self.set_cmd()
        self.set_app()
        self.set_default_register()

        self.running()

    def running(self):
        """启动"""
        for handle, func in self.handle_map:
            handle(func)

    def register(self, handle, func):
        """注册监听映射"""
        self.handle_map.append((handle, func))

    @staticmethod
    def format_name(pinyin_list):
        """格式化拼音内容"""
        return ''.join(item[0] for item in pinyin_list)

    def set_timing(self):
        """注册监控"""
        self.timing = Monitor(name=self.name)
        self.monitor = Monitor(name=f'{self.name}监控')

    def set_cmd(self):
        """注册命令"""
        self.cmd = on_fullmatch(
            (self.name, self.simple_name), rule=to_me(), priority=50, block=True)
        self.exit_cmd = on_fullmatch(
            (f'关闭{self.name}', f'!{self.name}', f'!{self.simple_name}'), rule=to_me(), priority=50, block=True)

    def set_default_register(self):
        """默认注册监听映射"""
        # 启动
        self.register(handle=self.cmd.handle(), func=self.handle_cmd)
        # 退出
        self.register(handle=self.exit_cmd.handle(), func=self.handle_exit_cmd)
        # 有效反馈
        if self.feedback_cmd:
            self.register(handle=self.feedback_cmd.handle(), func=self.handle_feedback_cmd)

    def set_app(self):
        """注册应用"""
        xxBot.load_apps({
            self.name: {
                'style': self.style,
                'timing': self.timing,
                'cmd': self.cmd,
                'auto': True,
            },
        })

    def get_time(self, days):
        """获取定时"""
        _, _, time = xxBot.get_regular_time(f'Regular_{self.full_name}', default=[23, 30], days=days)
        return time

    async def handle_cmd(self, event: GroupMessageEvent, msg: Message = CommandArg()):
        """启动"""
        timing, monitor = self.timing, self.monitor

        if not eventCheck.api_check__app_event(event):
            return

        # 启动
        if not timing('start'):
            return

        # 校验执行时间
        time = self.get_time(days=0)
        if time > 0:
            timing.set_time(time)
            timing('regular', msg=timing.dt_string(timing.exec_time))

        # 加载异步监听
        loop = LoopEvent(event)

        """监听"""
        while True:
            if timing.check('is_regular'):
                await timing.sleep()
            if timing.check('is_finish'):
                break

            # 执行监听
            timing('running')
            monitor('init')
            went_await = loop.add(loop.loop_await_cmd(self.simple_name, monitor=monitor))
            went_send = loop.add(loop.loop_send_cmd(self.simple_name, cmd=self.cmd, msg=self.msg, count=10))
            await went_await
            await went_send

            if timing.check('is_finish'):
                break

            # 下次执行
            timing.set_time(self.get_time(days=1))
            timing('regular', msg=timing.dt_string(timing.exec_time))

        timing('init')

    async def handle_exit_cmd(self, event: GroupMessageEvent, msg: Message = CommandArg()):
        """退出"""
        if not eventCheck.api_check__app_event(event):
            return

        self.monitor('exit')
        self.timing('exit', msg='手动结束')

    async def handle_feedback_cmd(self, event: GroupMessageEvent, msg: Message = CommandArg()):
        """有效反馈"""
        if eventCheck.api_monitor_check__active_app__xxbot_event(event, self.timing, self.monitor):
            return

        self.monitor('regular')


from . import qiandao
from . import koubaidiaoxiang
from . import zongmendanyao
from . import zongmenrenwu
