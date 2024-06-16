# -*- coding: utf-8 -*-
from Preset.Model.PartBase import PartBase

replacements = {
    "enter": "\n",
    "black": u"\u00A70",  # Using unicode escape sequence for special character
    "dark-blue": u"\u00A71",
    "dark-green": u"\u00A72",
    "dark-aqua": u"\u00A73",
    "dark-red": u"\u00A74",
    "dark-purple": u"\u00A75",
    "gold": u"\u00A76",
    "gray": u"\u00A77",
    "dark-gray": u"\u00A78",
    "blue": u"\u00A79",
    "green": u"\u00A7a",
    "aqua": u"\u00A7b",
    "red": u"\u00A7c",
    "light-purple": u"\u00A7d",
    "yellow": u"\u00A7e",
    "white": u"\u00A7f",
    "obfuscated": u"\u00A7k",
    "bold": u"\u00A7l",
    "italic": u"\u00A7o",
    "reset": u"\u00A7r",
    # Add additional mappings for icons and other special characters
}

class BetterPartUtil:

    @staticmethod
    def format_text(raw_msg, **args):
        for arg in replacements:
            raw_msg = raw_msg.replace("{" + arg + "}", str(replacements[arg]))
        for arg in args:
            raw_msg = raw_msg.replace("{" + arg + "}", str(args[arg]))
        return raw_msg

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

    def broadcast_title_reset(self):
        """
        重置Title
        """
        self.part.SetCommand("title @a reset")

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
        else:
            self.part.SetCommand("title @a reset")
        if sub_title is not None:
            self.part.SetCommand("title @a subtitle {}".format(sub_title))
        self.part.SetCommand("title @a title {}".format(title))
