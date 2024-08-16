"""灌注功能"""

import asyncio
import os
import json
import re
from collections import namedtuple, ChainMap

from nonebot.plugin.on import on_regex, on_fullmatch, on_startswith, on_keyword
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, GROUP
from nonebot.params import CommandArg
from nonebot.rule import to_me, regex

from . import (
    DataPath,
    Monitor, LoopEvent,
    xxBot,
    eventCheck,
)
from .config import gz_config

# 监控器 拓展编码
TimingCode__Money = '存取灵石'
TimingCode__Items = '穿卸装备'
TimingCode__Status = '查询状态'
TimingCode__Config = '检查配置'
TimingCode__Drugs = '服用丹药'
TimingCode__Battle = '切磋抢劫'

"""灌注"""

# 注册监控器
timing = Monitor(name='灌注')

command = on_startswith(('灌注', 'gz'), rule=to_me(), priority=60, block=True)
exit_command = on_fullmatch(('关闭灌注', '!灌注', '!gz'), rule=to_me(), priority=60, block=True)

# 注册应用
xxBot.load_apps({
    '灌注': {
        'timing': timing,
        'cmd': command,
        'auto': False,
    }
})


def check(error_list):
    """校验"""
    if error_list:
        return error_list

    if not bot_gz.active:
        error_list.append(f'{bot_gz.name}：{bot_gz.msg}')
    if not user_gz.active:
        error_list.append(f'{user_gz.name}：{user_gz.msg}')
    return error_list


@command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event):
        return

    for message in event.message:
        if message.type == 'at':
            uid = int(message.data['qq'])
            break
    else:
        uid = event.user_id

    _, uname, level = re.compile(r'(灌注|gz)\s*(\S*)\s*(\d*)').search(str(event.message)).groups()
    # 启动
    if not timing('start'):
        return
    timing('running')

    try:
        # 获取状态
        await __task_get_status(command, event, uname, uid)

        error_list = []
        if not check(error_list):
            # 检查配置
            await __task_check_config(command, event)

        if not check(error_list):
            timing(msg='开始灌注')
            if not level:
                level = xxBot['GuanZhu_Max_Level', 25]
            # 灌注
            await __task_running(command, event, _level=int(level))

        if check(error_list):
            await command.send(xxBot.msg__at(event.user_id) + Message('执行灌注失败！\n') + Message('\n'.join(error_list)))
        else:
            await command.send(xxBot.msg__at(event.user_id) + Message('执行灌注结束！\n'))
    except AssertionError:
        await command.send(xxBot.msg__at(event.user_id) + Message(timing.msg))

    # 灌注结束
    timing('init')


@exit_command.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if not eventCheck.api_check__app_event(event) or timing.check('is_valid'):
        return

    timing('error', msg='立即停止')


"""灌注 准备工作"""
HpDanYao = {
    5: '生骨丹',
    10: '化瘀丹',
    15: '固元丹',
    20: '培元丹',
    25: '黄龙丹',
    30: '回元丹',
    35: '回春丹',
    40: '养元丹',
    45: '太元真丹',
    50: '九阳真丹',
    60: '归藏灵丹',
}


def timing_code(func):
    """Timing监听切换"""
    save_code = timing.msg

    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        # 恢复code
        timing(msg=save_code)
        return result

    return wrapper


