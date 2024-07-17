import asyncio
import datetime
from dateutil.relativedelta import relativedelta

from . import TimingBase


class Monitor(TimingBase):
    def __init__(self, name=False, time=0, start=False):
        super(Monitor, self).__init__(name, start=start)

        # 默认等待时间 (秒)
        self.default_time = time
        # 等待时间
        self.time = time
        # 命令更新时间
        self.update_time = False
        # 命令执行时间
        self.exec_time = False

    @staticmethod
    def dt_string(dt=False):
        """格式化日期"""
        if not dt:
            return '/'
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def log(self):
        return (
            self.name,
            self.state.print,
            self.msg or '/',
            self.dt_string(self.exec_time),
        )

    def set_time(self, time=False):
        """设置监听器间隔时间"""
        time = self.default_time if time is False else time

        update_dt = datetime.datetime.now()
        exec_time = update_dt + relativedelta(seconds=time)

        self.time = time
        self.update_time = update_dt
        self.exec_time = exec_time

    def get_time(self):
        """获取监听器间隔时间"""
        time = self.time
        self.set_time()
        return time

    async def sleep(self):
        await asyncio.sleep(self.time)
