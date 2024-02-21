# -*- coding: utf-8 -*-
from GamingState import GamingState
from ..GamingStatePart import GamingStatePart


class RootGamingState(GamingState):

    def __init__(self, part):
        GamingState.__init__(self)
        self.part = part  # type: GamingStatePart
        self.init()
        self.with_enter(self._on_enter)
        self.with_no_such_next_sub_state(self._on_no_such_next_sub_state)

    def get_part(self):
        return self.part

    def _on_enter(self):
        pass

    def _on_no_such_next_sub_state(self):
        self.get_part().LogInfo("RootGamingState is over.")
        # TODO 对Part进行一些调用