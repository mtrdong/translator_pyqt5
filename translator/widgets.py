# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtCore, QtWidgets, QtGui

from threads import MouseCheckThread
from utils import move_widget


class FramelessWidget(QtWidgets.QWidget):
    """ 自定义Widget(主窗口)
    1. 无边框、置顶/取消置顶
    2. 添加阴影
    3. 鼠标拖动
    """
    sizeChanged = QtCore.pyqtSignal(tuple)

    def __init__(self, *args, **kwargs):
        super(FramelessWidget, self).__init__(*args, **kwargs)
        # 背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 无边框
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowMinMaxButtonsHint)
        # 初始化变量
        self.topHintFlag = False
        self.currentWidth = 0
        self.currentHeight = 0
        self.mFlag = False
        self.mPos = None

    def staysOnTopHint(self):
        """置顶/取消置顶"""
        default = QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowMinMaxButtonsHint
        windowHandle = self.windowHandle()
        if self.topHintFlag:
            windowHandle.setFlags(default)
            self.topHintFlag = False
        else:
            windowHandle.setFlags(default | QtCore.Qt.WindowStaysOnTopHint)
            self.topHintFlag = True
        windowHandle.show()

    def paintEvent(self, event):
        # 检测窗口变化
        if self.currentWidth != self.size().width() and self.currentWidth != 0:
            self.sizeChanged.emit((self.currentWidth, self.currentHeight))  # 发送窗口的宽和高
        else:
            self.currentWidth = self.size().width()
            self.currentHeight = self.size().height()
        # 窗口阴影
        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        color = QtGui.QColor(QtCore.Qt.gray)
        num = 11  # 阴影宽度 = 内边距 + 2
        for i in range(num):
            painterPath = QtGui.QPainterPath()
            painterPath.setFillRule(QtCore.Qt.WindingFill)
            ref = QtCore.QRectF(num - i, num - i, self.width() - (num - i) * 2, self.height() - (num - i) * 2)
            painterPath.addRoundedRect(ref, 0, 0)
            color.setAlpha(int(150 - i ** 0.5 * 50))
            painter.setPen(color)
            painter.drawPath(painterPath)
        # 窗口背景
        painter_2 = QtGui.QPainter(self)
        painter_2.setRenderHint(painter_2.Antialiasing)
        painter_2.setBrush(QtGui.QColor(240, 240, 240, 255))
        painter_2.setPen(QtCore.Qt.transparent)
        rect = self.rect()
        rect.setLeft(num)
        rect.setTop(num)
        rect.setWidth(rect.width() - num)
        rect.setHeight(rect.height() - num)
        painter_2.drawRoundedRect(rect, 0, 0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mPos = event.globalPos() - self.pos()  # 鼠标相对窗口的位置
            self.mFlag = True
            event.accept()

    def mouseMoveEvent(self, event):
        if QtCore.Qt.LeftButton and self.mFlag:
            self.move(event.globalPos() - self.mPos)  # 窗口跟随鼠标移动
            event.accept()

    def mouseReleaseEvent(self, event):
        self.mFlag = False

    def closeEvent(self, event):
        """关闭主窗口同时关闭所有子窗口"""
        event.accept()
        sys.exit(0)


class FloatWidget(QtWidgets.QWidget):
    """ 自定义Widget(悬浮窗)
    1. 无边框、圆角、置顶
    2. 添加阴影
    3. 淡入/淡出
    4. 自动关闭
    """
    radioButtonClicked = QtCore.pyqtSignal(bool)
    pushButtonClicked = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(FloatWidget, self).__init__(*args, **kwargs)
        # 无边框置顶
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        # 背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 阴影效果
        self.effect = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect.setOffset(0, 0)
        self.effect.setBlurRadius(10)
        self.effect.setColor(QtGui.QColor(200, 200, 200))
        self.setGraphicsEffect(self.effect)
        # 淡入/淡出动画
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.setDuration(200)  # 动画持续时间

    def paintEvent(self, event):
        # 窗口背景
        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtCore.Qt.transparent)
        rect = self.rect()
        rect.setLeft(10)
        rect.setTop(10)
        rect.setWidth(rect.width() - 10)
        rect.setHeight(rect.height() - 10)
        painter.drawRoundedRect(rect, 10, 10)

    def showFullScreen(self):
        self.show()

    def show(self):
        """ 显示窗口
        移动窗口到鼠标的位置
        先显示窗口，再执行淡入动画
        扫描鼠标位置
        """
        # 先显示窗口再执行动画
        move_widget(self, QtWidgets.QDesktopWidget().screenGeometry(), QtGui.QCursor.pos(), 10)  # 移动窗口到鼠标的位置
        super(FloatWidget, self).show()
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        # 自动关闭窗口
        self.check()

    def deleteLater(self):
        """ 回收窗口
        先执行淡出动画，再回收窗口
        """
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()
        self.animation.finished.connect(super(FloatWidget, self).deleteLater)

    def check(self):
        """ 检测鼠标位置
        通过线程扫描鼠标位置，当鼠标超出一定范围后自动关闭悬浮窗
        """
        self.mouse_check_thread = MouseCheckThread(self)
        self.mouse_check_thread.trigger.connect(self.deleteLater)
        self.mouse_check_thread.start()


