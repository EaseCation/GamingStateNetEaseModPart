# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase
from Preset.Model.GameObject import registerGenericClass
# 自定义import可千万不能写在顶上，而是要写在下面，巨大的坑啊


@registerGenericClass("GamingStatePart")
class GamingStatePart(PartBase):

	def __init__(self):
		PartBase.__init__(self)
		from util.BetterPartUtil import BetterPartUtil
		# 零件名称
		self.name = "游戏状态机"
		self.root_state = None  # type: RootGamingState | None
		self.better_util = BetterPartUtil(self)
		self.cached_better_players = {}  # type: dict[str, BetterPlayerObject]

	def InitClient(self):
		"""
		@description 客户端的零件对象初始化入口
		"""
		PartBase.InitClient(self)

	def InitServer(self):
		"""
		@description 服务端的零件对象初始化入口
		"""
		from state.RootGamingState import RootGamingState
		PartBase.InitServer(self)
		self.root_state = RootGamingState(self)
		self.ListenForEngineEvent('DelServerPlayerEvent', self, self.server_on_del_server_player)

	def server_on_del_server_player(self, args):
		"""
		@description 服务端玩家离开游戏事件
		"""
		self.cached_better_players.pop(args['id'])

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

	def get_better_player_obj(self, player_id):
		"""
		获取玩家对象
		:type player_id: str
		:rtype BetterPlayerObject
		"""
		from util.BetterPlayerObject import BetterPlayerObject
		player_obj = self.cached_better_players.get(player_id)
		if player_obj is None:
			player_obj = BetterPlayerObject(self.GetPlayerObject(player_id))
			self.cached_better_players[player_id] = player_obj
		return player_obj
