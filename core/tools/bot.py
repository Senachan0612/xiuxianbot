"""bot"""

__all__ = [
    'xxBot',
]

from collections import namedtuple

import nonebot
from nonebot.adapters.onebot.v11 import Message

from . import Config

App = namedtuple('App', 'timing matcher auto msg at_bot')


class XiuXianBot:
    # bot配置
    _config = Config
    # 应用清单
    apps = {}
    # 自启动
    auto_apps = {}
    # 配置信息
    config_dict = {
        'is_use_due': False,  # 使用肚饿丹
    }

    @property
    def bot(self):
        """bot"""
        return nonebot.get_bot()

    @property
    def BotId(self):
        """bot"""
        return self.bot.self_id

    def __init__(self):
        self.load_configs()

        # 允许群组
        self.GroupIds = self['Group_Ids', []]
        # 超级管理员
        self.SuperManagerIds = self['Super_Manager_Ids', []]
        # 管理员
        self.ManagerIds = list(set(self.SuperManagerIds + self['Manager_Ids', []]))
        # 修仙botID
        self.xxBotId = self['Bot_Id']

    def __call__(self, item):
        """获取应用"""
        return self.apps[item]

    def __getitem__(self, item):
        return self._config[item]

    def load_configs(self):
        """初始化配置"""
        if not self['xxbot_config_is_up_to_date']:
            self.update_configs({
                # 自启动应用
                'xxbot_config_auto_apps': self.auto_apps,
                # 配置信息
                'xxbot_config_configs': self.config_dict,
            })
        else:
            self.auto_apps = self['xxbot_config_auto_apps']
            self.config_dict = self['xxbot_config_configs']

    def load_apps(self, data: dict):
        """初始化应用"""

        def _f():
            for k, v in data.items():
                yield k, App(
                    v['timing'],
                    v['cmd'],
                    v.get('auto'),
                    Message(v.get('msg', k)),
                    v.get('at_bot', True)
                )

        self.apps.update(dict(_f()))
        self.load_auto_apps()

    def load_auto_apps(self):
        """加载初始化应用"""
        for name, info in self.apps.items():
            if name not in self.auto_apps:
                self.update_auto_apps(name, valid=info.auto)

    def update_auto_apps(self, name, valid=True):
        """修改初始化应用"""
        self.auto_apps[name] = bool(valid)
        self.update_configs({
            # 自启动应用
            'xxbot_config_auto_apps': self.auto_apps,
        })

        #     = {
        #     # 'cg_timing': Monitor(name='出关', time=get_config('Default_ChuGuan', _type='eval')),
        #     # 'tp_timing': Monitor(name='突破', time=get_config('Default_TuPo', _type='eval')),
        #     # 'gz_timing': Monitor(name='复读'),
        #     # 'tpd_timing': Monitor(name='突破丹'),
        #     #
        #     # 'zmrw_timing': Monitor(name='宗门任务', time=get_config('Default_ZongMenRenWu', _type='eval')),
        #     # 'xsl_timing': Monitor(name='悬赏令'),
        #     #
        #     'sc_timing': Monitor(name='收草', time=self._config['Default_Interval_ShouCao', 24 * 60 * 60]),
        #     # 'dx_timing': Monitor(name='雕像', time=24 * 60 * 60),
        #     # 'zmdy_timing': Monitor(name='宗门丹药', time=24 * 60 * 60),
        # }

    def update_configs(self, configs):
        """更新配置"""
        self._config.update(configs, write=configs.get('xxbot_config_is_up_to_date'))

    def save_configs(self):
        """保存配置"""
        self.update_configs({
            'xxbot_config_is_up_to_date': True,
        })

    def get_timing(self, name):
        """获取应用监控器"""
        app = self(name)
        return app['timing']

    def status(self):
        """打印状态"""
        return (
                Message('####指令\n') + self.cmd_status()
                + Message('\n\n####状态\n') + self.bot_status()
        )

    def bot_status(self):
        """bot状态"""
        msg_list = [
            ('肚饿丹', '允许' if self['is_use_due'] else '禁止'),
        ]
        msg_str = Message('\n'.join(''.join(self._right(m) for m in info) for info in msg_list))
        return msg_str

    def cmd_status(self):
        """命令状态"""

        msg_list = [
            ['指令', '状态', '', ],
            *[app.timing.log() for _, app in self.apps.items()]
        ]
        msg_str = Message('\n'.join(''.join(self._right(m) for m in info) for info in msg_list))
        return msg_str

    @staticmethod
    def _right(text):
        return '{: <10}'.format(text)

    def set_security(self, operate, tag, nums):
        """设置授权"""
        if tag == '超管':
            name, security = 'Super_Manager_Ids', self.SuperManagerIds
        elif tag == '用户':
            name, security = 'Manager_Ids', self.ManagerIds
        elif tag == '群组':
            name, security = 'Group_Ids', self.GroupIds
        else:
            return

        if operate == '设置授权':
            security.extend(set(nums) - set(security))
        elif operate == '取消授权':
            nums_index = (security.index(num) for num in (set(security) & set(nums)))
            for index in sorted(nums_index, reverse=True):
                security.pop(index)
        else:
            return

        self.update_configs({
            # 自启动应用
            name: security,
        })
        return security

    """通用回复模板"""

    @property
    def msg__at_xxbot(self):
        """at xxbot 命令"""
        return Message(f"[CQ:at,qq={self.xxBotId}] ")

    @property
    def msg__at_bot(self):
        """at bot 命令"""
        return Message(f"[CQ:at,qq={self.BotId}] ")

    """通用校验"""

    def check_is_gid(self, _id):
        """检查 是否拥有群组权限"""
        return _id in self.GroupIds

    def check_is_uid(self, _id):
        """检查 是否拥有用户权限"""
        return _id in self.SuperManagerIds or _id in self.ManagerIds

    def check_is_suid(self, _id):
        """检查 是否拥有超级用户权限"""
        return _id in self.SuperManagerIds

    def check_is_xxbot(self, _id):
        """检查 是否为bot"""
        return _id == self.xxBotId


xxBot = XiuXianBot()