class GuanZhu:
    name = False
    uid = False
    cmd = False
    event = False
    at_user = False
    # 启用
    active = False
    # 信息
    msg = False

    # 当前HP
    HP = False
    # 最大HP
    HP_Max = False
    # 攻击
    Atk = False
    # 暴伤
    CritProb = False
    # 暴击率
    CritRate = False
    # 减伤
    Def = False
    # 辅修
    FuXiu = False

    # 血丹
    drug = False
    _drug = False
    drugs_list = False

    # 切磋
    qc_status = False

    # 配置
    config = {}
    # 伤害公式
    damage_config = {}
    # 默认辅修
    config_fangju_dict = ChainMap({
        0: '卸载防具'
    })
    config_wuqi_dict = ChainMap({
        0: '卸载武器'
    })
    config_fuxiu_pu_dict = ChainMap({
        0: '卸载辅修功法',
        0.5: '装备功法 真龙九变',
        0.6: '装备功法 兰那罗之歌',
    })
    config_fuxiu_bao_dict = ChainMap({
        None: '装备功法 金刚移山诀',
    })

    # 武器
    Config_Weapon = False
    # 辅修
    Config_FuXiu = False
    # 减伤
    Config_Def = False
    # 伤害倍率
    Config_Damage = False

    def __init__(self, is_bot=False):
        self.is_bot = is_bot
        self.money_monitor = Monitor('存取灵石')
        self.items_monitor = Monitor('装备监控')
        self.status_monitor = Monitor('状态监控')
        self.drugs_monitor = Monitor('吃药监控')
        self.battle_monitor = Monitor('战斗监控')

    def control(self, active=True, msg=False):
        """关闭"""
        self.active = active
        self.msg = msg

    async def init(self, cmd, event, uid, name=False):
        """初始化"""
        self.control()
        self.name = name
        self.uid = uid
        self.cmd = cmd
        self.event = event
        self.at_user = xxBot.msg__at(self.uid)

        # todo
        # 初始化装备
        await self.init_items()
        # 获取状态
        await self.get_status()

    """灵石"""

    @timing_code
    async def set_money(self):
        """存灵石"""
        if not self.is_bot:
            return
        timing(msg=TimingCode__Items)
        loop = LoopEvent(self.event, name='Set Money', timing=timing)

        money = 0
        while True:
            self.money_monitor('init')
            msg = self.at_user + Message(f'灵庄存灵石 {money}')

            went_await = loop.add(loop.loop_await_cmd('Set Money', monitor=self.money_monitor))
            went_send = loop.add(loop.loop_send_cmd('Set Money', cmd=self.cmd, msg=msg, time=10, count=3))
            await went_await
            await went_send

            if self.money_monitor.check('is_done'):
                break

    async def get_money(self):
        """取灵石"""
        await self.cmd.send(self.at_user + Message(f'灵庄存灵石 {100000000}'))

    """装备"""

    @timing_code
    async def set_items(self, item_list=False):
        """穿卸装备"""
        if not self.active or not item_list:
            return

        timing(msg=TimingCode__Items)
        loop = LoopEvent(self.event, name='Set Items', timing=timing)

        for item in item_list:
            self.items_monitor('init')
            item_msg = self.at_user + Message(item)

            went_await = loop.add(loop.loop_await_cmd('Set Items', monitor=self.items_monitor))
            went_send = loop.add(loop.loop_send_cmd('Set Items', cmd=self.cmd, msg=item_msg, time=10, count=3))
            await went_await
            await went_send

            if not self.items_monitor.check('is_done'):
                return self.control(active=False, msg='穿卸装备失败！')

    async def init_items(self):
        """初始化装备"""
        items_list = [
            '卸载神通',
        ]
        if self.is_bot:
            items_list.extend([
                '卸载防具',
            ])
        else:
            items_list.extend([
                '卸载武器',
                '装备功法 金刚移山诀',
            ])

        await self.set_items(items_list)

    async def get_items(self, supply_range):
        """计算待更换装备"""
        # 当前倍率
        config = self.Config_Damage
        # 补充倍率
        range_min, range_max = supply_range
        # 目标倍率
        config_min, config_max = config * (1 + range_min), config * (1 + range_max)
        # 根据中位数补充伤害  range_min <= 补充 == range_avg <= range_max
        config_avg = sum((config_min, max(config_min, config_max))) / 2

        # 筛选范围内公式
        damage_config = list(filter(lambda x: x[0] > config_min, self.damage_config.items()))
        if not damage_config:
            return self.control(active=False, msg=f'当前没有能打过对方的装备组合，无法灌注！')

        (self.Config_Damage, (
            (fuxiu_val, fuxiu_cmd),
            (wuqi_val, wuqi_cmd),
            (fangju_val, fangju_cmd),
        )) = min(damage_config, key=lambda x: abs(x[0]) - config_avg)

        bot_items, user_items = [], []

        def _is_equal(x, y):
            if x is None:
                return y is None
            return x == y

        # 辅修
        if not _is_equal(self.Config_FuXiu, fuxiu_val):
            user_items.append(fuxiu_cmd)
            self.Config_FuXiu = fuxiu_val
        # 武器
        if not _is_equal(self.Config_Weapon, wuqi_val):
            user_items.append(wuqi_cmd)
            self.Config_Weapon = wuqi_val
        # 防具
        if not _is_equal(self.Config_Def, fangju_val):
            bot_items.append(fangju_cmd)
            self.Config_Def = fangju_val

        return bot_items, user_items

    """状态"""

    def set_status(self, status):
        """更新状态"""
        self.name = status.name
        self.HP = float(status.HP)
        self.HP_Max = float(status.HP_Max)
        self.CritRate = int(int(status.CritRate) > 0)
        self.Def = float(status.Def) * 0.01

    @timing_code
    async def get_status(self):
        """获取状态"""
        if not self.active:
            return

        timing(msg=TimingCode__Status)
        loop = LoopEvent(self.event, name='Get Status', timing=timing)

        send_msg = self.at_user + Message('我的状态')
        self.status_monitor('init')

        went_await = loop.add(loop.loop_await_cmd('Get Status', monitor=self.status_monitor))
        went_send = loop.add(loop.loop_send_cmd('Get Status', cmd=self.cmd, msg=send_msg, time=10, count=3))

        await went_await
        await went_send

        if not self.status_monitor.check('is_done'):
            return self.control(active=False, msg='状态获取失败！')

        self.set_status(self.status_monitor.msg)

    """配置"""

    def load_config(self):
        """读取配置"""
        self.config = gz_config.get_config(self.name)

    def print_config(self):
        """打印配置"""
        if self.is_bot:
            return gz_config.print_config(data={'bot': self.config})
        else:
            return gz_config.print_config(uname=self.name)

    def print_damage_config(self):
        """打印伤害公式配置"""
        return Message('\n'.join(
            '伤害倍率：{:.2%}，辅修：{}，武器：{:.2%}，防具：{:.2%}'.format(val, items.fuxiu[1], items.wuqi[0], items.wuqi[0])
            for val, items in self.damage_config.items()))

    def set_damage_config(self, user):
        """生成伤害配置"""
        user_config = user.config
        damage_config = {}
        # 辅修 武器 防具
        DamageConfigItems = namedtuple('DamageConfigItems', 'fuxiu wuqi fangju')

        # 防具
        items__fj_dict = self.config_fangju_dict.new_child(self.config.get('防具', {}))
        # 普攻武器
        items__pu__wq_dict = user_config.get('普攻', {})
        # 爆攻武器
        items__bao__wq_dict = self.config_wuqi_dict.new_child(user_config.get('暴攻', {}))

        for fj_item in items__fj_dict.items():
            fj_val, fj_cmd = fj_item
            # 普攻
            for wq_item in items__pu__wq_dict.items():
                wq_val, wq_cmd = wq_item
                for fx_item in self.config_fuxiu_pu_dict.items():
                    fx_val, fx_cmd = fx_item
                    damage = self.get_damage(fx_val, wq_val, fj_val)
                    damage_config[damage] = DamageConfigItems(fx_item, wq_item, fj_item)

            # 爆攻
            for wq_item in items__bao__wq_dict.items():
                wq_val, wq_cmd = wq_item
                for fx_item in self.config_fuxiu_bao_dict.items():
                    fx_val, fx_cmd = fx_item
                    damage = self.get_damage(fx_val, wq_val, fj_val)
                    damage_config[damage] = DamageConfigItems(fx_item, wq_item, fj_item)

        self.damage_config = dict(sorted(damage_config.items(), key=lambda x: x[0]))

        # 初始化数据
        self.Config_Weapon = 0
        self.Config_Def = 0
        self.Config_FuXiu = None
        self.Config_Damage = self.get_damage(self.Config_FuXiu, self.Config_Weapon, self.Config_Def)

    @staticmethod
    def get_damage(fx, wq, fj):
        """计算伤害公式"""
        if fx is None:
            # 爆攻伤害公式 = 武器 * 防具 * 辅修 * 爆伤
            damage = (1 + wq) * (1 - fj) * 1 * 1.5
        else:
            # 普攻伤害公式 = 武器 * 防具 * 辅修 * 爆伤
            damage = (1 + wq) * (1 - fj) * (1 + fx) * 1
        return damage

    """吃药"""

    def set_drugs(self, level):
        """更新血丹信息"""
        drugs_list = range(10, min(level, xxBot['GuanZhu_Max_Level', 25]) + 1, 5)
        self.drugs_list = list(reversed(drugs_list))
        self.drug = False
        self._drug = False

    @timing_code
    async def get_drugs(self):
        """服用血丹"""
        if not self.active:
            return

        timing(msg=TimingCode__Drugs)
        loop = LoopEvent(self.event, name='Get Drugs', timing=timing)

        while True:
            if await self._get_drugs(loop):
                if not self.drugs_list:
                    return self.control(active=False, msg='灌注完毕！')
                self._drug = self.drugs_list.pop()
                self.drug = 15 if self._drug < 15 else self._drug
                continue
            break

    async def _get_drugs(self, loop):
        """服用血丹 实现"""
        if not self._drug:
            return '换丹'

        while True:
            # 当前hp占比
            hp_rate = bot_gz.HP / bot_gz.HP_Max
            # 补充hp
            hp_rate_supply = 0.1 - hp_rate

            if hp_rate_supply < 0:
                return

            if self._drug <= 10:
                drug_list = [5, 10]
            else:
                drug_list = [self._drug]

            while True:
                for drug in drug_list:
                    drugs_msg = xxBot.msg__at_xxbot + Message(f'服用丹药 {HpDanYao[drug]}')

                    self.drugs_monitor('init')

                    went_await = loop.add(loop.loop_await_cmd('Get Drug', monitor=self.drugs_monitor))
                    went_send = loop.add(loop.loop_send_cmd('Get Drug', cmd=self.cmd, msg=drugs_msg, time=10, count=1))
                    await went_await
                    await went_send

                    if self.drugs_monitor.check('is_skip'):
                        return '换丹'
                    elif not self.drugs_monitor.check('is_done'):
                        # 未监听到成功服用时 查询状态判断是否服用成功
                        await self.get_status()

                # 检查状态 当前hp占比 + 剩余血丹 < 10% 视为服用失败
                if self.HP / self.HP_Max <= 0.1:
                    continue
                break

    def get_drugs_update_status(self, drug=False):
        """服用血丹 更新状态"""
        if not drug:
            drug = self.drug
        self.HP += self.HP_Max * drug * 0.01

    """灌注"""

    async def get_battle(self, ttype):
        """战斗"""
        if not self.active:
            return

        timing(msg=TimingCode__Battle)
        loop = LoopEvent(self.event, name='Get Battle', timing=timing)

        battle_msg = xxBot.msg__at_xxbot + Message(f'{ttype} {user_gz.name}')
        self.battle_monitor('init')

        went_await = loop.add(loop.loop_await_cmd('Get Battle', monitor=self.battle_monitor))
        went_send = loop.add(loop.loop_send_cmd('Get Battle', cmd=self.cmd, msg=battle_msg, time=10, count=3))
        await went_await
        await went_send

        if not self.battle_monitor.check('is_done'):
            return self.control(active=False, msg=f'{ttype}失败！')

        return self.battle_monitor.msg

    def get_expected_harm(self):
        """期望伤害"""
        hp, hp_max = self.HP, self.HP_Max
        drug = max(self.drug * 0.01, 0.15)

        # 期望血量 -1 * (hp_max * 丹药 + hp_max * 10%) ~ -1
        expected_hp_min, expected_hp_max = -1 * (hp_max * (drug - 0.1)), -1
        # 期望伤害
        expected_damage_min, expected_damage_max = hp - expected_hp_max, hp - expected_hp_min
        # 理论伤害
        theory_damage_min, theory_damage_max = expected_damage_min / 0.9, expected_damage_max / 1.1

        return theory_damage_min, theory_damage_max

    async def get_battle_actual(self):
        """切磋"""
        result = await self.get_battle(ttype='切磋')
        if not self.active:
            return

        # 计算期望伤害
        self.HP = result.damage + result.health
        theory_damage_min, theory_damage_max = self.get_expected_harm()

        # 补足伤害
        return theory_damage_min / result.damage - 1, theory_damage_max / result.damage - 1

    async def get_battle_combat(self):
        """抢劫"""
        result = await self.get_battle(ttype='抢劫')
        if not self.active:
            return

        self.HP = result.health
        return True


