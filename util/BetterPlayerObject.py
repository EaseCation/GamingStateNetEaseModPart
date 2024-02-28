import math

from Preset.Model.Player.PlayerObject import PlayerObject
from mod.common.minecraftEnum import ItemPosType, PlayerUISlot

from ..GamingStatePart import GamingStatePart

class BetterPlayerObject(PlayerObject):
    def __init__(self, part, player_obj):
        PlayerObject.__init__(self)
        self.part = part  # type: GamingStatePart
        for attr_name, attr_value in vars(player_obj).items():
            # 使用setattr将每个属性赋值给当前对象
            setattr(self, attr_name, attr_value)

    def clear_title(self):
        self.SetCommand("title {} clear".format(self.GetName()))

    def send_action_bar(self, action_bar):
        """
        发送ActionBar
        :param action_bar: 文本内容
        :type action_bar: str
        """
        self.SetCommand("title {} actionbar {}".format(self.GetName(), action_bar))

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
        self.SetCommand("title {} times {} {} {}".format(self.GetName(), fadein, duration, fadeout))

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
        else:
            self.part.SetCommand("title {} reset".format(self.GetName()))
        if sub_title is not None:
            self.SetCommand("title {} subtitle {}".format(self.GetName(), sub_title))
        self.SetCommand("title {} title {}".format(self.GetName(), title))

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
        :type pitch: float
        """
        self.SetCommand("playsound {sound} {player} {pos} {volume} {pitch}".format(
            sound = sound,
            player = self.GetName(),
            pos = "{} {} {}".format(pos[0], pos[1], pos[2]),
            volume = volume,
            pitch = pitch
        ))

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
            pos = (pos[0], pos[1] + 1.62, pos[2])  # 这边需要加上眼睛高度（不知道为什么同世界传送就又不用加）
            self.ChangeDimension(dimension, pos)
            self.SetRot((pitch, yaw))

    def set_game_type(self, mode):
        comp_player = self.part.GetApi().GetEngineCompFactory().CreatePlayer(self.GetPlayerId())
        comp_player.SetPlayerGameType(mode)

    def clear_inventory(self):
        comp = self.CreateItemComponent(self.GetPlayerId())

        items_dict_map = {}
        for i in range(36):
            items_dict_map[(ItemPosType.INVENTORY, i)] = None

        comp.SetPlayerAllItems(items_dict_map)
        comp.SetPlayerUIItem(self.GetPlayerId(), PlayerUISlot.CursorSelected, None, False)
        for i in range(PlayerUISlot.Crafting2x2Input1, PlayerUISlot.Crafting2x2Input4):
            comp.SetPlayerUIItem(self.GetPlayerId(), i, None, False)