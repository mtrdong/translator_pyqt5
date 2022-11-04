# -*- coding: utf-8 -*-
from time import sleep

import httpx
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

from spider.transl_baidu import BaiduTranslate
from spider.transl_google import GoogleTranslate
from spider.transl_youdao import YoudaoTranslate
from utils import baidu_ocr

__all__ = [
    'MouseCheckThread',
    'EngineThread',
    'TranslThread',
    'VoiceThread',
    'BaiduOCRThread',
]


class MouseCheckThread(QThread):
    """鼠标相对悬浮窗位置监测"""
    trigger = pyqtSignal(bool)

    def __init__(self, widget: QWidget):
        super(MouseCheckThread, self).__init__()
        self.widget = widget

    def run(self):
        offset = 20  # 鼠标超出 widget 边缘的距离（单位：像素）
        widget_w = self.widget.width()  # widget 的宽度
        widget_h = self.widget.height()  # widget 的高度
        widget_pos = self.widget.pos()  # widget 左上角的坐标
        while True:
            mouse_pos = QCursor.pos()  # 鼠标当前坐标
            pos = mouse_pos - widget_pos  # 鼠标相对 widget 左上角的坐标
            if not (-offset <= pos.x() <= widget_w + offset and -offset <= pos.y() <= widget_h + offset):
                # 鼠标超出 widget 边缘一定距离后，发送信号并结束循环
                self.trigger.emit(True)
                break
            sleep(0.1)


class EngineThread(QThread):
    """创建翻译引擎对象"""
    trigger = pyqtSignal(dict)

    def __init__(self, select: str):
        super(EngineThread, self).__init__()
        self.select = select

    def run(self):
        result = {'code': 0, 'msg': 'OK', 'obj': None}
        try:
            if self.select == 'youdao':
                obj = YoudaoTranslate()  # 创建有道翻译
            elif self.select == 'google':
                obj = GoogleTranslate()  # 创建谷歌翻译
            else:
                obj = BaiduTranslate()  # 创建百度翻译
        except (httpx.ConnectError, httpx.ProxyError, httpx.ConnectTimeout) as exc:
            result.update({'msg': str(exc)})
        else:
            result.update({'code': 1, 'obj': obj})
        self.trigger.emit(result)  # 发送信号


class TranslThread(QThread):
    """启动翻译"""
    trigger = pyqtSignal(dict)

    def __init__(self, engine, **kwargs):
        super(TranslThread, self).__init__()
        self.engine = engine
        self.kwargs = kwargs

    def run(self):
        result = {'code': 1, 'msg': 'OK'}
        if self.engine.__class__.__name__ == 'YoudaoTranslate':
            self.kwargs.pop('from_lan', None)
        try:
            self.engine.translate(**self.kwargs)
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout) as exc:
            # 翻译失败
            result.update({'code': 0, 'msg': str(exc)})
            self.trigger.emit(result)
        else:
            # 翻译完成
            self.trigger.emit(result)


class VoiceThread(QThread):
    """下载发音"""
    trigger = pyqtSignal(bytes)

    def __init__(self, engine, *args):
        super(VoiceThread, self).__init__()
        self.engine = engine
        self.args = args

    def run(self):
        try:
            data = self.engine.get_tts(*self.args)
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout):
            data = bytes()
        self.trigger.emit(data)  # 发送数据


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
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout):
            text = ''
        self.trigger.emit(text)  # 信号发送文本
