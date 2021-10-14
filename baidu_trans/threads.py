import contextlib
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect, QApplication

from baidu_trans_spider import BaiDuTrans

__all__ = [
    'MouseCheckThread',
    'FadeInThread',
    'BaiduTransThread',
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
            while 1:
                mouse_pos = QCursor.pos()
                pos = mouse_pos - widget_pos
                if not (-20 <= pos.x() <= self.widget.width() + 20 and -20 <= pos.y() <= self.widget.height() + 20):
                    # 鼠标超出悬浮窗范围，发送信号并结束循环
                    self.trigger.emit(True)
                    break


class FadeInThread(QThread):
    """部件淡入效果"""
    trigger = pyqtSignal(bool)

    def __init__(self, widget: QWidget):
        super().__init__()
        self.widget = widget
        self.opacity = QGraphicsOpacityEffect()

    def run(self):
        for i in range(0, 11):
            self.opacity.setOpacity(i / 10)
            self.widget.setGraphicsEffect(self.opacity)
            QApplication.processEvents()
            sleep(0.01)
        self.trigger.emit(True)


class BaiduTransThread(QThread):
    """创建百度翻译对象"""
    trigger = pyqtSignal(object)

    def run(self):
        try:
            baidu_trans = BaiDuTrans()
        except:
            baidu_trans = None
        self.trigger.emit(baidu_trans)  # 信号发送百度翻译对象


class StartTransThread(QThread):
    """启动百度翻译获取翻译结果"""
    trigger = pyqtSignal(dict)

    def __init__(self, query: str, to_str: str):
        super().__init__()
        self.query = query
        self.to_str = to_str

    def run(self):
        try:
            data = BaiDuTrans().start_trans(self.query, self.to_str)
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
        data = BaiDuTrans().get_tts(self.lan, self.text)
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
        text = BaiDuTrans().get_str_from_img(self.image)  # 精度低，备用
        self.trigger.emit(text)  # 信号发送文本
