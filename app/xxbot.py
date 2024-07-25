"""bot"""

from nonebot.adapters.onebot.v11 import Message

from . import Config, Monitor


class XiuXianBot:
    # bot配置
    _config = Config
    # 应用清单
    apps = {}

    def __init__(self):
        # 允许群组
        self.GroupIds = self._config['Group_Ids', []]
        # 超级管理员
        self.SuperManagerIds = self._config['Super_Manager_Ids', []]
        # 管理员
        self.ManagerIds = list(set(self.SuperManagerIds + self._config['Manager_Ids', []]))
        # 修仙botID
        self.xxBotId = self._config['Bot_Id']

        self.load_apps()

    def __getitem__(self, item):
        return self.apps[item]

    @property
    def msg__at_xxbot(self):
        """at xxbot 命令"""
        return Message(f"[CQ:at,qq={self.xxBotId}] ")

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

    def load_apps(self):
        """加载应用"""
        self.apps = {
            # 'cg_timing': Monitor(name='出关', time=get_config('Default_ChuGuan', _type='eval')),
            # 'tp_timing': Monitor(name='突破', time=get_config('Default_TuPo', _type='eval')),
            # 'gz_timing': Monitor(name='复读'),
            # 'tpd_timing': Monitor(name='突破丹'),
            #
            # 'zmrw_timing': Monitor(name='宗门任务', time=get_config('Default_ZongMenRenWu', _type='eval')),
            # 'xsl_timing': Monitor(name='悬赏令'),
            #
            'sc_timing': Monitor(name='收草', time=self._config['Default_Interval_ShouCao', 24 * 60 * 60]),
            # 'dx_timing': Monitor(name='雕像', time=24 * 60 * 60),
            # 'zmdy_timing': Monitor(name='宗门丹药', time=24 * 60 * 60),
        }