bot_gz = GuanZhu(is_bot=True)
user_gz = GuanZhu()


async def __task_get_status(_cmd, _event, _uname, _uid):
    """灌注 获取状态"""
    user_await = user_gz.init(_cmd, _event, name=_uname, uid=_uid)
    bot_await = bot_gz.init(_cmd, _event, uid=xxBot.xxBotId)
    await user_await
    await bot_await


async def __task_check_config(_cmd, _event):
    """灌注 确认配置"""
    timing(msg=TimingCode__Config)

    bot_gz.load_config()
    user_gz.load_config()

    # 生成伤害公式字典
    bot_gz.set_damage_config(user_gz)

    # await _cmd.send(
    #     Message(user_gz.at_user + '本次灌注伤害配置信息：\n')
    #     + bot_gz.print_damage_config()
    # )


"""获取状态"""

get_status_pattern = (
    r'.*道号：(.*?)\n'
    r'气血：(-?\d+\.?\d*)/(\d+\.?\d*)\n'
    r'真元：\d+\.?\d*/\d+\.?\d*\n'
    r'攻击：\d+\.?\d* 攻击修炼：\d+级\(提升攻击力\d+%\)\n'
    r'修炼效率：\d+%\n'
    r'会心：(-?\d+)%\n'
    r'减伤率：(\d+)%\n'
    r'今日突破次数：\d+\n'
    r'今日总突破次数：\d+\n?'
)
command_get_status = on_regex(get_status_pattern, permission=GROUP, priority=1000, block=True)

