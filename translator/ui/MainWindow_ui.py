# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

from widgets import MyTextEdit


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.verticalLayout = QtWidgets.QVBoxLayout(MainWindow)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(MainWindow)
        self.pushButton.setMinimumSize(QtCore.QSize(45, 30))
        self.pushButton.setStyleSheet("QPushButton {background-color: transparent; border: 0;} QPushButton:hover {background-color: rgb(220, 220, 220);} QPushButton:pressed, QPushButton:checked {background-color: rgb(200, 200, 200);}")
        self.pushButton.setCheckable(True)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(MainWindow)
        self.pushButton_2.setMinimumSize(QtCore.QSize(45, 30))
        self.pushButton_2.setStyleSheet("QPushButton {background-color: transparent; border: 0;} QPushButton:hover {background-color: rgb(220, 220, 220);} QPushButton:pressed {background-color: rgb(200, 200, 200);}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(MainWindow)
        self.pushButton_3.setMinimumSize(QtCore.QSize(45, 30))
        self.pushButton_3.setStyleSheet("QPushButton {background-color: transparent; border: 0;} QPushButton:hover {background-color: rgb(228, 104, 85);} QPushButton:pressed {background-color: rgb(196, 94, 74);}")
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(MainWindow)
        self.line.setMinimumSize(QtCore.QSize(400, 3))
        self.line.setStyleSheet("border: 1px solid rgb(220, 220, 220); border-left-color: transparent; border-right-color: transparent; border-bottom-color: transparent;")
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(10, 8, 10, 10)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBox = QtWidgets.QComboBox(MainWindow)
        self.comboBox.setMinimumSize(QtCore.QSize(90, 28))
        self.comboBox.setMaximumSize(QtCore.QSize(90, 28))
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.checkBox = QtWidgets.QCheckBox(MainWindow)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.pushButton_4 = QtWidgets.QPushButton(MainWindow)
        self.pushButton_4.setMinimumSize(QtCore.QSize(30, 28))
        self.pushButton_4.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_4.setStyleSheet("QPushButton {background-color: transparent; border: 0; font-size: 20px;}")
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.pushButton_5 = QtWidgets.QPushButton(MainWindow)
        self.pushButton_5.setMinimumSize(QtCore.QSize(80, 28))
        self.pushButton_5.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_5.setStyleSheet("QPushButton {background-color: rgb(67, 149, 255); color: rgb(255, 255, 255); border-radius: 5px;} QPushButton:pressed {background-color: rgb(52, 133, 251);}")
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_2.addWidget(self.pushButton_5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.comboBox_2 = QtWidgets.QComboBox(MainWindow)
        self.comboBox_2.setMinimumSize(QtCore.QSize(140, 28))
        self.comboBox_2.setEditable(True)
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout_3.addWidget(self.comboBox_2)
        self.pushButton_6 = QtWidgets.QPushButton(MainWindow)
        self.pushButton_6.setMaximumSize(QtCore.QSize(30, 28))
        self.pushButton_6.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_6.setStyleSheet("QPushButton {background-color: transparent; border: 0; font-size: 25px;}")
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_3.addWidget(self.pushButton_6)
        self.comboBox_3 = QtWidgets.QComboBox(MainWindow)
        self.comboBox_3.setMinimumSize(QtCore.QSize(140, 28))
        self.comboBox_3.setEditable(True)
        self.comboBox_3.setObjectName("comboBox_3")
        self.horizontalLayout_3.addWidget(self.comboBox_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        spacerItem3 = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem3)
        self.widget = QtWidgets.QWidget(MainWindow)
        self.widget.setStyleSheet("QWidget#widget {background-color: rgb(250, 250, 250); border-radius: 10px;} QScrollBar:vertical {background: transparent; width: 6px; margin: 0;} QScrollBar::handle:vertical {background: rgb(224, 224, 224); min-height: 30px; border-radius: 3px;} QScrollBar::sub-line:vertical {height: 0; subcontrol-position: top;} QScrollBar::add-line:vertical {height: 0; subcontrol-position: bottom;} QScrollBar:horizontal {background: transparent; height: 6px; margin: 0;} QScrollBar::handle:horizontal {background: rgb(224, 224, 224); min-width: 30px; border-radius: 3px;} QScrollBar::sub-line:horizontal {width: 0; subcontrol-position: left;} QScrollBar::add-line:horizontal {width: 0; subcontrol-position: right;}")
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.textEdit = MyTextEdit(self.widget)
        self.textEdit.setMinimumSize(QtCore.QSize(380, 110))
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 150))
        self.textEdit.setStyleSheet("QTextEdit {background-color: rgb(255, 255, 255); border-radius: 10px; font: 16px \"微软雅黑\"; color: rgb(60, 60, 60); padding: 6px;} QTextEdit:hover {border: 2px solid rgb(82, 186, 255);} QTextEdit:focus {border: 2px solid rgb(82, 186, 255);}")
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.textEdit)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, -1, 6, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem4 = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
        self.pushButton_7 = QtWidgets.QPushButton(self.textEdit)
        self.pushButton_7.setMinimumSize(QtCore.QSize(18, 18))
        self.pushButton_7.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_7.setStyleSheet("QPushButton {background-color: rgba(0, 0, 0, 80); border-radius: 9px; font-size: 8px; color: rgb(255, 255, 255);}")
        self.pushButton_7.setObjectName("pushButton_7")
        self.horizontalLayout_4.addWidget(self.pushButton_7)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        spacerItem5 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem5)
        self.verticalLayout_3.addWidget(self.textEdit)
        self.widget_2 = QtWidgets.QWidget(self.widget)
        self.widget_2.setStyleSheet("QPushButton {background-color: transparent; border: 0; font-size: 16px;}")
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.textBrowser = QtWidgets.QTextBrowser(self.widget_2)
        self.textBrowser.setMinimumSize(QtCore.QSize(380, 55))
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 55))
        self.textBrowser.setStyleSheet("QTextBrowser {background-color: transparent; border: 2px solid transparent; border-radius: 10px; font: 18px \"微软雅黑\"; color: rgb(60, 60, 60); padding: 6px;}")
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_5.addWidget(self.textBrowser)
        self.widget_3 = QtWidgets.QWidget(self.widget_2)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setProperty("toptMargin", 0)
        self.horizontalLayout_5.setContentsMargins(11, -1, -1, 8)
        self.horizontalLayout_5.setSpacing(14)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton_8 = QtWidgets.QPushButton(self.widget_3)
        self.pushButton_8.setMinimumSize(QtCore.QSize(22, 22))
        self.pushButton_8.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_8.setObjectName("pushButton_8")
        self.horizontalLayout_5.addWidget(self.pushButton_8)
        self.pushButton_9 = QtWidgets.QPushButton(self.widget_3)
        self.pushButton_9.setMinimumSize(QtCore.QSize(22, 22))
        self.pushButton_9.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_9.setObjectName("pushButton_9")
        self.horizontalLayout_5.addWidget(self.pushButton_9)
        spacerItem6 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem6)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.line_2 = QtWidgets.QFrame(self.widget_3)
        self.line_2.setStyleSheet("background-color: rgb(255, 170, 127); border: 1px solid transparent;")
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_6.addWidget(self.line_2)
        self.verticalLayout_5.addWidget(self.widget_3)
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.widget_2)
        self.textBrowser_2.setMinimumSize(QtCore.QSize(380, 260))
        self.textBrowser_2.setStyleSheet("QTextBrowser {background-color: rgb(250, 250, 250); border: 2px solid rgb(250, 250, 250); border-radius: 10px; font: 16px \"微软雅黑\"; color: rgb(60, 60, 60); padding: 6px;}")
        self.textBrowser_2.setOpenLinks(False)
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.verticalLayout_5.addWidget(self.textBrowser_2)
        self.widget_4 = QtWidgets.QWidget(self.widget_2)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_6.setContentsMargins(11, 0, 0, 8)
        self.horizontalLayout_6.setSpacing(14)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.pushButton_10 = QtWidgets.QPushButton(self.widget_4)
        self.pushButton_10.setMinimumSize(QtCore.QSize(22, 22))
        self.pushButton_10.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_10.setObjectName("pushButton_10")
        self.horizontalLayout_6.addWidget(self.pushButton_10)
        self.pushButton_11 = QtWidgets.QPushButton(self.widget_4)
        self.pushButton_11.setMinimumSize(QtCore.QSize(22, 22))
        self.pushButton_11.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_11.setObjectName("pushButton_11")
        self.horizontalLayout_6.addWidget(self.pushButton_11)
        spacerItem7 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem7)
        self.verticalLayout_5.addWidget(self.widget_4)
        self.verticalLayout_3.addWidget(self.widget_2)
        self.widget_2.raise_()
        self.textEdit.raise_()
        self.verticalLayout_2.addWidget(self.widget)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(MainWindow)
        self.pushButton_2.clicked.connect(MainWindow.showMinimized)
        self.pushButton_3.clicked.connect(MainWindow.close)
        self.pushButton_7.clicked.connect(self.textEdit.clear)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "翻译"))
        self.pushButton.setToolTip(_translate("MainWindow", "置顶/取消置顶"))
        self.pushButton.setText(_translate("MainWindow", "📌"))
        self.pushButton_2.setToolTip(_translate("MainWindow", "最小化"))
        self.pushButton_2.setText(_translate("MainWindow", "─"))
        self.pushButton_3.setToolTip(_translate("MainWindow", "关闭"))
        self.pushButton_3.setText(_translate("MainWindow", "╳"))
        self.comboBox.setToolTip(_translate("MainWindow", "翻译引擎"))
        self.checkBox.setToolTip(_translate("MainWindow", "Ctrl+C 快速发起翻译"))
        self.checkBox.setText(_translate("MainWindow", "划词翻译"))
        self.pushButton_4.setToolTip(_translate("MainWindow", "截屏翻译（F1）"))
        self.pushButton_4.setText(_translate("MainWindow", "📸"))
        self.pushButton_5.setToolTip(_translate("MainWindow", "开始翻译"))
        self.pushButton_5.setText(_translate("MainWindow", "翻译"))
        self.comboBox_2.setToolTip(_translate("MainWindow", "源语言"))
        self.pushButton_6.setToolTip(_translate("MainWindow", "交换源语言和目标语言"))
        self.pushButton_6.setText(_translate("MainWindow", "⇌"))
        self.comboBox_3.setToolTip(_translate("MainWindow", "目标语言"))
        self.textEdit.setPlaceholderText(_translate("MainWindow", "输入文字/拖入图片"))
        self.pushButton_7.setToolTip(_translate("MainWindow", "清空"))
        self.pushButton_7.setText(_translate("MainWindow", "╳"))
        self.pushButton_8.setToolTip(_translate("MainWindow", "发音"))
        self.pushButton_8.setText(_translate("MainWindow", "🔊"))
        self.pushButton_9.setToolTip(_translate("MainWindow", "复制"))
        self.pushButton_9.setText(_translate("MainWindow", "📑"))
        self.pushButton_10.setToolTip(_translate("MainWindow", "发音"))
        self.pushButton_10.setText(_translate("MainWindow", "🔊"))
        self.pushButton_11.setToolTip(_translate("MainWindow", "复制"))
        self.pushButton_11.setText(_translate("MainWindow", "📑"))
