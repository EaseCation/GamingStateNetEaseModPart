# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
from state.RootGamingState import RootGamingState


@registerGenericClass("GamingStatePart")
class GamingStatePart(PartBase):
	def __init__(self):
		PartBase.__init__(self)
		# 零件名称
		self.name = "游戏状态机"
		self.root_state = None  # type: RootGamingState | None

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		PartBase.InitClient(self)

	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		PartBase.InitServer(self)
		self.root_state = RootGamingState(self)

	def TickClient(self):
		"""
		@description 客户端的零件对象逻辑驱动入口
		"""
		PartBase.TickClient(self)

	def TickServer(self):
		"""
		@description 服务端的零件对象逻辑驱动入口
		"""
		PartBase.TickServer(self)
		self.root_state.tick()

	def DestroyClient(self):
		"""
		@description 客户端的零件对象销毁逻辑入口
		"""
		PartBase.DestroyClient(self)

	def DestroyServer(self):
		"""
		@description 服务端的零件对象销毁逻辑入口
		"""
		PartBase.DestroyServer(self)
