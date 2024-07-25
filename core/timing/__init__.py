"""监听器"""

__all__ = [
    'Monitor',  # 监听器
    'LoopEvent',  # 事件循环器
]

from collections import defaultdict, namedtuple

from .. import Config

# 状态
StateInfo = namedtuple('StateInfo', 'name code print')
StateInit = [
    # [0 ~ 10] 未启用，仅允许启动事件
    StateInfo('init', 0, '初始'),

    # [10 ~ 20] 启动中，进行准备工作，期间允许关闭
    StateInfo('auto', -10, '自启动'),
    StateInfo('start', 10, '启动'),

    # [20 ~ 70] 监听执行，期间无法关闭
    StateInfo('running', 20, '执行中'),
    StateInfo('waiting', 30, '等待中'),

    # 执行结束 70 ~ 90 监听结束，期间无法关闭
    StateInfo('skip', 60, '跳过'),
    StateInfo('regular', -60, '计时'),
    StateInfo('pause', 70, '暂停'),
    StateInfo('exit', 80, '退出'),

    # 关闭状态 90 ~ 100 仅允许重新启动
    StateInfo('done', 99, '结束'),
    StateInfo('error', -99, '错误'),
]


class Timing:
    # 初始
    _StateInit = StateInit
    name = False
    state = False
    _state = False
    # 日志信息
    msg = False

    def __init__(self, name, *args, **kwargs):

        # 状态-编码映射
        self._StateMappingCode = {item.code: item for item in self._StateInit}
        # 状态-名称映射
        self._StateMappingName = {item.name: item for item in self._StateInit}
        # 状态反向映射 - 组合
        self._StateCheckMulti = self._init_state_check()

        self.init(name=name)

    def __setattr__(self, key, value):
        if key in ['name', 'state']:
            return

        super(Timing, self).__setattr__(key, value)

    def __call__(self, state=False, *, msg=False, **kwargs):
        self.msg = msg
        if state is not False:
            return self._set_state(name=state, **kwargs)

    def init(self, name=False):
        """初始化"""
        su = super(Timing, self)

        # 容器描述
        su.__setattr__('name', name or getattr(self, 'name', False))
        # 暂停状态
        su.__setattr__('_pause_state', 80)
        # 状态
        self._set_state(name='init', func=False)

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

    def _set_state(self, func=True, **kwargs):
        """设置状态"""
        if func:
            set_state_func = getattr(self, '_set_state__%s' % kwargs.get('name'), False)
            if callable(set_state_func):
                return set_state_func(**kwargs)

        state = self._get_state(**kwargs)
        su = super(Timing, self)
        # 状态
        su.__setattr__('_state', state.code)
        # 状态明细
        su.__setattr__('state', state)
        return state.code

    @staticmethod
    def _init_state_check():
        """初始化组合状态判断种类"""
        return {
            'valid': lambda self: abs(self._state) < 10,  # 有效，仅允许启动事件
            'normal': lambda self: 20 <= abs(self._state) < 90,  # 进行中，进行事件监听
            # 'afoot_mutual': lambda self: 20 <= abs(self._state) < 90,  # 进行中，允许事件交互
            # 'afoot_control': lambda self: 70 <= abs(self._state) < 90,  # 进行中，仅允许控制类事件交互
            # 'break_mutual': lambda self: 70 <= abs(self._state) < 90,  # 监听结束，用于打断监听状态

            # 'normal': lambda self: 20 <= abs(self._state) < 70,  # 进行中，允许事件交互
            # 'mutual': lambda self: 10 <= abs(self._state) < 90,  # 监听执行，允许事件监听与交互

            'break': lambda self: 60 <= abs(self._state),  # 监听结束，用于打断监听状态
            'finish': lambda self: 80 <= abs(self._state),  # 执行完成，单次事件执行完毕退出校验
            'invalid': lambda self: 90 <= abs(self._state),  # 执行完成，任意位置退出校验
        }

    """状态控制"""

    def _set_state__init(self, **kwargs):
        """设置状态 - 初始化"""
        self.init()

    def _set_state__start(self, **kwargs):
        """设置状态 - 启动"""
        if self.check('is_valid'):
            self._set_state(name='start', func=False)
            return self.state
        if self.check('is_exit'):
            # 恢复退出
            self('waiting')

    def _set_state__pause(self, value='pause', **kwargs):
        """设置状态 - 暂停"""
        _state = self._state
        if (value == 'pause' and _state != 80) or (value == 'unpause' and _state == 80):
            self._set_state(code=self._pause_state, func=False)
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
