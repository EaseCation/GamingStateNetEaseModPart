from Preset.Model.Player.PlayerObject import PlayerObject

class BetterPlayerObject(PlayerObject):
    def __init__(self, player_obj):
        PlayerObject.__init__(self)
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