from Preset.Model.PartBase import PartBase


class BetterPartUtil:

    def __init__(self, part):
        """
        :param part: PartBase
        :type part: PartBase
        """
        self.part = part

    def broadcast_message(self, message, color='\xc2\xa7f'):
        """
        广播消息
        :param message: 消息
        :type message: str
        :param color: 颜色（可选）
        :type color: str
        """
        self.part.CreateGameComponent().SetNotifyMsg(message, color)

    def broadcast_tip(self, tip):
        """
        广播提示
        :param tip: 提示
        :type tip: str
        """
        self.part.CreateGameComponent().SetTipMessage(tip)

    def broadcast_popup(self, popup, sub):
        """
        广播弹窗提示
        :param popup: 主提示
        :type popup: str
        :param sub: 副提示
        :type sub: str
        """
        self.part.CreateGameComponent().SetPopupNotice(popup, sub)

    def broadcast_actionbar(self, text):
        """
        广播ActionBar
        :param text: 文本
        :type text: str
        """
        self.part.SetCommand("title @a actionbar {}".format(text))

    def broadcast_title_times(self, fadein=20, duration=20, fadeout=5):
        """
        设置Title的显示时间
        :param fadein: 淡入时间
        :type fadein: int
        :param duration: 保持时间
        :type duration: int
        :param fadeout: 淡出时间
        :type fadeout: int
        """
        if fadein is None:
            fadein = 20
        if duration is None:
            duration = 20
        if fadeout is None:
            fadeout = 5
        self.part.SetCommand("title @a times {} {} {}".format(fadein, duration, fadeout))

    def broadcast_title(self, title, sub_title=None, fadein=None, duration=None, fadeout=None):
        """
        广播Title
        :param title: 主标题
        :type title: str
        :param sub_title: 副标题
        :type sub_title: str | None
        :param fadein: 淡入时间
        :type fadein: int | None
        :param duration: 保持时间
        :type duration: int | None
        :param fadeout: 淡出时间
        :type fadeout: int | None
        """
        if fadein is not None or duration is not None or fadeout is not None:
            self.broadcast_title_times(fadein, duration, fadeout)
        if sub_title is not None:
            self.part.SetCommand("title @a subtitle {}".format(sub_title))
        self.part.SetCommand("title @a title {}".format(title))