class MyTextEdit(QtWidgets.QTextEdit):
    """ 自定义TextEdit
    1. 自定义右键菜单
    2. 插入文件时清空文本框
    3. 设置、取消阴影
    """
    def __init__(self, *args):
        super(MyTextEdit, self).__init__(*args)
        # 阴影设置
        self.effect = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect.setOffset(0, 2)
        self.effect.setBlurRadius(10)
        # 变量初始化
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.currentHeight = 0

    # def contextMenuEvent(self, event):
    #     """自定义右键菜单"""
    #     menu = QtWidgets.QMenu()
    #     undo = menu.addAction("撤销")
    #     undo.setShortcut(QtGui.QKeySequence.Undo)
    #     redo = menu.addAction("恢复")
    #     redo.setShortcut(QtGui.QKeySequence.Redo)
    #     menu.addSeparator()
    #     cut = menu.addAction("剪切")
    #     cut.setShortcut(QtGui.QKeySequence.Cut)
    #     copy = menu.addAction("复制")
    #     copy.setShortcut(QtGui.QKeySequence.Copy)
    #     paste = menu.addAction("粘贴")
    #     paste.setShortcut(QtGui.QKeySequence.Paste)
    #     delete = menu.addAction("删除")
    #     menu.addSeparator()
    #     select_all = menu.addAction("选择全部")
    #     select_all.setShortcut(QtGui.QKeySequence.SelectAll)
    #
    #     if self.textCursor().selectedText():
    #         cut.setEnabled(True)
    #         copy.setEnabled(True)
    #         delete.setEnabled(True)
    #     else:
    #         cut.setDisabled(True)
    #         copy.setDisabled(True)
    #         delete.setDisabled(True)
    #     if self.clipboard.mimeData().formats():
    #         paste.setEnabled(True)
    #     else:
    #         paste.setDisabled(True)
    #     if self.toPlainText():
    #         select_all.setEnabled(True)
    #     else:
    #         select_all.setDisabled(True)
    #
    #     if self.isReadOnly():
    #         menu.removeAction(undo)
    #         menu.removeAction(redo)
    #         menu.removeAction(cut)
    #         menu.removeAction(paste)
    #         menu.removeAction(delete)
    #
    #     menu.move(event.pos())
    #     menu.show()
    #
    #     action = menu.exec_(self.mapToGlobal(event.pos()))
    #     if action == undo:
    #         self.undo()
    #     elif action == redo:
    #         self.redo()
    #     elif action == cut:
    #         self.cut()
    #     elif action == copy:
    #         self.copy()
    #     elif action == paste:
    #         self.paste()
    #     elif action == delete:
    #         self.textCursor().deleteChar()
    #     elif action == select_all:
    #         self.selectAll()

    def insertFromMimeData(self, mime_data):
        """插入文件时清空文本框内容"""
        if mime_data.urls():
            if mime_data.urls()[0].url().find('file:///') == 0:
                self.clear()
        super(MyTextEdit, self).insertFromMimeData(mime_data)

    def paintEvent(self, event):
        super(MyTextEdit, self).paintEvent(event)
        if self.height() == self.maximumHeight() and self.currentHeight != self.maximumHeight():
            # 添加阴影
            self.effect.setColor(QtGui.QColor(240, 240, 240))
            self.setGraphicsEffect(self.effect)
            self.currentHeight = self.height()
        elif self.height() == self.minimumHeight() and self.currentHeight != self.minimumHeight():
            # 去除阴影
            self.effect.setColor(QtCore.Qt.transparent)
            self.setGraphicsEffect(self.effect)
            self.currentHeight = self.height()
        else:
            self.currentHeight = self.height()


class MyLabel(QtWidgets.QLabel):
    """ 自定义Label
    鼠标移入隐藏，移出显示
    """
    def __init__(self, *args):
        super(MyLabel, self).__init__(*args)

    def enterEvent(self, event):
        """鼠标移入隐藏"""
        self.hide()

    def leaveEvent(self, event):
        """鼠标移出显示"""
        self.show()