StatusInfo = namedtuple('StatusInfo', 'name HP HP_Max CritRate Def')


@command_get_status.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if timing.msg != TimingCode__Status:
        return

    # 状态文本
    str_msg = msg and str(msg) or event.raw_message
    status = StatusInfo(*re.compile(get_status_pattern).search(str_msg).groups())

    if event.to_me and not bot_gz.status_monitor.check('is_break'):
        # bot信息
        bot_gz.status_monitor('done', msg=status)
    elif user_gz.name == status.name and xxBot.check_is_eid(event.user_id) \
            and not user_gz.status_monitor.check('is_break'):
        # 其他用户信息
        user_gz.status_monitor('done', msg=status)


"""服用丹药"""

get_drugs_pattern = r'道友成功使用丹药：(.*?)，状态恢复了(\d+)%！$'
command_get_drugs = on_regex(get_drugs_pattern, permission=GROUP, rule=to_me(), priority=100, block=True)

get_drugs__no_count_tuple = ('道友没有该丹药，无法使用！', '道友使用的丹药已经达到每日上限，今日使用已经没效果了哦~！')
command_get_drugs__no_count = on_fullmatch(get_drugs__no_count_tuple, permission=GROUP, rule=to_me(), priority=100)


@command_get_drugs.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if timing.msg != TimingCode__Drugs:
        return
    if not xxBot.check_is_xxbot(event.user_id) or bot_gz.drugs_monitor.check('is_break'):
        return

    drugs_name, drugs_hp = re.compile(get_drugs_pattern).search(str(event.message)).groups()
    drug = int(drugs_hp)
    if not (int(drug) == bot_gz.drug or int(drug) in [5, 10] and bot_gz.drug == 15):
        bot_gz.drugs_monitor('error')
        return
    bot_gz.get_drugs_update_status(drug)
    bot_gz.drugs_monitor('done')


