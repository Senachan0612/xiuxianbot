"""宗门任务功能"""

import os
import json
import re
import asyncio
from collections import namedtuple

from nonebot.plugin.on import on_regex, on_keyword, on_fullmatch
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me

from . import (
    DataPath,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)

"""宗门任务"""

# 加载配置
File_Path = r'%s\%s' % (DataPath, 'ZongMenRenWu.json')
Task = namedtuple('Task', 'content money')
# 宗门任务清单
DefaultTaskList = {
    # 2% 挑战
    1: [
        Task('最近有宗外势力抹黑宗门', 0),  # 为了宗主
        Task('最近有人不敬环奈', 0),  # 开启圣战
    ],
    # 2% 灵石
    2: [
        Task('请道友雇佣记者多加宣传', 10000),  # 舆论战
        Task('又到了一年一度集体突破的日子了', 12000),  # 修炼无宗界
        Task('为宗门打扫一下', 30000),  # 清理雕像
    ],
    # 2.2%
    3: [
        Task('为宗门提前五百年迎回弟子', 500000),  # 社会毒打
    ],
    # 4%
    4: [
        Task('宗门高层有个人给你了一个宗门采购清单', 40000000),  # 正当采购
    ],
}

try:
    if os.path.isfile(File_Path):
        # 加载用户配置
        with open(File_Path, mode='r', encoding='utf-8') as f:
            TaskList = {int(_key): [Task(*_v) for _v in _val] for _key, _val in json.load(f).items()}
    else:
        if not os.path.isdir(DataPath):
            os.makedirs(DataPath)

        with open(File_Path, mode='w', encoding='utf-8') as f:
            json.dump(DefaultTaskList, f, ensure_ascii=False, indent=2)
        TaskList = DefaultTaskList
except Exception:
    TaskList = DefaultTaskList

# 注册监控器
timing = Monitor(name='宗门任务')

command = on_fullmatch(('宗门任务', 'zmrw'), rule=to_me(), priority=60, block=True)
exit_command = on_fullmatch(('关闭宗门任务', '!宗门任务', '!zmrw'), rule=to_me(), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '宗门任务': {
        'timing': timing,
        'cmd': command,
        'auto': True,
    },
})

monitor = Monitor(name='宗门任务')
Message__jq = xxBot.msg__at_xxbot + Message('宗门任务接取')
Message__sx = xxBot.msg__at_xxbot + Message('宗门任务刷新')
Message__wc = xxBot.msg__at_xxbot + Message('宗门任务完成')


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    # 启动
    if not timing('start'):
        return

    # 校验执行时间
    _, _, time = xxBot.get_regular_time('Regular_ZongMenRenWu', default=[12, 00], days=0)
    if time > 0:
        timing.set_time(time)
        timing('regular', msg=timing.dt_string(timing.exec_time))

    """监听"""
    while True:
        if timing.check('is_regular'):
            await timing.sleep()

        if timing.check('is_finish'):
            break

        # 执行监听
        timing('running')
        monitor('init')

        """ 宗门任务 接取 """
        await __task_jq(_cmd=command)

        """ 宗门任务 刷新 """
        await __task_sx(_cmd=command, _event=event)

        """ 宗门任务 完成 """
        await __task_wc(_cmd=command, _event=event)

        if monitor.check('is_regular'):
            timing.set_time(monitor.time)
            timing('regular', msg=timing.dt_string(timing.exec_time))
            continue

    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    eventCheck.api_monitor_check_and_control__update_state_by_user(event, timing, state={
        'state': 'exit',
        'msg': '手动结束',
    })


"""宗门任务接取"""

command_jq_false = on_keyword({'道友已接取3次，今日无法再获取宗门任务了'}, rule=to_me(), priority=100)
# 任务内容
task_pattern = r'(%s)' % '|'.join(re.escape(_task.content) for _, _tasks in TaskList.items() for _task in _tasks)
command_jq_ture = on_regex(pattern=task_pattern, flags=re.I, permission=GROUP, rule=to_me(), priority=100)


@command_jq_false.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    # 接取上限，次日重启
    _, _, time = xxBot.get_regular_time('Regular_ZongMenRenWu', default=[12, 00], days=1)

    monitor.set_time(time)
    monitor('regular')


