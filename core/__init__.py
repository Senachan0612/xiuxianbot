""""""
import nonebot

from collections import defaultdict, namedtuple

config_dict = nonebot.get_driver().config.dict()

Loop_Max_Count = float(config_dict.get('Max_Loop'.lower(), 'inf'))
Loop_Send_Time = float(config_dict.get('Loop_Send_Time'.lower(), 5))
Loop_Await_Time = float(config_dict.get('Loop_Await_Time'.lower(), 1))

# 状态
StateInfo = namedtuple('StateInfo', 'name code print')
StateInit = [
    StateInfo('error', -99, '错误'),
    StateInfo('auto', -10, '自启动'),
    StateInfo('warn', -1, '警告'),
    StateInfo('init', 0, '初始'),
    StateInfo('start', 10, '启动'),
    StateInfo('running', 20, '执行中'),
    StateInfo('waiting', 30, '等待中'),
    StateInfo('waiting', 30, '等待中'),
    StateInfo('pause', 80, '暂停'),
    StateInfo('regular', 90, '定时'),
    StateInfo('done', 99, '结束'),
]


class TimingBase:
    # 初始
    _StateInit = StateInit
    name = False
    state = False
    _state = False
    # 日志信息
    msg = False

    def __init__(self, name, *args, start=False, **kwargs):

        # 状态-编码映射
        self._StateMappingCode = {item.code: item for item in self._StateInit}
        # 状态-名称映射
        self._StateMappingName = {item.name: item for item in self._StateInit}
        # 状态反向映射 - 组合
        self._StateCheckMulti = self._init_state_check()

        self.init(name=name, start=start)

    def __setattr__(self, key, value):
        if key in ['name', 'state']:
            return

        super(TimingBase, self).__setattr__(key, value)

    def __call__(self, state=False, *, msg=False, **kwargs):
        if state is not False:
            self._set_state(name=state, **kwargs)
        self.msg = msg

    def init(self, name=False, start=False):
        """初始化"""
        su = super(TimingBase, self)

        # 容器描述
        su.__setattr__('name', name or getattr(self, 'name', False))
        # 暂停状态
        su.__setattr__('_pause_state', 80)
        # 状态
        self._set_state(name='init', init=True)

        if start:
            self('start')

    def _get_state(self, error=True, code=False, name=False, **kwargs):
        """获取状态"""
        if code is not False:
            _dict = self._StateMappingCode
            _key = code
        else:
            _dict = self._StateMappingName
            _key = name

        if error:
            error = self._StateMappingCode[-99]

        return _dict.get(_key) or error

    def _set_state(self, init=False, **kwargs):
        """设置状态"""
        if not init:
            set_state_func = getattr(self, '_set_state__%s' % kwargs.get('name'), False)
            if callable(set_state_func):
                return set_state_func(**kwargs)

        state = self._get_state(**kwargs)
        su = super(TimingBase, self)
        # 状态
        su.__setattr__('_state', state.code)
        # 状态明细
        su.__setattr__('state', state)
        return state.code

    @staticmethod
    def _init_state_check():
        """初始化组合状态判断种类"""
        return {
            'usable': lambda self: abs(self._state) < 10,  # 未启用，仅允许启动事件通过
            'finish': lambda self: abs(self._state) > 90,  # 已完成，不在接受任何事件，等待重新启用
            'break': lambda self: abs(self._state) >= 80,  # 用于监听中打断监听状态
            'normal': lambda self: 10 <= self._state <= 80,  # 正常运行中，允许事件监听
            'mutual': lambda self: 10 <= self._state < 80,  # 正常运行中，允许事件监听与交互
        }

    """状态控制"""

    def _set_state__init(self, start=False, **kwargs):
        """设置状态 - 初始化"""
        self.init(start=start)

    def _set_state__pause(self, value='pause', **kwargs):
        """设置状态 - 暂停"""
        _state = self._state
        if (value == 'pause' and _state != 80) or (value == 'unpause' and _state == 80):
            self._set_state(code=self._pause_state, init=True)
            self._pause_state, _state = _state, self._pause_state

        return _state

    def _set_state__unpause(self, **kwargs):
        """设置状态 - 恢复暂停"""
        return self._set_state__pause(value='unpause')

    """API"""

    def check(self, check_name):
        """判断是否处于某状态"""
        assert check_name.startswith('is_')

        name = check_name.split('is_', maxsplit=1)[-1]
        state = self._get_state(name=name, error=False)
        if state:
            return self.state == state

        return self._StateCheckMulti.get(name, lambda x: False)(self)


from .monitor import Monitor
from .loop import LoopEvent