@command_get_drugs__no_count.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if timing.msg != TimingCode__Drugs:
        return
    if not xxBot.check_is_xxbot(event.user_id) or bot_gz.drugs_monitor.check('is_break'):
        return

    bot_gz.drugs_monitor('skip')


"""切磋"""

get_battle_pattern = (
    r'.*?☆------(\S+)的回合------☆\n'
    r'.*?(\S+)发起攻击，.*?造成了(-?\d+)伤害.*?\n'
    r'.*?(\S+)剩余血量(-?\d+)'
)
command_get_battle = on_regex(get_battle_pattern, permission=GROUP, rule=to_me(), priority=100, block=True)

BattleInfo = namedtuple('BattleInfo', 'damage health')


@command_get_battle.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if timing.msg != TimingCode__Battle:
        return
    if not xxBot.check_is_xxbot(event.user_id) or bot_gz.battle_monitor.check('is_break'):
        return

    user_name, _, damage, bot_name, health = re.compile(get_battle_pattern).search(str(event.message)).groups()
    if bot_name != bot_gz.name or user_name != user_gz.name:
        return

    bot_gz.battle_monitor('done', msg=BattleInfo(float(damage), float(health)))


"""装备"""

command_set_items = on_keyword({'恭喜道友装备成功，快去试试吧。', '卸载成功。'}, permission=GROUP, priority=1000, block=True)


@command_set_items.handle()
async def _(event: GroupMessageEvent, msg: Message = CommandArg()):
    if timing.msg != TimingCode__Items:
        return

    for message in event.message:
        if message.type == 'at':
            if str(user_gz.uid) == message.data['qq'] and not user_gz.items_monitor.check('is_break'):
                user_gz.items_monitor('done')
            break
    else:
        if event.to_me and xxBot.check_is_xxbot(event.user_id) and not bot_gz.items_monitor.check('is_break'):
            bot_gz.items_monitor('done')


"""开始灌注"""


async def __task_running(_cmd, _event, _level):
    """灌注 开始灌注"""
    bot_gz.set_drugs(_level)

    count = 2
    while True:
        if not bot_gz or not user_gz:
            return

        # 检查hp
        await bot_gz.get_drugs()

        # 切磋
        supply_range = await bot_gz.get_battle_actual()

        # 计算装备
        if not supply_range:
            return
        result = await bot_gz.get_items(supply_range)

        # 更换装备
        if count and any(result or []):
            bot_items, user_items = result
            await bot_gz.set_items(bot_items)
            await user_gz.set_items(user_items)

            count -= 2
            continue

        # 抢劫
        await bot_gz.get_battle_combat()
        count = 2
