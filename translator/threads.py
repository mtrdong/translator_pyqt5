# -*- coding: utf-8 -*-
import contextlib
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

from spider.transl_baidu import BaiduTranslate
from spider.transl_google import GoogleTranslate
from spider.transl_youdao import YoudaoTranslate
from utils import baidu_ocr

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
        try:
            if self.select == 'youdao':
                obj = YoudaoTranslate()  # 创建有道翻译
            elif self.select == 'google':
                obj = GoogleTranslate()  # 创建谷歌翻译
            else:
                obj = BaiduTranslate()  # 创建百度翻译
        except:
            obj = None
        self.trigger.emit(obj)  # 发送信号


class StartTransThread(QThread):
    """启动百度翻译获取翻译结果"""
    trigger = pyqtSignal(bool)

    def __init__(self, engine, **kwargs):
        super().__init__()
        self.engine = engine
        self.kwargs = kwargs

    def run(self):
        if self.engine.__class__.__name__ == 'YoudaoTranslate':
            self.kwargs.pop('from_lan', None)
        try:
            self.engine.translate(**self.kwargs)
        except:
            self.trigger.emit(False)  # 翻译失败
        else:
            self.trigger.emit(True)  # 翻译完成


class DownloadVoiceThread(QThread):
    """下载读音"""
    trigger = pyqtSignal(bytes)

    def __init__(self, engine, **kwargs):
        super().__init__()
        self.engine = engine
        self.kwargs = kwargs

    def run(self):
        if self.engine.__class__.__name__ == 'BaiduTranslate':
            self.kwargs.pop('type_', None)
        try:
            data = self.engine.get_tts(**self.kwargs)
        except:
            data = bytes()
        self.trigger.emit(data)  # 信号发送数据


class BaiduOCRThread(QThread):
    """百度图象识别"""
    trigger = pyqtSignal(str)

    def __init__(self, image: bytes):
        super().__init__()
        self.image = image

    def run(self):
        try:
            # text = baidu_ocr(self.image)  # 精度高，推荐
            text = BaiduTranslate().get_ocr(self.image)  # 精度低，备用
        except:
            text = ''
        self.trigger.emit(text)  # 信号发送文本
