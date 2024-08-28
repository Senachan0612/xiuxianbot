"""自动任务相关"""

from nonebot.plugin.on import on_fullmatch
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg

from .. import (
    Task,
    Monitor, LoopEvent,
    xxBot,  # 加载xxbot
    eventCheck,  # 加载事件校验工具包
)


class Cron(Task):
    # 反馈命令
    feedback_cmd = False

    def __init__(self, *, msg, feedback_cmd, **kwargs):
        # 内容及反馈
        self.msg = msg
        self.feedback_cmd = feedback_cmd

        super(Cron, self).__init__(**kwargs)

    def set_cmd(self):
        """注册命令"""
        self.cmd = on_fullmatch(
            (self.name, self.simple_name), rule=to_me(), priority=50, block=True)
        self.exit_cmd = on_fullmatch(
            (f'关闭{self.name}', f'!{self.name}', f'!{self.simple_name}'), rule=to_me(), priority=50, block=True)

    def set_register(self):
        """默认注册监听映射"""
        super(Cron, self).set_register()
        # 有效反馈
        if self.feedback_cmd:
            self.register(handle=self.feedback_cmd.handle(), func=self.handle_feedback_cmd)

    def get_time(self, days):
        """获取定时"""
        if self.style == 'Regular':
            _, _, time = xxBot.get_regular_time(f'Regular_{self.full_name}', default=[23, 30], days=days)
        elif self.style == 'CD':
            time = xxBot[f'CD_{self.full_name}', 24 * 60 * 60]
        else:
            time = float('inf')

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
        if self.style == 'Regular':
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
            if monitor.check('is_regular'):
                # 定时状态 等待定时时间
                timing.set_time(monitor.time)
            elif monitor.check('is_done'):
                # 完成状态 等待下次执行时间
                timing.set_time(self.get_time(days=1))
            elif monitor.check('is_pause'):
                # 暂停状态 等待暂停状态解除
                timing('pause', msg=monitor.msg)
                await loop.add(loop.loop_pause_cmd(f'Pause {self.simple_name}', monitor=timing))
                continue
            else:
                break
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

        self.monitor('done')


from . import regular
from . import cd
