# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, Qt, QRectF, QBuffer, qAbs, QRect, QIODevice, QPoint, QPropertyAnimation
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QKeySequence, QGuiApplication, QCursor
from PyQt5.QtWidgets import QWidget, QTextEdit, QGraphicsDropShadowEffect, QApplication, QLabel, QDesktopWidget, QShortcut


class FramelessWidget(QWidget):
    """ 自定义Widget(主窗口)
    1. 无边框、置顶
    2. 添加阴影
    3. 鼠标拖动
    """
    sizeChanged = pyqtSignal(tuple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 无边框置顶
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowMinMaxButtonsHint)
        # 初始化变量
        self.currentWidth = 0
        self.currentHeight = 0
        self.mFlag = False
        self.mPos = None

    def paintEvent(self, event):
        # 检测窗口变化
        if self.currentWidth != self.size().width() and self.currentWidth != 0:
            self.sizeChanged.emit((self.currentWidth, self.currentHeight))  # 发送窗口的宽和高
        else:
            self.currentWidth = self.size().width()
            self.currentHeight = self.size().height()
        # 窗口阴影
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        color = QColor(Qt.gray)
        num = 11  # 阴影宽度 = 内边距 + 2
        for i in range(num):
            painterPath = QPainterPath()
            painterPath.setFillRule(Qt.WindingFill)
            ref = QRectF(num - i, num - i, self.width() - (num - i) * 2, self.height() - (num - i) * 2)
            painterPath.addRoundedRect(ref, 0, 0)
            color.setAlpha(int(150 - i ** 0.5 * 50))
            painter.setPen(color)
            painter.drawPath(painterPath)
        # 窗口背景
        painter_2 = QPainter(self)
        painter_2.setRenderHint(painter_2.Antialiasing)
        painter_2.setBrush(QColor(240, 240, 240, 255))
        painter_2.setPen(Qt.transparent)
        rect = self.rect()
        rect.setLeft(num)
        rect.setTop(num)
        rect.setWidth(rect.width() - num)
        rect.setHeight(rect.height() - num)
        painter_2.drawRoundedRect(rect, 0, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mPos = event.globalPos() - self.pos()  # 鼠标相对窗口的位置
            self.mFlag = True
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.mFlag:
            self.move(event.globalPos() - self.mPos)  # 窗口跟随鼠标移动
            event.accept()

    def mouseReleaseEvent(self, event):
        self.mFlag = False


class MyTextEdit(QTextEdit):
    """ 自定义TextEdit
    1. 自定义右键菜单
    2. 插入文件时清空文本框
    3. 设置、取消阴影
    """
    def __init__(self, *args):
        super().__init__(*args)
        # 阴影设置
        self.effect = QGraphicsDropShadowEffect(self)
        self.effect.setOffset(0, 0)
        self.effect.setBlurRadius(10)
        # 变量初始化
        self.clipboard = QApplication.clipboard()
        self.currentHeight = 0

    # def contextMenuEvent(self, event):
    #     """自定义右键菜单"""
    #     menu = QMenu()
    #     undo = menu.addAction("撤销")
    #     undo.setShortcut(QKeySequence.Undo)
    #     redo = menu.addAction("恢复")
    #     redo.setShortcut(QKeySequence.Redo)
    #     menu.addSeparator()
    #     cut = menu.addAction("剪切")
    #     cut.setShortcut(QKeySequence.Cut)
    #     copy = menu.addAction("复制")
    #     copy.setShortcut(QKeySequence.Copy)
    #     paste = menu.addAction("粘贴")
    #     paste.setShortcut(QKeySequence.Paste)
    #     delete = menu.addAction("删除")
    #     menu.addSeparator()
    #     select_all = menu.addAction("选择全部")
    #     select_all.setShortcut(QKeySequence.SelectAll)
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
        super().insertFromMimeData(mime_data)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.height() == self.maximumHeight() and self.currentHeight != self.maximumHeight():
            # 添加阴影
            self.effect.setColor(QColor(220, 220, 220))
            self.setGraphicsEffect(self.effect)
            self.currentHeight = self.height()
        elif self.height() == self.minimumHeight() and self.currentHeight != self.minimumHeight():
            # 去除阴影
            self.effect.setColor(Qt.transparent)
            self.setGraphicsEffect(self.effect)
            self.currentHeight = self.height()
        else:
            self.currentHeight = self.height()


class MyLabel(QLabel):
    """ 自定义Label
    鼠标移入隐藏，移出显示
    """
    def __init__(self, *args):
        super().__init__(*args)

    def enterEvent(self, event):
        """鼠标移入隐藏"""
        self.hide()

    def leaveEvent(self, event):
        """鼠标移出显示"""
        self.show()


class Screenshot(QWidget):
    """ 自定义Widget(屏幕截图)
    1. 启动截图时获取整个屏幕
    2. 按住鼠标左键移动选择截取区域
    3. 松开鼠标左键获取截图，并通过信号发送
    4. 按下鼠标右键或Esc键取消截图
    """
    completed = pyqtSignal(QBuffer)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化窗口
        self.setMouseTracking(True)  # 鼠标追踪
        self.setCursor(Qt.CrossCursor)  # 十字光标
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 无边框置顶
        # 屏幕分宽高
        self._screenGeometry = QDesktopWidget().screenGeometry()
        # 初始化变量
        self._pressLeftButton = False
        self._beginPos = None
        self._endPos = None
        self._captureImage = None
        self._fullScreenImage = None
        self._painter = QPainter()
        self._pen = QPen(QColor(30, 144, 245), 1, Qt.SolidLine, Qt.RoundCap)
        # 创建提示框
        self._createTipBox()
        # Esc 键取消截屏
        QShortcut(QKeySequence(self.tr("Esc")), self, self.cancel)

    def _createTipBox(self):
        """创建提示框"""
        self._label = MyLabel(self)
        self._label.setText("按住鼠标左键选择翻译区域<br>按下鼠标右键或Esc键取消截屏")
        self._label.setStyleSheet("QLabel {background-color: rgba(0, 0, 0, 100); border: 1px solid transparent; font: 14px \"微软雅黑\"; color: rgb(255, 255, 255)}")
        self._label.setObjectName("label")

    def mousePressEvent(self, event):
        """ 鼠标按键按下
        左键按下记录鼠标按下位置
        右键按下退出截图，并发送结束信号
        """
        if event.button() == Qt.LeftButton:
            # 关闭提示框
            self._label.close()
            # 点击鼠标左键开始截图
            self._beginPos = event.pos()
            self._pressLeftButton = True
        elif event.button() == Qt.RightButton:
            # 点击鼠标右键取消截图
            self.cancel()

    def mouseReleaseEvent(self, event):
        """ 鼠标按键抬起
        记录鼠标抬起位置
        退出截图，并发送结束信号和截图
        """
        self._endPos = event.pos()
        self.complete()  # 截屏完成

    def mouseMoveEvent(self, event):
        """ 鼠标移动
        更新鼠标移动位置
        提示框跟随鼠标移动
        """
        if self._pressLeftButton:
            self._endPos = event.pos()
            self.update()
        else:
            move_widget(self._label, self._screenGeometry, event.pos())  # 提示框跟随鼠标移动

    def paintEvent(self, event):
        """绘制屏幕选区"""
        self._painter.begin(self)  # 开始重绘
        self._painter.drawPixmap(0, 0, self._fullScreenImage)
        self._painter.fillRect(self._fullScreenImage.rect(), QColor(0, 0, 0, 60))  # 黑色半透明遮罩
        self._painter.setPen(self._pen)  # 蓝色画笔
        if self._pressLeftButton and self._beginPos is not None and self._endPos is not None:
            pickRect = self._getRectangle(self._beginPos, self._endPos)  # 获得要截图的矩形框
            self._captureImage = self._fullScreenImage.copy(pickRect)  # 获取矩形框内的图片
            self._painter.drawPixmap(pickRect.topLeft(), self._captureImage)  # 填充截取的图片
            self._painter.drawRect(pickRect)  # 画矩形边框
        self._painter.end()  # 结束重绘

    def _getRectangle(self, beginPoint, endPoint):
        """获取屏幕选区"""
        pickRectWidth = int(qAbs(beginPoint.x() - endPoint.x()))
        pickRectHeight = int(qAbs(beginPoint.y() - endPoint.y()))
        pickRectTop = beginPoint.x() if beginPoint.x() < endPoint.x() else endPoint.x()
        pickRectLeft = beginPoint.y() if beginPoint.y() < endPoint.y() else endPoint.y()
        pickRect = QRect(pickRectTop, pickRectLeft, pickRectWidth if pickRectWidth > 0 else 1, pickRectHeight if pickRectHeight > 0 else 1)
        return pickRect

    def show(self):
        self.showFullScreen()

    def showFullScreen(self):
        """ 启动截屏
        获取屏幕，显示截屏窗口
        """
        if not self.isVisible():
            self._fullScreenImage = QGuiApplication.primaryScreen().grabWindow(QApplication.desktop().winId())  # 获取整个屏幕
            self._label.show()  # 显示提示框
            move_widget(self._label, self._screenGeometry, QCursor.pos())  # 刷新提示框位置
            super().showFullScreen()  # 全屏显示截图窗口

    def complete(self):
        """ 截屏完成
        通过信号发送截取的图片，并重置变量
        """
        # 截图转 QBuffer，并通过信号发送截图数据
        buffer = QBuffer(self)
        buffer.open(QIODevice.WriteOnly)
        if self._captureImage:
            self._captureImage.save(buffer, 'JPG')
        self.completed.emit(buffer)  # 发送信号
        # 重置变量
        self.reset()

    def cancel(self):
        """ 取消截屏
        丢弃截图并退出截屏
        """
        self._captureImage = None  # 清除截图

    def reset(self):
        """重置变量"""
        self._pressLeftButton = False
        self._beginPos = None
        self._endPos = None
        self._captureImage = None
        self._fullScreenImage = None


class FloatWidget(QWidget):
    """ 自定义Widget(悬浮窗口)
    1. 无边框、圆角、置顶
    2. 添加阴影
    3. 淡入/淡出
    """
    radioButtonClicked = pyqtSignal(bool)
    pushButtonClicked = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 无边框置顶
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 阴影效果
        self.effect = QGraphicsDropShadowEffect(self)
        self.effect.setOffset(0, 0)
        self.effect.setBlurRadius(10)
        self.effect.setColor(QColor(200, 200, 200))
        self.setGraphicsEffect(self.effect)
        # 淡入/淡出动画
        self.animation = QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.setDuration(300)  # 动画持续时间

    def paintEvent(self, event):
        # 窗口背景
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.setBrush(Qt.white)
        painter.setPen(Qt.transparent)
        rect = self.rect()
        rect.setLeft(10)
        rect.setTop(10)
        rect.setWidth(rect.width() - 10)
        rect.setHeight(rect.height() - 10)
        painter.drawRoundedRect(rect, 10, 10)

    def showFullScreen(self):
        self.show()

    def show(self):
        """窗口淡入"""
        if not self.isVisible():
            # 先显示窗口再执行动画
            super().show()
            self.animation.setStartValue(0)
            self.animation.setEndValue(1)
            self.animation.start()

    def close(self):
        """窗口淡出"""
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()
        self.animation.finished.connect(self.deleteLater)  # 动画执行完毕再销毁窗口


def move_widget(widget: QWidget, geometry: QRect, pos: QPoint = None, offset: int = 20):
    """ 移动部件
    保持部件始终显示在屏幕内
    :param widget: 移动部件
    :param geometry: 屏幕宽高
    :param pos: 鼠标坐标。窗口跟随鼠标移动
    :param offset: 窗口跟随鼠标移动时窗口与鼠标的间距
    """
    screen_w = geometry.width()  # 屏幕宽
    screen_h = geometry.height()  # 屏幕高
    if pos is None:  # 窗口不跟随鼠标
        x = widget.geometry().x()  # 部件X坐标
        y = widget.geometry().y()  # 部件Y坐标
        # 保持部件始终显示在屏幕内
        if x < 0 or x + widget.width() > screen_w:
            x = 0 if x < 0 else screen_w - widget.width()
        if y < 0 or y + widget.height() > screen_h:
            y = 0 if y < 0 else screen_h - widget.height()
    else:  # 窗口跟随鼠标
        x = pos.x() + offset  # 鼠标X坐标
        y = pos.y() + offset  # 鼠标Y坐标
        # 保持部件始终显示在屏幕内
        if x + widget.width() > screen_w:  # 部件右侧超出边界
            x = screen_w - widget.width() if x - widget.width() < offset * 2 else x - widget.width() - offset * 2
        if y + widget.height() > screen_h:  # 部件底部超出边界
            y = screen_h - widget.height() if y - widget.height() < offset * 2 else y - widget.height() - offset * 2
    widget.move(x, y)  # 移动部件
