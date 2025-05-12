# -*- coding: utf-8 -*-
import math
from Preset.Model.Player.PlayerObject import PlayerObject
from mod.common.minecraftEnum import ItemPosType, PlayerUISlot

from ..GamingStatePart import GamingStatePart


class BetterPlayerObject(PlayerObject):
    def __init__(self, part, player_obj):
        PlayerObject.__init__(self)
        self.part = part  # type: GamingStatePart
        for attr_name in dir(player_obj):
            if not attr_name.startswith('__') and not attr_name == 'system' and not callable(
                    getattr(player_obj, attr_name)):
                try:
                    # 尝试设置属性
                    setattr(self, attr_name, getattr(player_obj, attr_name))
                except AttributeError:
                    # 无法设置属性时打印警告信息
                    print("警告: 无法设置属性 '" + attr_name + "'，该属性可能是只读的或与内建属性冲突")
                except Exception as e:
                    # 捕获其他异常并打印
                    print("错误: 在设置属性 '" + attr_name + "' 时发生异常: " + e)

    def clear_title(self):
        self.SetCommand("title @s clear", self.GetPlayerId())

    def send_action_bar(self, action_bar):
        """
        发送ActionBar
        :param action_bar: 文本内容
        :type action_bar: str
        """
        self.SetCommand("title @s actionbar {}".format(action_bar), self.GetPlayerId())

    def set_title_times(self, fadein=20, duration=20, fadeout=5):
        """
        设置Title的显示时间
        :param fadein: 淡入时间
        :type fadein: int
        :param duration: 保持时间
        :type duration: int
        :param fadeout: 淡出时间
        :type fadeout: int
        :return:
        """
        if fadein is None:
            fadein = 20
        if duration is None:
            duration = 20
        if fadeout is None:
            fadeout = 5
        self.SetCommand("title @s times {} {} {}".format(fadein, duration, fadeout), self.GetPlayerId())

    def send_title(self, title, sub_title=None, fadein=None, duration=None, fadeout=None):
        """
        发送Title
        :param title: 文本内容
        :type title: str
        :param sub_title: 富文本
        :type sub_title: str | None
        :param fadein: 淡入时间
        :type fadein: int | None
        :param duration: 保持时间
        :type duration: int | None
        :param fadeout: 淡出时间
        :type fadeout: int | None
        """
        if fadein is not None or duration is not None or fadeout is not None:
            self.set_title_times(fadein, duration, fadeout)

        self.SetCommand("title @s title {}".format(title), self.GetPlayerId())

        if sub_title is not None:
            self.SetCommand("title @s subtitle {}".format(sub_title), self.GetPlayerId())

    def send_message(self, message, color='\xc2\xa7f'):
        """
        发送消息
        :param message: 消息
        :type message: str
        :param color: 颜色（可选）
        :type color: str
        """
        self.NotifyOneMessage(self.GetPlayerId(), message, color)

    def send_tip(self, tip):
        """
        发送Tip提示
        :param tip: 提示
        :type tip: str
        """
        self.SetOneTipMessage(self.GetPlayerId(), tip)

    def send_popup(self, popup, sub=""):
        """
        发送Popup提示
        :param popup: 主提示
        :type popup: str
        :param sub: 副提示
        :type sub: str
        """
        self.CreateGameComponent().SetOnePopupNotice(self.GetPlayerId(), popup, sub)

    def play_client_sound(self, sound, pos, volume=1, pitch=1, loop=False):
        """
        播放客户端声音，不可同时播放多个同sound
        :param sound: 声音ID
        :type sound: str
        :param pos: 播放位置
        :type pos: tuple[float, float, float]
        :param volume: 音量
        :type volume: float
        :param pitch: 音调
        :type pitch: float
        :param loop: 循环
        :type: loop: bool
        """
        if self.isClient:
            import mod.client.extraClientApi as clientApi
            comp = clientApi.GetEngineCompFactory().CreateCustomAudio(self.GetLevelId())
            comp.PlayCustomMusic(sound, pos, volume, pitch, loop, None)
        else:
            data = {
                'player_id': self.GetPlayerId(),
                'sound': sound,
                'pos': pos,
                'volume': volume,
                'pitch': pitch,
                'loop': loop
            }
            self.part.NotifyToClient(self.GetPlayerId(), "S2CPlaySoundEvent", data)

    def play_sound(self, sound, pos, volume=1, pitch=1):
        """
        通过服务端指令播放声音，可同时播放多个同sound
        :param sound: 声音ID
        :type sound: str
        :param pos: 播放位置
        :type pos: tuple[float, float, float]
        :param volume: 音量
        :type volume: float
        :param pitch: 音调
        :type pitch: floatXQXQ
        """

        self.SetCommand("playsound {sound} @s {pos} {volume} {pitch}".format(
            sound=sound,
            pos="{} {} {}".format(pos[0], pos[1], pos[2]),
            volume=volume,
            pitch=pitch
        ), self.GetPlayerId())

    @staticmethod
    def get_note_sound_pitch(key):
        return math.pow(2, (float(key) - 12) / 12)

    def play_note_pling_sound(self, pos, key):
        self.play_sound("note.pling", pos, 1, BetterPlayerObject.get_note_sound_pitch(key))

    def teleport(self, pos, yaw=None, pitch=None, dimension=None):
        if yaw is None:
            yaw = self.GetRot()[1]
        if pitch is None:
            pitch = self.GetRot()[0]

        if dimension is None or self.GetDimensionId() == dimension:
            self.SetPos(pos)
            self.SetRot((pitch, yaw))
        else:
            pos = (pos[0], pos[1] + 3.62, pos[2])  # 这边需要加上眼睛高度（不知道为什么同世界传送就又不用加）
            self.ChangeDimension(dimension, pos)
            self.SetRot((pitch, yaw))

    def set_game_type(self, mode):
        comp_player = self.part.GetApi().GetEngineCompFactory().CreatePlayer(self.GetPlayerId())
        comp_player.SetPlayerGameType(mode)

    def clear_inventory(self):
        comp = self.CreateItemComponent(self.GetPlayerId())

        inv = comp.GetPlayerAllItems(ItemPosType.INVENTORY)

        items_dict_map = {}
        for i in range(len(inv)):
            if inv[i] is not None:
                items_dict_map[(ItemPosType.INVENTORY, i)] = None

        armors = comp.GetPlayerAllItems(ItemPosType.ARMOR)
        for i in range(len(armors)):
            if armors[i] is not None:
                items_dict_map[(ItemPosType.ARMOR, i)] = None

        comp.SetPlayerAllItems(items_dict_map)
        comp.SetPlayerUIItem(self.GetPlayerId(), PlayerUISlot.CursorSelected, None, False)
        for i in range(PlayerUISlot.Crafting2x2Input1, PlayerUISlot.Crafting2x2Input4):
            comp.SetPlayerUIItem(self.GetPlayerId(), i, None, False)
