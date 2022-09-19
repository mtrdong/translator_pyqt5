# -*- coding: utf-8 -*-
import contextlib
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

from spider.transl_baidu import BaiduTranslate
from spider.transl_google import GoogleTranslate
from spider.transl_youdao import YoudaoTranslate
from utils import check_network, baidu_ocr

__all__ = [
    'MouseCheckThread',
    'TranslThread',
    'StartTransThread',
    'DownloadVoiceThread',
    'BaiduOCRThread',
]


class MouseCheckThread(QThread):
    """鼠标相对悬浮窗位置监测"""
    trigger = pyqtSignal(bool)

    def __init__(self, widget: QWidget):
        super().__init__()
        self.widget = widget

    def run(self):
        widget_pos = self.widget.pos()
        with contextlib.suppress(Exception):
            while True:
                mouse_pos = QCursor.pos()
                pos = mouse_pos - widget_pos
                if not (-20 <= pos.x() <= self.widget.width() + 20 and -20 <= pos.y() <= self.widget.height() + 20):
                    # 鼠标超出悬浮窗范围，发送信号并结束循环
                    self.trigger.emit(True)
                    break
                sleep(0.1)


class TranslThread(QThread):
    """创建翻译引擎对象"""
    trigger = pyqtSignal(object)

    def __init__(self, select: str):
        super().__init__()
        self.select = select

    def run(self):
        if not check_network():  # 检查网络连接
            obj = None
        elif self.select == 'youdao':
            obj = YoudaoTranslate()  # 创建有道翻译
        elif self.select == 'google':
            obj = GoogleTranslate()  # 创建谷歌翻译
        else:
            obj = BaiduTranslate()  # 创建百度翻译
        self.trigger.emit(obj)  # 发送信号


class StartTransThread(QThread):
    """启动百度翻译获取翻译结果"""
    trigger = pyqtSignal(dict)

    def __init__(self, query: str, to_str: str, from_str: str = None):
        super().__init__()
        self.query = query
        self.to_str = to_str
        self.from_str = from_str

    def run(self):
        try:
            data = BaiduTranslate().start_trans(self.query, self.to_str, self.from_str)
        except:
            data = dict()
        self.trigger.emit(data)  # 信号发送翻译结果


class DownloadVoiceThread(QThread):
    """下载单词发音"""
    trigger = pyqtSignal(bytes)

    def __init__(self, lan: str, text: str):
        super().__init__()
        self.lan = lan
        self.text = text

    def run(self):
        data = BaiduTranslate().get_tts(self.lan, self.text)
        if data is None:
            data = bytes()
        self.trigger.emit(data)  # 信号发送数据


class BaiduOCRThread(QThread):
    """百度图象识别"""
    trigger = pyqtSignal(str)

    def __init__(self, image: bytes):
        super().__init__()
        self.image = image

    def run(self):
        # text = baidu_ocr(self.image)  # 精度高，推荐
        text = BaiduTranslate().get_str_from_img(self.image)  # 精度低，备用
        self.trigger.emit(text)  # 信号发送文本
