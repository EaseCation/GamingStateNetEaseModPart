# -*- coding: utf-8 -*-
from collections import OrderedDict


class GamingState:

    def __init__(self):
        self.parent = None  # type: GamingState | None
        self.current_sub_state = None  # type: str | None
        self.loop = False  # type: bool

        # 子状态机，是一个有序dict
        self.sub_states = OrderedDict()  # type: dict[str, GamingState]
        # 监听器
        self.listened_events = dict()  # type: dict[tuple[str, str, str], list[callable]] # (namespace, system_name, event_name) -> callback

        # 状态初始化时的回调
        self.callbacks_init = list()  # type: list[callable]
        # 状态开始时的回调
        self.callbacks_enter = list()  # type: list[callable]
        # 状态结束时的回调
        self.callbacks_exit = list()  # type: list[callable]
        # tick回调
        self.callbacks_tick = list()  # type: list[callable]
        # 当没有下一个子状态时回调
        self.callbacks_no_such_next_sub_state = list()  # type: list[callable]

    # ====== 生命周期方法（不要轻易override） ======

    def init(self):
        """
        @description 创建状态
        """
        for callback in self.callbacks_init:
            try:
                callback()
            except Exception as e:
                self.get_part().LogError("GamingState.init callback error: " + str(e))

    def enter(self):
        """
        @description 进入状态（不推荐override，而是调用with_enter）
        """
        self.get_part().LogDebug("GamingState.enter with callbacks: {}".format(str(self.callbacks_enter)))
        for callback in self.callbacks_enter:
            try:
                callback()
            except Exception as e:
                self.get_part().LogError("GamingState.enter callback error: " + str(e))
        # 如果该状态机包含子状态，那么自动进入子状态
        if len(self.sub_states) > 0:
            self.next_sub_state()

    def exit(self):
        """
        @description 退出状态（不推荐override，而是调用with_exit）
        """
        for callback in self.callbacks_exit:
            try:
                callback()
            except Exception as e:
                self.get_part().LogError("GamingState.exit callback error: " + str(e))

    def tick(self):
        """
        @description 逻辑驱动（不推荐override，而是调用with_tick）
        """
        if self.current_sub_state is not None:
            sub_state = self.sub_states[self.current_sub_state]
            if sub_state != self:
                sub_state.tick()
            else:
                self.get_part().LogError("尝试tick递归的sub_state: {}".format(self.current_sub_state))
        for callback in self.callbacks_tick:
            try:
                callback()
            except Exception as e:
                self.get_part().LogError("GamingState.tick callback error: " + str(e))

    def event_call(self, namespace, system_name, event_name, *args):
        """
        @description 监听器被调用
        :param namespace: 命名空间
        :type namespace: str
        :param system_name: 系统名称
        :type system_name: str
        :param event_name: 事件名称
        :type event_name: str
        :param args: 参数
        """
        if event_name in self.listened_events:
            for callback in self.listened_events[(namespace, system_name, event_name)]:
                try:
                    callback(*args)
                except Exception as e:
                    self.get_part().LogError("GamingState.event_call callback error: " + str(e))
        if self.current_sub_state is not None:
            self.sub_states[self.current_sub_state].event_call(namespace, system_name, event_name, *args)

    # ====== API 方法 ======

    def get_part(self):
        """
        获取零件Part实例
        :rtype: GamingStatePart
        """
        if self.parent is not None:
            return self.parent.get_part()
        else:
            return None

    def listen_engine_event(self, event_name, callback):
        """
        @description 监听引擎事件
        :param event_name: 事件名称
        :type event_name: str
        :param callback: 回调函数(self, args...)
        :type callback: callable
        """
        self.listen_event("Minecraft", "Engine", event_name, callback)

    def listen_preset_event(self, event_name, callback):
        """
        @description 监听预设事件
        :param event_name: 事件名称
        :type event_name: str
        :param callback: 回调函数(self, args...)
        :type callback: callable
        """
        self.listen_event("Minecraft", "preset", event_name, callback)

    def listen_event(self, namespace, system_name, event_name, callback):
        """
        @description 监听引擎事件
        :param namespace: 命名空间
        :type namespace: str
        :param system_name: 系统名称
        :type system_name: str
        :param event_name: 事件名称
        :type event_name: str
        :param callback: 回调函数(self, args...)
        :type callback: callable
        """
        if event_name not in self.listened_events:
            self.listened_events[(namespace, system_name, event_name)] = list()
        self.listened_events[(namespace, system_name, event_name)].append(callback)
        self.get_part().ListenForEvent(namespace, system_name, event_name, self, callback)

    def add_sub_state(self, name, state_supplier):
        """
        @description 添加子状态
        :param name: 子状态名称
        :type name: str
        :param state_supplier: 一个返回子状态对象的lambda函数，例如：lambda: IdleState()
        :type state_supplier: callable
        """
        if name in self.sub_states:
            raise ValueError("添加子状态时，状态名 {} 已存在".format(name))
        state = state_supplier()  # type: GamingState
        state.init()
        self.sub_states[name] = state
        state.parent = self

    def remove_sub_state(self, state_name):
        """
        @description 移除子状态
        :param state_name: 子状态名称
        :type state_name: str
        :return: 被移除的子状态
        :rtype: GamingState | None
        """
        # 如果移除了一个正在进行中的状态，则自动切换到下一状态
        if self.current_sub_state == state_name:
            self.next_sub_state()
        return self.sub_states.pop(state_name)

    def get_current_sub_state(self):
        """
        @description 获取当前子状态
        :return: 当前子状态
        :rtype: GamingState | None
        """
        return self.sub_states[self.current_sub_state]

    def is_state_running(self):
        """
        @description 检查父状态的当前子状态是否是自己（也就是说，当前状态是正在运行生效）
        """
        if self.parent is None:
            return True
        elif self.parent.current_sub_state is None:
            return False
        return self.parent.sub_states[self.parent.current_sub_state] == self

    def get_runtime_state_name(self):
        """
        @description 获取自己正在运行的状态名称
        :return: 状态名称 | 如果没有运行则返回None
        :rtype: str | None
        """
        if self.parent is not None and self.is_state_running():
            return self.parent.current_sub_state
        return None

    def next_sub_state(self):
        """
        @description 进入下一个子状态
        """
        keys = list(self.sub_states.keys())

        if self.current_sub_state is None:
            if len(keys) > 0:
                self.current_sub_state = keys[0]
                state = self.sub_states[self.current_sub_state]
                self.get_part().LogDebug("next_sub_state: " + self.current_sub_state)
                state.enter()
            else:
                for callback in self.callbacks_no_such_next_sub_state:
                    callback()
        else:
            current = self.sub_states[self.current_sub_state]
            if current is None:
                raise ValueError("Current states {} is missing".format(self.current_sub_state))
            index = keys.index(self.current_sub_state)
            if index + 1 < len(keys):
                current.exit()
                self.current_sub_state = keys[index + 1]
                state = self.sub_states[self.current_sub_state]
                self.get_part().LogDebug("next_sub_state: " + self.current_sub_state)
                state.enter()
            else:
                if self.loop:
                    current.exit()
                    self.current_sub_state = None
                    self.next_sub_state()
                else:
                    for callback in self.callbacks_no_such_next_sub_state:
                        callback()
                    if self.is_state_running() and self.current_sub_state == keys[
                        -1]:  # 这边需要判断进行了callback后，目前状态机是否被改变，如果被改变，表示在callback中修改了状态
                        current.exit()
                        if self.parent is not None:
                            self.parent.next_sub_state()

    def toggle_sub_state(self, state_name):
        """
        @description 切换子状态
        :param state_name: 子状态名称
        :type state_name: str
        """
        if state_name not in self.sub_states:
            raise ValueError("State {} not found".format(state_name))
        if self.current_sub_state is not None:
            self.sub_states[self.current_sub_state].exit()
        self.current_sub_state = state_name
        self.sub_states[state_name].enter()

    def set_loop(self, loop=True):
        """
        @description 设置是否循环
        :param loop: 是否循环
        :type loop: bool
        """
        self.loop = loop

    # ====== withCallback 附加回调逻辑 ======

    def with_init(self, callback):
        """
        @description 添加状态初始化时的回调
        :param callback: 回调函数，例如：lambda: print("init")
        :type callback: callable
        """
        self.callbacks_init.append(callback)

    def with_enter(self, callback):
        """
        @description 添加状态开始时的回调
        @param callback: 回调函数，例如：lambda: print("enter")
        :type callback: callable
        """
        self.callbacks_enter.append(callback)

    def with_exit(self, callback):
        """
        @description 添加状态结束时的回调
        :param callback: 回调函数，例如：lambda: print("exit")
        :type callback: callable
        """
        self.callbacks_exit.append(callback)

    def with_tick(self, callback):
        """
        @description 添加tick回调
        :param callback: 回调函数，例如：lambda: print("tick")
        :type callback: callable
        """
        self.callbacks_tick.append(callback)

    def with_no_such_next_sub_state(self, callback):
        """
        @description 添加没有下一个子状态时的回调
        :param callback: 回调函数，例如：lambda: print("no next sub states")
        :type callback: callable
        """
        self.callbacks_no_such_next_sub_state.append(callback)
