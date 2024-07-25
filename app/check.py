"""相关校验"""

from . import xxbot


def api_check__is_at(event, *, msg=False, uid=False):
    """检测 at事件"""
    if not uid:
        if event.to_me:
            return True
        uid = event.self_id
    if msg is False:
        msg = event.message

    for m in msg:
        if "[at:qq=%s]" % uid in str(m):
            return True


def api_check__event(event, *, bot_event=False, at_me=True, super_event=False):
    """校验事件"""
    if at_me and not api_check__is_at(event):
        return
    if not xxbot.check_is_gid(event.group_id):
        return

    if bot_event and xxbot.check_is_xxbot(event.user_id):
        return True
    elif not bot_event and super_event and xxbot.check_is_suid(event.user_id):
        return True
    elif not bot_event and not super_event and xxbot.check_is_uid(event.user_id):
        return True


def api_check__xxbot_event(event):
    """校验 xxbot at事件"""
    return api_check__event(event, bot_event=True, at_me=True)


def api_check__app_event(event):
    """校验 功能交互事件"""
    return api_check__event(event, at_me=True)


def api_check__app_super_event(event):
    """校验 超级功能交互事件"""
    return api_check__event(event, at_me=True, super_event=True)


def api_monitor_check__normal_event(event, timing=False, monitor=False):
    """监听校验事件"""
    if timing and not timing.check('is_normal'):
        return True
    if monitor and monitor.check('is_invalid'):
        return True
    if not api_check__xxbot_event(event):
        return True


def api_monitor_check__active_app__xxbot_event(event, timing, monitor):
    """监听校验 已激活功能 - bot反馈事件"""
    return api_monitor_check__normal_event(event, timing, monitor)


def api_monitor_check_and_control__update_state_by_user(event, timing, state):
    """监听校验并控制 用户 修改监听器状态"""
    if not api_check__app_event(event):
        return

    if not isinstance(state, dict):
        state = {'state': state}
    timing(**state)


def api_monitor_check_and_control__update_state_by_xxbot(event, timing, state):
    """监听校验并控制 xxbot 修改监听器状态"""
    if not api_check__xxbot_event(event):
        return

    if not isinstance(state, dict):
        state = {'state': state}
    timing(**state)
