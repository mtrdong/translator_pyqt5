# -*- coding: utf-8 -*-
import base64
import os
import sys
from time import sleep

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtMultimedia
from PyQt5 import QtWidgets
from system_hotkey import SystemHotkey, user32
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE, SWP_SHOWWINDOW, HWND_NOTOPMOST, VK_F1
from win32gui import SetWindowPos

from common import engine_lang, engine_name
from res import widgets_zh_CN_qm, favicon_ico
from spider import BaseTranslate
from spider.transl_youdao import youdao_lang
from threads import *
from ui.MainWindow_ui import Ui_MainWindow
from utils import b64decode_json, generate_output
from widgets import FramelessWidget
from window.FloatWindow import FloatWindow
from window.ScreenshotWindow import ScreenshotWindow

# 窗口最大高度
MAX_H = 682


class MainWindow(FramelessWidget, Ui_MainWindow):
    """主窗口"""
    def __init__(self, *args, **kwargs):
        # 窗口设置
        super().__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(favicon_ico))
        font = QtGui.QFont('微软雅黑')
        font.setPixelSize(14)
        self.setFont(font)
        self.setupUi(self)
        self.resize(self.minimumSize())
        # 初始化UI
        self.initUI()
        # 语音和复制按钮点击事件
        self.pushButton_8.clicked.connect(self.voiceButtonClicked)
        self.pushButton_10.clicked.connect(self.voiceButtonClicked)
        self.pushButton_9.clicked.connect(self.copyButtonClicked)
        self.pushButton_11.clicked.connect(self.copyButtonClicked)
        # 底部输出框链接点击事件
        self.textBrowser_2.anchorClicked.connect(self.anchorClicked)
        # 下拉列表初始化
        self.comboBox.addItems(engine_name.keys())
        self.comboBox.setCurrentIndex(0)
        # TODO 谷歌翻译已挂，暂时禁用
        google_idx = list(engine_name.values()).index('google')
        self.comboBox.setItemData(google_idx, 0, QtCore.Qt.UserRole - 1)
        # TODO end
        self.comboBox.currentIndexChanged.connect(self.comboBoxCurrentIndexChanged)
        self.source_lan = None  # 源语言代码
        self.target_lan = None  # 目标语言代码
        self.comboBox_2DisableIndex = 0  # 源语言下拉列表禁用的的索引
        self.comboBox_3DisableIndex = 0  # 目标语言下拉列表禁用的的索引
        self.comboBox_2.currentIndexChanged.connect(self.comboBox_2CurrentIndexChanged)
        self.comboBox_3.currentIndexChanged.connect(self.comboBox_3CurrentIndexChanged)
        self.setLangItems()  # 设置源语言/目标语言下拉选项
        # 通过线程创建翻译引擎对象
        self.transl_engine: BaseTranslate = ...  # 翻译引擎对象
        self.getTranslEngine()  # 创建翻译引擎对象
        # 监听剪切板。开启监听时，当剪切板内容发生变化时，自动获取剪切板文本发起翻译（伪划词翻译）
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clipboardChanged)
        self.clipboard_flag = False  # 监听标志（True-开启监听；False-关闭监听）
        # 翻译定时器。输入框内容发生变化时，延时一定时间后自动发起翻译
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.startTransl)
        # 翻译状态（True-正在翻译；False-翻译结束）。当有正在进行的翻译时，不允许发起二次翻译
        self.transl_started = False
        # 注册热键
        self.registerHotKey()
        # 窗口剧中显示
        self.center()

    @QtCore.pyqtSlot()
    def on_checkBox_clicked(self):
        """ 复选按钮状态变更
        1. 勾选状态开启复制翻译
        2. 取消勾选关闭复制翻译
        """
        if self.checkBox.isChecked():
            # 翻译引擎未准备就绪时，弹窗提示并终止开启划词翻译
            if self.transl_engine is None:
                self.checkBox.setChecked(False)
                QtWidgets.QMessageBox.information(self, '翻译引擎始化中', '翻译引擎正在初始化中，请稍后重试！')
                return None
            self.clipboard_flag = True
        else:
            self.clipboard_flag = False

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        """ 点击置顶按钮
        设置窗口置顶/取消置顶
        """
        if self.pushButton.isChecked():
            SetWindowPos(int(self.winId()), HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        else:
            SetWindowPos(int(self.winId()), HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)

    @QtCore.pyqtSlot()
    def on_pushButton_4_clicked(self):
        """ 点击截图翻译按钮
        隐藏主窗口，启动截屏
        """
        # 翻译引擎未准备就绪时，弹窗提示并终止启动截图翻译
        if self.transl_engine is None:
            QtWidgets.QMessageBox.information(self, '翻译引擎始化中', '翻译引擎正在初始化中，请稍后重试！')
            return None

        # 防止重复创建截屏窗口
        if not hasattr(self, 'screenshot_window'):

            def completed(img_data):
                """截屏完成，显示主窗口并启动识别翻译"""
                self.activateWindow()  # 主窗口变为活动窗口
                self.showNormal()  # 显示主窗口
                QtWidgets.QApplication.processEvents()  # 刷新界面
                if img_data:
                    # 识别图片中的文本并发起翻译
                    self.ocr(img_data)

            def destroyed():
                """回收截图窗口"""
                del self.screenshot_window

            self.hide()  # 隐藏主窗口
            self.screenshot_window = ScreenshotWindow()  # 创建截屏窗口
            self.screenshot_window.completed.connect(completed)
            self.screenshot_window.destroyed.connect(destroyed)
            self.screenshot_window.show()  # 显示截屏窗口

    @QtCore.pyqtSlot()
    def on_pushButton_5_clicked(self):
        """ 翻译按钮状态变更
        点击翻译按钮立即发起翻译
        """
        self.startTransl()

    @QtCore.pyqtSlot()
    def on_pushButton_6_clicked(self):
        """ 点击语言对调按钮
        调换源语言与目标语言
        """
        if engine_name.get(self.comboBox.currentText()) != 'youdao':
            if self.source_lan and self.source_lan != 'auto':
                combobox_2_index = self.comboBox_2.currentIndex()
                combobox_3_index = self.comboBox_3.currentIndex()
                # 保持源语言信号连接，暂停目标语言信号连接，防止自动触发两次翻译
                self.comboBox_2.setCurrentIndex(combobox_3_index + 1)
                self.comboBox_3.blockSignals(True)  # 关闭信号连接
                self.comboBox_3.setCurrentIndex(combobox_2_index - 1)
                self.comboBox_3.blockSignals(False)  # 恢复信号连接
                self.refreshComboBoxItems()

    @QtCore.pyqtSlot()
    def on_textEdit_textChanged(self):
        """ 文本输入框内容变更
        文本输入框内容发生变化时对内容进行检查
        如果输入内容为图片，则对图片进行识别并发起翻译
        如果输入内容为文本，则设置一个定时器，定时结束时自动发起翻译
        """
        self.timer.stop()  # 每当文本框内容发生变化时停止定时翻译，防止连续输入触发多次定时翻译
        text = self.textEdit.toPlainText().strip()
        # 有内容输入时，对输入内容进行检查
        if text:
            # 翻译引擎未准备就绪时，弹窗提示并终止操作
            if self.transl_engine is None:
                QtWidgets.QMessageBox.information(self, '翻译引擎始化中', '翻译引擎正在初始化中，请稍后重试！')
            # 输入文件时，如果输入的是图片则进行识别翻译（多张图片只取一张），否则弹窗提示
            elif text.find('file:///') == 0 or text.find('base64:///') == 0:
                file_list = text.split('\n')
                for file in file_list:
                    label, string = file.split(':///')
                    if label == 'base64':
                        img_data = base64.b64decode(string)
                        break
                    elif os.path.splitext(string)[-1].lower() in ['.jpg', '.png']:
                        with open(string, 'rb') as f:
                            img_data = f.read()
                        break
                else:
                    self.textEdit.clear()
                    QtWidgets.QMessageBox.information(self, '提示', '仅支持 jpg 或 png 格式的图片')
                    return None
                self.ocr(img_data)  # 识别图片中的文本并发起翻译
            # 输入文本时，启动定时翻译对输入的文本进行翻译
            else:
                self.timer.start(1000)  # 启动定时翻译
        # 输入内容为空或空白字符时，收起输出文本框
        else:
            self.textBrowser.clear()  # 清空输出框内容
            self.textBrowser_2.clear()
            self.updateUI()  # 收起输出文本框
        # 输入框内容不为空时显示清空按钮，否则隐藏清空按钮
        if self.textEdit.toPlainText():
            self.pushButton_7.show()
        else:
            self.pushButton_7.hide()

    def clipboardChanged(self):
        """ 剪切板数据变更
        开启复制翻译时，获取剪切板内容并发起翻译
        """
        mime_data = self.clipboard.mimeData()
        text = mime_data.text().strip()
        # 满足以下条件时，获取剪切板的内容进行翻译，并输出到悬浮窗
        # 1. 开启了“划词翻译”
        # 2. 没有正在进行中的翻译任务
        # 3. 剪切板的内容为纯文本，且不是纯空白字符
        if self.clipboard_flag and not self.transl_started and mime_data.hasFormat('text/plain') and text:

            if not hasattr(self, 'float_window'):

                def pushButtonClicked(s):
                    """从悬浮窗口转到主窗口"""
                    self.float_window.deleteLater()
                    self.activateWindow()
                    self.showNormal()
                    self.textEdit.setPlainText(s)
                    self.startTransl()
                    QtWidgets.QApplication.processEvents()

                def textBrowserAnchorClicked(s):
                    """点击悬浮窗的单词时通过主程序进行翻译，再输出到悬浮窗"""
                    self.float_window.setQuery(s)
                    self.startTransl(s, output=1)

                def destroyed():
                    """回收悬浮窗口"""
                    del self.float_window

                # 显示悬浮窗
                self.float_window = FloatWindow(text)  # 创建悬浮窗
                self.float_window.pushButtonClicked.connect(pushButtonClicked)
                self.float_window.radioButtonClicked.connect(self.checkBox.click)
                self.float_window.textBrowserAnchorClicked.connect(textBrowserAnchorClicked)
                self.float_window.destroyed.connect(destroyed)
                self.float_window.show()
            else:
                self.float_window.setQuery(text)

            # 发起翻译
            self.startTransl(text, output=1)

    def getTranslEngine(self):
        """通过线程创建翻译引擎对象"""
        # 退出之前的线程，并重置翻译引擎
        if hasattr(self, 'engine_thread'):
            self.engine_thread.disconnect()
            self.engine_thread.quit()
        self.transl_engine = None

        def trigger(result):
            """设置翻译引擎"""
            if result['code'] == 0:
                QtWidgets.QMessageBox.information(self, '翻译引擎初始化失败', '翻译引擎初始化失败，请尝试切换翻译引擎或检查网络是否正常！')
                return None
            self.transl_engine = result['obj']
            # 切换引擎后如果输入框有内容则发起翻译
            if self.textEdit.toPlainText():
                self.startTransl()

        self.engine_thread = EngineThread(engine_name.get(self.comboBox.currentText()))
        self.engine_thread.trigger.connect(trigger)
        self.engine_thread.start()

    def setLangItems(self):
        """设置源语言和目标语言下拉列表"""
        engine_val = engine_name.get(self.comboBox.currentText())
        if engine_val == 'youdao':
            youdao_keys = list(youdao_lang.keys())
            source_lan_items = [youdao_keys.pop(0)]
            target_lan_items = youdao_keys
        else:
            source_lan_items = list(engine_lang[engine_val].keys())
            target_lan_items = source_lan_items.copy()
            target_lan_items.pop(0)
        # 源语言下拉列表
        self.comboBox_2.blockSignals(True)  # 关闭信号连接
        self.comboBox_2.clear()
        self.comboBox_2.addItems(source_lan_items)
        self.comboBox_2.setCurrentIndex(0)
        self.comboBox_2.blockSignals(False)  # 恢复信号连接
        # 目标语言下拉列表
        self.comboBox_3.blockSignals(True)
        self.comboBox_3.clear()
        self.comboBox_3.addItems(target_lan_items)
        self.comboBox_3.setCurrentIndex(0)
        self.comboBox_3.blockSignals(False)
        # 设置源语言和目标语言，并刷新源语言/目标语言下拉列表禁用选项
        self.source_lan = engine_lang[engine_val][source_lan_items[0]]
        self.target_lan = engine_lang[engine_val][target_lan_items[0]]
        self.refreshComboBoxItems()

    def comboBoxCurrentIndexChanged(self):
        """ 翻译引擎下拉列表索引变更
        切换翻译引擎时重新发起翻译
        """
        self.getTranslEngine()
        self.setLangItems()

    def comboBox_2CurrentIndexChanged(self):
        """ 源语言下拉列表索引变更
        1. 获取源语言代码
        2. 刷新语言下拉禁用选项
        3. 发起翻译
        """
        engine_val = engine_name.get(self.comboBox.currentText())
        self.source_lan = engine_lang[engine_val][self.comboBox_2.currentText()]
        if engine_val == 'youdao':
            # 0--中译日（默认）；1--日译中
            index = self.comboBox_2.currentIndex()
            self.output(bool(index))
        else:
            if self.textEdit.toPlainText():
                self.startTransl()
        self.refreshComboBoxItems()

    def comboBox_3CurrentIndexChanged(self):
        """ 目标语言下拉列表索引变更
        1. 获取目标语言代码
        2. 刷新语言下拉禁用选项
        3. 发起翻译
        """
        engine_val = engine_name.get(self.comboBox.currentText())
        self.target_lan = engine_lang[engine_val][self.comboBox_3.currentText()]
        if self.textEdit.toPlainText():
            self.startTransl()
        if engine_val != 'youdao':
            self.refreshComboBoxItems()

    def refreshComboBoxItems(self):
        """刷新源语言/目标语言下拉禁用选项"""
        if engine_name.get(self.comboBox.currentText()) == 'youdao':
            self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 1 | 32, QtCore.Qt.UserRole - 1)
            self.comboBox_2DisableIndex = self.comboBox_2.currentIndex()
            self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 0, QtCore.Qt.UserRole - 1)
        else:
            # 解除上次禁用选项
            self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 1 | 32, QtCore.Qt.UserRole - 1)
            self.comboBox_3.setItemData(self.comboBox_3DisableIndex, 1 | 32, QtCore.Qt.UserRole - 1)
            if self.source_lan and self.source_lan != 'auto':  # 源语言下拉选项为非“自动检测”选项
                self.comboBox_2DisableIndex = self.comboBox_3.currentIndex() + 1
                self.comboBox_3DisableIndex = self.comboBox_2.currentIndex() - 1
                self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 0, QtCore.Qt.UserRole - 1)
                self.comboBox_3.setItemData(self.comboBox_3DisableIndex, 0, QtCore.Qt.UserRole - 1)
            else:
                self.comboBox_2DisableIndex = self.comboBox_3.currentIndex() + 1
                self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 0, QtCore.Qt.UserRole - 1)

    def updateComboBoxItems(self):
        """更新下拉列表"""
        # 有道词典切换目标语言为“中日”时，由于翻译结果会有“中译日”和“日译中”两种
        # 因此源语言选项修改为 ['中文 >> 日语', '日语 >> 中文']，用于切换输出结果
        if engine_name.get(self.comboBox.currentText()) == 'youdao':
            if youdao_lang.get(self.comboBox_3.currentText()) == 'ja' and self.transl_engine.reverse_flag:
                items = ['中文 >> 日语', '日语 >> 中文']
            else:
                items = [list(youdao_lang.keys())[0]]
            self.comboBox_2.blockSignals(True)  # 关闭信号连接
            self.comboBox_2.clear()
            self.comboBox_2.addItems(items)
            self.comboBox_2.setCurrentIndex(0)
            self.refreshComboBoxItems()
            self.comboBox_2.blockSignals(False)  # 恢复信号连接
        # 自动纠正目标语言选项
        to_lan = self.transl_engine.to_lan
        if self.target_lan != to_lan:
            self.target_lan = to_lan
            index = list(engine_lang[engine_name[self.comboBox.currentText()]].values()).index(to_lan) - 1
            self.comboBox_3.blockSignals(True)
            self.comboBox_3.setCurrentIndex(index)
            self.refreshComboBoxItems()
            self.comboBox_3.blockSignals(False)

    def startTransl(self, query=None, output=0):
        """ 启动翻译并输出翻译结果
        output = 0: 输出到主窗口（默认）
        output = 1: 输出到悬浮窗
        """
        # 主动发起翻译时，关闭自动翻译定时器
        self.timer.stop()
        # 上一次翻译上尚未结束时终止本次翻译
        if self.transl_started:
            return None
        # 翻译引擎为空时弹窗提示，并终止翻译
        if self.transl_engine is None:
            QtWidgets.QMessageBox.information(self, '翻译引擎始化中', '翻译引擎正在初始化中，请稍后重试！')
            return None
        # 获取翻译内容，并去除首尾的空白字符
        query = self.textEdit.toPlainText() if query is None else query
        query = query.strip()
        # 没有输入翻译内容时弹窗提示，并终止翻译
        if not query:
            QtWidgets.QMessageBox.information(self, '翻译内容为空', '请输入翻译内容')
            return None

        def output_to_main_window(result):
            """翻译结束，输出结果到主窗口"""
            # 标记本次翻译结束
            self.transl_started = False
            # 翻译发生异常时弹窗提示，并终止输出
            if result['code'] == 0:
                QtWidgets.QMessageBox.information(self, '翻译失败', result['msg'])
                return None
            # 没有翻译内容时终止输出
            if not self.textEdit.toPlainText().strip():
                return None
            # 更新下拉列表
            self.updateComboBoxItems()
            # 输出翻译结果
            self.output()

        def output_to_float_window(result):
            """翻译结束，输出结果到悬浮窗"""
            # 标记本次翻译结束
            self.transl_started = False
            if hasattr(self, 'float_window'):
                # 将结果输出到悬浮窗口
                self.float_window.output(self.transl_engine)

        # 输出方式
        if output == 0:
            trigger = output_to_main_window
        elif output == 1:
            trigger = output_to_float_window
        else:
            return None
        # 通过线程发起翻译
        kwargs = {'query': query, 'to_lan': self.target_lan, 'from_lan': self.source_lan}
        self.transl_thread = TranslThread(self.transl_engine, **kwargs)
        self.transl_thread.trigger.connect(trigger)
        self.transl_thread.start()
        self.transl_started = True  # 标记本次翻译正在进行

    def output(self, reverse=False):
        """输出翻译结果"""
        translation_contents, explanation_contents = generate_output(self.transl_engine, True, reverse)
        if translation_contents and explanation_contents:
            # 设置输出内容
            self.textBrowser.setText(translation_contents)
            self.textBrowser_2.setText(explanation_contents)
            # 调整UI
            self.updateUI(1)
        else:
            # 设置输出内容
            self.textBrowser_2.setText(translation_contents or explanation_contents)
            # 调整UI
            self.updateUI(2)

    def voiceButtonClicked(self):
        """ 点击语音播报按钮
        下载译文内容的语音并播放
        """
        _, args = self.transl_engine.get_translation()
        # 通过线程下载并播放读音
        self.tts(*args)

    def copyButtonClicked(self):
        """ 点击复制内容按钮
        复制译文内容到剪切板
        """
        text, _ = self.transl_engine.get_translation()
        if text:  # 文本不为空则添加到剪切板
            self.clipboard.setText(text)

    def anchorClicked(self, url):
        """ 点击底部输出框中的链接
        点击输出框中音标发音按钮时，获取单词发音并播放
        点击输出框中文本链接的时候，提取文本并进行翻译
        """
        url = url.url()[1:]
        res = b64decode_json(url)
        if isinstance(res, list):  # 点击发音按钮
            # 通过线程下载并播放发音
            self.tts(*res)
        else:  # 点击文本链接
            self.textEdit.setPlainText(res)
            self.startTransl()

    def initUI(self):
        """初始化UI布局"""
        # 隐藏输入框清空按钮
        self.pushButton_7.hide()
        # 隐藏输出框1和输出框2
        self.textBrowser.hide()
        self.textBrowser_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()

    def updateUI(self, mode=0):
        """更新UI布局"""
        size = None
        if mode == 0:
            # 关闭输出框1和输出框2
            size = QtCore.QSize(QtCore.QSize(self.width(), 0))
        elif mode == 1:
            # 显示输出框1和输出框2
            size = QtCore.QSize(self.width(), MAX_H)
        elif mode == 2:
            # 关闭输出框1，显示输出框2
            h = self.widget_3.height() + self.textBrowser.height()
            size = QtCore.QSize(self.width(), MAX_H - h)

        def hide():
            """隐藏输出控件"""
            self.textBrowser.hide()
            self.textBrowser_2.hide()
            self.widget_3.hide()
            self.widget_4.hide()

        def finished():
            """调整输出控件"""
            self.animation.deleteLater()
            if mode == 1:
                self.widget_3.show()
                self.textBrowser.show()
                self.textBrowser_2.show()
                self.fadeIn(self.widget_2)
            elif mode == 2:
                self.widget_4.show()
                self.textBrowser_2.show()
                self.fadeIn(self.widget_2)

        if size is not None:
            hide()
            # 窗口大小变化动画
            self.animation = QtCore.QPropertyAnimation(self, b"size", self)
            self.animation.setDuration(200)  # 动画持续时间
            self.animation.setEndValue(size)
            self.animation.finished.connect(finished)
            self.animation.start()

    def fadeIn(self, widget):
        """控件淡入"""
        opacity = QtWidgets.QGraphicsOpacityEffect()
        opacity.setOpacity(0)
        widget.setGraphicsEffect(opacity)
        opacity.i = 1
        num = 50

        def timeout():
            """设置控件透明度"""
            opacity.setOpacity(opacity.i / num)
            widget.setGraphicsEffect(opacity)
            opacity.i += 1
            if opacity.i >= num:
                self.temp_timer.stop()
                self.temp_timer.deleteLater()

        self.temp_timer = QtCore.QTimer()
        self.temp_timer.setInterval(1)
        self.temp_timer.timeout.connect(timeout)
        self.temp_timer.start()

    def tts(self, *args):
        """ 文本转语音
        下载 TTS 并播放
        """
        def trigger(data):
            """播放语音"""
            # 将语音写入缓冲区
            buffer = QtCore.QBuffer(self)
            buffer.setData(data)
            buffer.open(QtCore.QIODevice.ReadOnly)
            # 创建播放器
            player = QtMultimedia.QMediaPlayer(self)
            player.setVolume(100)
            player.setMedia(QtMultimedia.QMediaContent(), buffer)
            sleep(0.1)  # 延时等待 setMedia 完成。
            # 播放语音
            player.play()

        self.voice_thread = VoiceThread(self.transl_engine, *args)
        self.voice_thread.trigger.connect(trigger)
        self.voice_thread.start()

    def ocr(self, img_data):
        """ 文字识别
        识别图片中的文本并发起翻译
        """
        # 输出提示信息
        self.textEdit.blockSignals(True)  # 关闭信号连接
        self.textEdit.setText('<i>正在识别翻译，请稍候...</i>')
        self.textEdit.blockSignals(False)  # 恢复信号连接

        def trigger(text):
            """将识别到的文本设置到输入框进行翻译。如果没有识别到文本则弹窗提示"""
            if text:
                self.textEdit.setPlainText(text)
                self.startTransl()
            else:
                self.textEdit.clear()  # 清除提示信息
                QtWidgets.QMessageBox.information(self, '提示', '没有从图片中识别到文字！')

        # 提取图片中的文字
        self.ocr_thread = OCRThread(img_data, self.source_lan)
        self.ocr_thread.trigger.connect(trigger)
        self.ocr_thread.start()

    def registerHotKey(self):
        """注册全局热键"""
        # 检查“F1”是否已被注册
        if user32.RegisterHotKey(None, 0, 0, VK_F1) and user32.RegisterHotKey(None, 0, 1, VK_F1):
            # 注册“F1”为全局截屏翻译快捷键
            screen_trans_hot_key = SystemHotkey()
            screen_trans_hot_key.register(['f1'], callback=lambda x: self.pushButton_4.click())

    def center(self):
        """窗口剧中显示"""
        screen_geometry = QtGui.QGuiApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        x = int((screen_geometry.width() - window_geometry.width()) / 2)
        y = int((screen_geometry.height() - window_geometry.height()) / 4)
        self.move(x, y)


if __name__ == '__main__':
    # 高分辨率屏幕自适应
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # 创建QApplication类的实例
    app = QtWidgets.QApplication(sys.argv)
    # 设置窗口风格为Fusion
    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    # 汉化右键菜单
    translator = QtCore.QTranslator()
    translator.load(widgets_zh_CN_qm)
    app.installTranslator(translator)
    # 创建主窗口
    window = MainWindow()
    window.show()
    # 进入程序的主循环，并通过exit函数确保主循环安全结束
    sys.exit(app.exec_())
