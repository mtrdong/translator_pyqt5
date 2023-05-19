# -*- coding: utf-8 -*-
from time import sleep

import httpx
import pywintypes
import win32api
import win32clipboard
import win32con
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

from common import engine_class
from spider import BaseTranslate
from spider.transl_sougou import SougouTranslate

__all__ = [
    'MouseCheckThread',
    'EngineThread',
    'TranslThread',
    'VoiceThread',
    'OCRThread',
    'ScribeThread',
]


class MouseCheckThread(QThread):
    """鼠标相对悬浮窗位置监测"""
    trigger = pyqtSignal(bool)

    def __init__(self, widget: QWidget):
        super(MouseCheckThread, self).__init__()
        self.widget = widget
        self.quit_flag = False

    def quit(self):
        super().quit()
        self.quit_flag = True

    def run(self):
        offset = 20  # 鼠标超出 widget 边缘的距离（单位：像素）
        widget_w = self.widget.width()  # widget 的宽度
        widget_h = self.widget.height()  # widget 的高度
        widget_pos = self.widget.pos()  # widget 左上角的坐标
        while True:
            # 退出线程时结束循环
            if self.quit_flag:
                break
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
            engine = engine_class.get(self.select)
            obj = engine()  # 实例化翻译引擎
        except (httpx.ConnectError, httpx.ProxyError, httpx.ConnectTimeout) as exc:
            result.update({'msg': str(exc)})
        else:
            result.update({'code': 1, 'obj': obj})
        self.trigger.emit(result)  # 发送信号


class TranslThread(QThread):
    """启动翻译"""
    trigger = pyqtSignal(dict)

    def __init__(self, engine: BaseTranslate, **kwargs):
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

    def __init__(self, engine: BaseTranslate, *args):
        super(VoiceThread, self).__init__()
        self.engine = engine
        self.args = args

    def run(self):
        try:
            data = self.engine.get_tts(*self.args)
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout):
            data = bytes()
        self.trigger.emit(data)  # 发送数据


class OCRThread(QThread):
    """文字识别"""
    trigger = pyqtSignal(str)

    def __init__(self, image: bytes, from_lan):
        super().__init__()
        self.image = image
        self.from_lan = from_lan

    def run(self):
        try:
            # text = baidu_ocr(self.image)  # 百度API，精度较高
            # text = BaiduTranslate().get_ocr(self.image)  # 百度翻译接口，精度较低
            text = SougouTranslate().get_ocr(self.image)  # 搜狗翻译接口，精度适中
        except (AssertionError, httpx.ConnectError, httpx.ConnectTimeout):
            text = ''
        self.trigger.emit(text)  # 信号发送文本


class ScribeThread(QThread):
    """模拟划词"""
    trigger = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.quit_flag = False
    
    def quit(self):
        super().quit()
        self.quit_flag = True

    def run(self):
        """检测到鼠标发生“拖动”事件时，触发一次复制操作"""
        press = False
        while True:
            # 退出线程时结束循环
            if self.quit_flag:
                break
            # 鼠标左键按下检测
            if win32api.GetKeyState(win32con.VK_LBUTTON) < 0 and not press:
                press_x, press_y = win32api.GetCursorPos()
                press = ~press
            # 鼠标左键抬起检测
            elif win32api.GetKeyState(win32con.VK_LBUTTON) >= 0 and press:
                release_x, release_y = win32api.GetCursorPos()
                press = ~press
                # 鼠标移动检测
                if abs(release_x - press_x) >= 5 or abs(release_y - press_y) >= 5:
                    self.send_ctrl_c()
            sleep(0.01)

    def send_ctrl_c(self):
        """ 发送 Ctrl + C 复制
        为防止改变剪切板原有内容，首先保存剪切板原始内容，然后再发送 Ctrl + C
        复制操作发出后，提取复制的内容，然后还原剪切板的原始内容
        最后检查是否复制到文本内容，如果复制到文本则发送给槽函数
        TODO: 鼠标调整某些支持快捷复制整行的“编辑窗体”的大小时，可能会触发复制编辑窗体中光标所在行的内容
        """
        # 先保存剪切板中的原始内容
        win32clipboard.OpenClipboard()
        formats = []
        last_format = 0
        while True:
            next_format = win32clipboard.EnumClipboardFormats(last_format)
            if next_format == 0:
                break
            else:
                formats.append(next_format)
                last_format = next_format
        old_clipboard_data = {}
        for clipboard_format in formats:
            try:
                data = win32clipboard.GetClipboardData(clipboard_format)
                if isinstance(data, bytes):
                    old_clipboard_data[clipboard_format] = data
            except pywintypes.error:
                pass
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()
        # 发送 Ctrl + C 执行复制操作
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('C'), 0, 0, 0)
        win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        sleep(0.1)
        # 从剪切板中获取临时复制的内容，并恢复之前的内容
        win32clipboard.OpenClipboard()
        try:
            new_clipboard_text = win32clipboard.GetClipboardData().strip()
            if new_clipboard_text:
                self.trigger.emit(new_clipboard_text)
        except TypeError:
            pass
        finally:
            # 恢复剪切板中的原始内容
            win32clipboard.EmptyClipboard()
            for clipboard_format, clipboard_data in old_clipboard_data.items():
                win32clipboard.SetClipboardData(clipboard_format, clipboard_data)
            win32clipboard.CloseClipboard()