@command_jq_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, monitor):
        return

    task_level = xxBot['xxBot_Config_ZongMen_Task_Level', [1, 2, 3]]
    task_list = (_task for _level, _tasks in TaskList.items() if _level in task_level for _task in _tasks)
    cmd_msg = str(msg)

    # 有效任务
    target_task = [_money for _content, _money in task_list if re.search(re.escape(_content), cmd_msg)]

    if target_task:
        await command_jq_ture.send(xxBot.msg__at_xxbot + Message(f'灵庄取灵石 {sum(target_task)}'))
        monitor('done')


async def __task_jq(_cmd):
    """接取任务"""
    timing(msg='宗门任务接取')
    await _cmd.send(Message__jq)
    await asyncio.sleep(5)


"""宗门任务刷新"""


async def __task_sx(_cmd, _event):
    """刷新任务"""
    if not monitor.check('is_break'):
        timing(msg='宗门任务刷新')
        # 加载异步监听
        loop = LoopEvent(_event, name='zmrw_sx_loop')

        went_await = loop.add(loop.loop_await_cmd('sx', monitor=monitor))
        went_send = loop.add(loop.loop_send_cmd('sx', cmd=_cmd, msg=Message__sx,
                                                time=xxBot['CD_ZongMenRenWu_ShuaXin', 5 * 60]))
        await went_await
        await went_send


"""宗门任务完成"""

task_wc_monitor = Monitor(name='宗门任务完成')

# 有效任务完成反馈
task_wc_pattern = r'(道友为了完成任务购买宝物消耗灵石|道友大战一番，气血减少)'
command_wc_ture = on_regex(pattern=task_wc_pattern, flags=re.I, permission=GROUP, rule=to_me(), priority=100)

command_wc_false_no_hp = on_keyword({'重伤未愈，动弹不得'}, rule=to_me(), priority=100)
command_wc_false_no_money = on_keyword({'道友的灵石不足以完成宗门任务'}, rule=to_me(), priority=100)

command_wc_false_no_task = on_keyword({'道友目前还没有宗门任务'}, rule=to_me(), priority=100)
command_wc_false_no_time = on_keyword({'剩余CD'}, rule=to_me(), priority=100)


@command_wc_ture.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, task_wc_monitor):
        return
    task_wc_monitor('done')


@command_wc_false_no_hp.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, task_wc_monitor):
        return
    task_wc_monitor('pause', msg='状态异常')


@command_wc_false_no_money.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, task_wc_monitor):
        return
    task_wc_monitor('pause', msg='灵石不足')


@command_wc_false_no_task.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, task_wc_monitor):
        return
    task_wc_monitor('skip')


@command_wc_false_no_time.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if eventCheck.api_monitor_check__active_app__xxbot_event(event, timing, task_wc_monitor):
        return

    pattern = r'剩余CD:([\d.]+)秒'
    time = float(re.search(pattern, str(msg)).group(1))

    task_wc_monitor('regular')
    task_wc_monitor.set_time(time)


async def __task_wc(_cmd, _event):
    """完成任务"""
    if monitor.check('is_done'):
        timing(msg='宗门任务完成')
        # 加载异步监听
        loop = LoopEvent(_event, name='zmrw_wc_loop')

        while True:
            remaining_time = timing.get_remaining_time()
            if remaining_time > 0:
                timing('regular', msg=timing.dt_string(timing.exec_time))
                await timing.sleep()

            if timing.check('is_break'):
                break

            timing('running', msg='宗门任务完成')
            timing.set_time()

            task_wc_monitor('init')

            went_await = loop.add(loop.loop_await_cmd('wc', monitor=task_wc_monitor))
            went_send = loop.add(loop.loop_send_cmd('wc', cmd=_cmd, msg=Message__wc))

            await went_await
            await went_send

            if task_wc_monitor.check('is_pause'):
                # 暂停状态 等待状态解除
                timing('pause', msg=task_wc_monitor.msg)
                await loop.add(loop.loop_pause_cmd('pause zmrw wc', monitor=timing))
                continue

            if task_wc_monitor.check('is_done'):
                timing.set_time(xxBot['CD_ZongMenRenWu_WanChen', 30 * 60])
                break
            elif task_wc_monitor.check('is_skip'):
                break
            elif task_wc_monitor.check('is_regular'):
                timing.set_time(task_wc_monitor.time)

            if timing.check('is_break'):
                break
