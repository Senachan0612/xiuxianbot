"""事件循环器"""

import asyncio

from . import Timing
from . import Config

Loop_Max_Count = float(Config['Loop_Max_Count', 'inf'])
Loop_Await_Max_Count = float('inf')
Loop_Send_Time = float(Config['Loop_Send_Time', 10])
Loop_Await_Time = float(Config['Loop_Await_Time', 1])


class LoopEvent(Timing):

    def __init__(self, event, name=False, timing=False):
        super(LoopEvent, self).__init__(name)

        self.event = event
        self.timing = timing

        self.task = dict()
        self.dataset = dict()

        self.add = asyncio.create_task

    def create_task(self, index):
        """创建任务"""
        self.task[index] = True

    def finish_task(self, index, drop=False):
        """完成任务"""
        if index not in self.task:
            return

        if drop:
            self.task.pop(index, False)
        else:
            self.task[index] = False

    def wait_task(self, index, count=Loop_Max_Count):
        """等待任务"""
        while not (index in self.task):
            count -= 1
            if count < 0:
                return False
        return True

    def check_task(self, index=False):
        """检查任务状态"""
        if self.timing:
            assert not self.timing.check('is_error')

        if index is False:
            return bool(self.task)
        return self.task.get(index)

    async def loop_send_cmd(self, index, *, cmd, msg, time=Loop_Send_Time, count=Loop_Max_Count):
        """异步发送指令"""
        if not self.wait_task(index, count=count):
            return

        if type(msg) != list:
            msg = [msg]
        msg_len = len(msg)

        time_split01 = time // 2
        time_split02 = time - time_split01
        while self.check_task(index):
            count -= 1
            if count < 0:
                break

            for _index, _msg in enumerate(msg, start=1):
                await cmd.send(_msg)
                if _index >= msg_len:
                    break
                await asyncio.sleep(5)

            await asyncio.sleep(time_split01)
            if not self.check_task(index):
                break
            await asyncio.sleep(time_split02)

        self.finish_task(index, drop=True)

    async def loop_await_cmd(self, index, *, monitor, time=Loop_Await_Time, count=Loop_Await_Max_Count, no_send=False):
        """
            异步等待指令
            no_send: 为T时表示无需等待发送事件
        :return:
        """
        self.create_task(index)

        while not monitor.check('is_break') and self.check_task(index):
            count -= 1
            if count < 0:
                monitor('error')
                continue

            monitor('waiting')
            await asyncio.sleep(time)

        self.finish_task(index, drop=no_send)

    async def loop_pause_cmd(self, index, *, monitor, time=Loop_Await_Time, count=Loop_Await_Max_Count):
        """
            异步暂停指令
        :return:
        """
        self.create_task(index)

        while monitor.check('is_pause'):
            count -= 1
            if count < 0:
                monitor('error')
                continue

            await asyncio.sleep(time)

        self.finish_task(index, drop=True)
