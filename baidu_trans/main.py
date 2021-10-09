# -*- coding: utf-8 -*-
import contextlib
import sys
from time import sleep

from PyQt5.QtCore import pyqtSlot, QTranslator, QTimer, QBuffer, QIODevice, QPropertyAnimation, QSize, QRect
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMessageBox, QDesktopWidget
from system_hotkey import SystemHotkey

from FloatWindow import Ui_FloatWindow
from MainWindow import Ui_MainWindow
from resource import favicon_ico, widgets_zh_CN_qm
from utils import *
from widgets import FramelessWidget, Screenshot, FloatWidget, move_widget

# 窗口最大宽高
MAX_W, MAX_H = 440, 660
# 窗口最小宽高
MIN_W, MIN_H = 440, 209

# 语言种类
exports = {'中文(简体)': 'zh', '英语': 'en', '日语': 'jp', '泰语': 'th', '西班牙语': 'spa', '阿拉伯语': 'ara', '法语': 'fra', '韩语': 'kor', '俄语': 'ru', '德语': 'de', '葡萄牙语': 'pt', '意大利语': 'it', '希腊语': 'el', '荷兰语': 'nl', '波兰语': 'pl', '芬兰语': 'fin', '捷克语': 'cs', '保加利亚语': 'bul', '丹麦语': 'dan', '爱沙尼亚语': 'est', '匈牙利语': 'hu', '罗马尼亚语': 'rom', '斯洛文尼亚语': 'slo', '瑞典语': 'swe', '越南语': 'vie', '中文(粤语)': 'yue', '中文(繁体)': 'cht', '中文(文言文)': 'wyw', '南非荷兰语': 'afr', '阿尔巴尼亚语': 'alb', '阿姆哈拉语': 'amh', '亚美尼亚语': 'arm', '阿萨姆语': 'asm', '阿斯图里亚斯语': 'ast', '阿塞拜疆语': 'aze', '巴斯克语': 'baq', '白俄罗斯语': 'bel', '孟加拉语': 'ben', '波斯尼亚语': 'bos', '缅甸语': 'bur', '加泰罗尼亚语': 'cat', '宿务语': 'ceb', '克罗地亚语': 'hrv', '世界语': 'epo', '法罗语': 'fao', '菲律宾语': 'fil', '加利西亚语': 'glg', '格鲁吉亚语': 'geo', '古吉拉特语': 'guj', '豪萨语': 'hau', '希伯来语': 'heb', '印地语': 'hi', '冰岛语': 'ice', '伊博语': 'ibo', '印尼语': 'id', '爱尔兰语': 'gle', '卡纳达语': 'kan', '克林贡语': 'kli', '库尔德语': 'kur', '老挝语': 'lao', '拉丁语': 'lat', '拉脱维亚语': 'lav', '立陶宛语': 'lit', '卢森堡语': 'ltz', '马其顿语': 'mac', '马拉加斯语': 'mg', '马来语': 'may', '马拉雅拉姆语': 'mal', '马耳他语': 'mlt', '马拉地语': 'mar', '尼泊尔语': 'nep', '新挪威语': 'nno', '波斯语': 'per', '萨丁尼亚语': 'srd', '塞尔维亚语(拉丁文)': 'srp', '僧伽罗语 ': 'sin', '斯洛伐克语': 'sk', '索马里语': 'som', '斯瓦希里语': 'swa', '他加禄语': 'tgl', '塔吉克语': 'tgk', '泰米尔语': 'tam', '鞑靼语': 'tat', '泰卢固语': 'tel', '土耳其语': 'tr', '土库曼语': 'tuk', '乌克兰语': 'ukr', '乌尔都语': 'urd', '奥克语': 'oci', '吉尔吉斯语': 'kir', '普什图语': 'pus', '高棉语': 'hkm', '海地语': 'ht', '书面挪威语': 'nob', '旁遮普语': 'pan', '阿尔及利亚阿拉伯语': 'arq', '比斯拉马语': 'bis', '加拿大法语': 'frn', '哈卡钦语': 'hak', '胡帕语': 'hup', '印古什语': 'ing', '拉特加莱语': 'lag', '毛里求斯克里奥尔语': 'mau', '黑山语': 'mot', '巴西葡萄牙语': 'pot', '卢森尼亚语': 'ruy', '塞尔维亚-克罗地亚语': 'sec', '西里西亚语': 'sil', '突尼斯阿拉伯语': 'tua', '亚齐语': 'ach', '阿肯语': 'aka', '阿拉贡语': 'arg', '艾马拉语': 'aym', '俾路支语': 'bal', '巴什基尔语': 'bak', '本巴语': 'bem', '柏柏尔语': 'ber', '博杰普尔语': 'bho', '比林语': 'bli', '布列塔尼语': 'bre', '切罗基语': 'chr', '齐切瓦语': 'nya', '楚瓦什语': 'chv', '康瓦尔语': 'cor', '科西嘉语': 'cos', '克里克语': 'cre', '克里米亚鞑靼语': 'cri', '迪维希语': 'div', '古英语': 'eno', '中古法语': 'frm', '弗留利语': 'fri', '富拉尼语': 'ful', '盖尔语': 'gla', '卢干达语': 'lug', '古希腊语': 'gra', '瓜拉尼语': 'grn', '夏威夷语': 'haw', '希利盖农语': 'hil', '伊多语': 'ido', '因特语': 'ina', '伊努克提图特语': 'iku', '爪哇语': 'jav', '卡拜尔语': 'kab', '格陵兰语': 'kal', '卡努里语': 'kau', '克什米尔语': 'kas', '卡舒比语': 'kah', '卢旺达语': 'kin', '刚果语': 'kon', '孔卡尼语': 'kok', '林堡语': 'lim', '林加拉语': 'lin', '逻辑语': 'loj', '低地德语': 'log', '下索布语': 'los', '迈蒂利语': 'mai', '曼克斯语': 'glv', '毛利语': 'mao', '马绍尔语': 'mah', '南恩德贝莱语': 'nbl', '那不勒斯语': 'nea', '西非书面语': 'nqo', '北方萨米语': 'sme', '挪威语': 'nor', '奥杰布瓦语': 'oji', '奥里亚语': 'ori', '奥罗莫语': 'orm', '奥塞梯语': 'oss', '邦板牙语': 'pam', '帕皮阿门托语': 'pap', '北索托语': 'ped', '克丘亚语': 'que', '罗曼什语': 'roh', '罗姆语': 'ro', '萨摩亚语': 'sm', '梵语': 'san', '苏格兰语': 'sco', '掸语': 'sha', '修纳语': 'sna', '信德语': 'snd', '桑海语': 'sol', '南索托语': 'sot', '叙利亚语': 'syr', '德顿语': 'tet', '提格利尼亚语': 'tir', '聪加语': 'tso', '契维语': 'twi', '高地索布语': 'ups', '文达语': 'ven', '瓦隆语': 'wln', '威尔士语': 'wel', '西弗里斯语': 'fry', '沃洛夫语': 'wol', '科萨语': 'xho', '意第绪语': 'yid', '约鲁巴语': 'yor', '扎扎其语': 'zaz', '祖鲁语': 'zul', '巽他语': 'sun', '苗语': 'hmn', '塞尔维亚语(西里尔文)': 'src'}


class MainWindow(FramelessWidget, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        # 通过线程创建百度翻译对象
        self.baidu_trans_obj = None
        self.baidu_trans_result = None
        self.baidu_trans_thread = BaiduTransThread()
        self.baidu_trans_thread.trigger.connect(self.getBaiduTransObj)
        self.baidu_trans_thread.start()
        # 窗口初始化
        super().__init__(*args, **kwargs)
        # 窗口设置
        self.setWindowIcon(QIcon(favicon_ico))
        font = QFont('微软雅黑')
        font.setPixelSize(14)
        self.setFont(font)
        self.setupUi(self)
        # 调整分辨率时不改变窗口大小
        self.sizeChanged.connect(lambda x: self.resize(x[0], x[1]))
        # 隐藏输入框清空按钮
        self.pushButton_5.hide()
        # 隐藏语音和复制按钮
        self.widget_4.hide()
        self.widget_5.hide()
        # 隐藏输出框
        self.textBrowser.hide()
        self.textBrowser_2.hide()
        # 语音和复制按钮点击事件
        self.pushButton_6.clicked.connect(self.voiceButtonClicked)
        self.pushButton_8.clicked.connect(self.voiceButtonClicked)
        self.pushButton_7.clicked.connect(self.copyButtonClicked)
        self.pushButton_9.clicked.connect(self.copyButtonClicked)
        # 底部输出框链接点击事件
        self.textBrowser_2.anchorClicked.connect(self.anchorClicked)
        # 下拉语言列表设置
        self.comboBox.addItems(exports.keys())
        self.comboBox.setCurrentIndex(0)
        self.comboBox.currentIndexChanged.connect(self.comboBoxCurrentIndexChanged)
        # 监听剪切板
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clipboardChanged)
        self.clipboard_flag = False
        # 翻译定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.startTrans)
        # 文本输入框当前内容
        self.textEditCurrentContent = ''
        # 全局截屏翻译快捷键
        self.screen_trans_hot_key = SystemHotkey()
        self.screen_trans_hot_key.register(['f1'], callback=lambda x: self.pushButton_4.click())
        # 翻译状态（True-正在翻译；False-翻译结束）
        self.trans_started = False
        # 主窗口尺寸缩放动画
        self.animation = QPropertyAnimation(self, b"size", self)
        self.animation.setDuration(100)  # 动画持续时间

    def getBaiduTransObj(self, obj):
        """ 创建百度翻译对象的线程结束
        线程结束时获取返回的百度翻译对象
        """
        if obj is None:
            msg = QMessageBox.question(self, '错误', '程序初始化失败，可能是网络不佳所致。是否重试？', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if msg == QMessageBox.Yes:
                self.baidu_trans_thread.start()
            else:
                self.close()
        self.baidu_trans_obj = obj

    @pyqtSlot()
    def on_checkBox_clicked(self):
        """ 复选框状态变更
        勾选状态开启复制翻译
        取消勾选关闭复制翻译
        """
        state = self.checkBox.checkState()
        if state == 2:
            self.clipboard_flag = True
        else:
            self.clipboard_flag = False

    def clipboardChanged(self):
        """ 剪切板数据变更
        开启复制翻译时，获取剪切板内容并发起翻译
        """
        if self.clipboard_flag and not self.trans_started:
            data = self.clipboard.mimeData()
            if 'text/plain' in data.formats():
                # 通过线程发起翻译
                self.start_trans_thread = StartTransThread(data.text(), 'zh')
                self.start_trans_thread.trigger.connect(self.outToFloatWindow)
                self.start_trans_thread.start()
                # 显示悬浮窗
                self.float_window = FloatWindow(data.text())
                self.float_window.pushButtonClicked.connect(self.gotoMainWindow)
                self.float_window.radioButtonClicked.connect(self.checkBox.click)
                self.float_window.show()
                move_widget(self.float_window, QDesktopWidget().screenGeometry(), QCursor.pos(), 10)
                # 通过线程关闭悬浮窗
                self.mouse_check_thread = MouseCheckThread(self.float_window)
                self.mouse_check_thread.trigger.connect(self.float_window.close)
                self.mouse_check_thread.start()
                # 标记正在翻译
                self.trans_started = True

    def gotoMainWindow(self, s):
        """从悬浮窗口转到主窗口"""
        self.float_window.close()
        if self.isMinimized() or not self.isVisible():  # 窗口最小化或不可见
            self.hide()
            self.showNormal()
        self.textEdit.setText(s)
        self.startTrans()

    def outToFloatWindow(self, data):
        """翻译结果输出到悬浮窗口"""
        # 标记翻译结束
        self.trans_started = False
        with contextlib.suppress(Exception):
            self.float_window.outResult(data)

    def comboBoxCurrentIndexChanged(self):
        """ 下拉列表索引变更
        切换语言种类时重新发起翻译
        """
        if self.textEdit.toPlainText():
            self.startTrans()

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """ 翻译按钮状态变更
        点击翻译按钮立即发起翻译
        """
        self.startTrans()

    @pyqtSlot()
    def on_textEdit_textChanged(self):
        """ 文本输入框内容变更
        文本输入框内容发生变化时对内容进行检查
        如果输入内容为图片，则对图片进行识别并发起翻译
        如果输入内容为文本，则设置一个定时器，定时结束时自动发起翻译
        """
        if '>正在识别翻译，请稍候...<' in self.textEdit.toHtml():
            return None
        self.timer.stop()  # 文本框内容发生变化时停止定时器
        text = self.textEdit.toPlainText().strip()
        if text:
            if text.find('file:///') == 0:  # 如果文本框输入文件则对文件进行检查，如果输入的是图片则进行识别翻译，否则弹窗提示
                file_name = text.split('\n')[0].replace('file:///', '')
                self.textEdit.setText('<i>正在识别翻译，请稍候...</i>')
                QApplication.processEvents()  # 刷新界面
                if file_name.split('.')[-1:][0].lower() not in ['jpg', 'png']:
                    QMessageBox.information(self, '提示', '仅支持 jpg 或 png 格式的图片')
                    self.textEdit.clear()
                    return None
                with open(file_name, 'rb') as f:
                    img = f.read()
                # 通过线程进行图像文字识别
                self.ocr_thread = BaiduOCRThread(img)
                self.ocr_thread.trigger.connect(self.transImageText)
                self.ocr_thread.start()
            elif text != self.textEditCurrentContent:
                self.timer.start(1000)  # 如果文本框输入的不是文件且内容不为空则启动 1000ms 定时器
            self.textEditCurrentContent = text
        else:
            # 清空输出框内容
            self.textBrowser.clear()
            self.textBrowser_2.clear()
            # 重设窗口大小
            self.hide_widget()
            self.animation.setEndValue(QSize(MIN_W, MIN_H))
            self.animation.start()
            self.animation.finished.connect(lambda: self.change_widget())
        # 输入框内容不为空时显示清空按钮，否则隐藏清空按钮
        if self.textEdit.toPlainText():
            self.pushButton_5.show()
        else:
            self.pushButton_5.hide()

    def transImageText(self, text):
        """ OCR线程结束
        获取识别文本，并进行翻译
        """
        if text:
            self.textEdit.setText(text)
            self.startTrans()
        else:
            QMessageBox.information(self, '提示', '没有从图片中识别到文字！')
            self.textEdit.clear()

    def startTrans(self):
        """启动翻译并输出翻译结果"""
        if self.trans_started:
            return None
        self.timer.stop()  # 主动发起翻译时关闭定时器
        if self.baidu_trans_obj is None:
            QMessageBox.information(self, '提示', '程序正在初始化中，请稍候重试！')
            return None
        query = self.textEdit.toPlainText().strip()
        if not query:
            QMessageBox.information(self, '提示', '请输入翻译内容')
            return None
        to_str = exports.get(self.comboBox.currentText())
        if not to_str:
            QMessageBox.information(self, '提示', '请选择目标语言')
            return None
        # 通过线程发起翻译
        self.start_trans_thread = StartTransThread(query, to_str)
        self.start_trans_thread.trigger.connect(self.outResult)
        self.start_trans_thread.start()
        self.trans_started = True

    def outResult(self, data):
        """ 发起翻译的线程结束
        线程结束时获取翻译结果并输出
        """
        self.trans_started = False
        if not self.textEdit.toPlainText().strip():
            # 输入框没有内容则直接返回
            return None
        if not data:
            QMessageBox.information(self, '提示', '翻译结果为空，请重试！')
            return None
        self.baidu_trans_result = data  # 翻译结果
        trans_result = get_trans_result(data)  # 直译
        spell_html = get_spell_html(data)  # 音标
        comment_html = get_comment_html(data)  # 释义
        exchange_html = get_exchange_html(data)  # 形态
        example_html = get_example_html(data)  # 例句
        if spell_html or comment_html:
            trans_result_html = '<div style="font-size: 16px; color: #3C3C3C;"><h4>{}</h4></div>'.format(trans_result)
            explanation_html = '<div style="font-size: 16px; color: #3C3C3C;"><p>{}</p><p>{}</p><p>{}</p><p>{}</p></div>'.format(spell_html, comment_html, exchange_html, example_html)
            # 设置输出内容
            self.textBrowser.setText(trans_result_html)
            self.textBrowser_2.setText(explanation_html)
            # 重设窗口大小
            if self.height() != MAX_H:
                self.hide_widget()
                self.animation.setEndValue(QSize(MAX_W, MAX_H))
                self.animation.start()
                self.animation.finished.connect(lambda: self.change_widget(1))
        else:
            trans_result_html = '<div style="font-size: 16px; color: #3C3C3C;">{}<div>'.format(trans_result)
            # 设置输出内容
            self.textBrowser_2.setText(trans_result_html)
            # 重设窗口大小
            h = self.widget_4.height() + self.textBrowser.height()
            if self.height() != MAX_H - h:
                self.hide_widget()
                self.animation.setEndValue(QSize(MAX_W, MAX_H - h))
                self.animation.start()
                self.animation.finished.connect(lambda: self.change_widget(2))

    def voiceButtonClicked(self):
        """点击语音播报按钮"""
        text = self.baidu_trans_result['trans_result']['data'][0].get('dst')
        lan = self.baidu_trans_result['trans_result'].get('to')
        # 通过线程下载并播放发音
        self.voice_thread = DownloadVoiceThread(lan, text)
        self.voice_thread.trigger.connect(self.playVoice)
        self.voice_thread.start()

    def copyButtonClicked(self):
        """点击复制内容按钮"""
        text = self.baidu_trans_result['trans_result']['data'][0].get('dst')
        self.clipboard.setText(text)

    def anchorClicked(self, url):
        """ 点击底部输出框中的链接
        点击输出框中音标发音按钮时，获取单词发音并播放
        点击输出框中文本链接的时候，提取文本并进行翻译
        """
        url = url.url().replace('#', '')
        if url in ['英', '美', '音']:  # 点击发音按钮
            text = self.baidu_trans_result['trans_result']['data'][0].get('src')
            if url == '英':
                lan = 'en'
            elif url == '美':
                lan = 'uk'
            else:
                lan = 'zh'
            # 通过线程下载并播放发音
            self.voice_thread = DownloadVoiceThread(lan, text)
            self.voice_thread.trigger.connect(self.playVoice)
            self.voice_thread.start()
        else:  # 点击文本链接
            self.textEdit.setText(url)
            self.startTrans()

    def playVoice(self, voice_data):
        """ 下载单词发音的线程结束
        获取单词发音并创建播放器进行播放
        """
        # 将语音写入缓冲区
        buffer = QBuffer(self)
        buffer.setData(voice_data)
        buffer.open(QIODevice.ReadOnly)
        # 创建播放器
        player = QMediaPlayer(self)
        player.setVolume(100)
        player.setMedia(QMediaContent(), buffer)
        sleep(0.1)  # 延时等待 setMedia 完成。
        # 播放语音
        player.play()

    @pyqtSlot()
    def on_pushButton_4_clicked(self):
        """ 点击截图翻译按钮
        隐藏主窗口，启动截屏
        """
        self.hide()  # 隐藏主窗口
        self.screenshot = Screenshot()  # 创建截屏窗口
        self.screenshot.completed.connect(self.screenshotCompleted)
        self.screenshot.show()  # 显示截屏窗口

    def screenshotCompleted(self, img):
        """ 截屏完成
        获取屏幕截图，并进行文字识别
        """
        self.screenshot.deleteLater()  # 回收截屏窗口
        self.showNormal()  # 显示主窗口
        img_data = img.data()  # 获取截图
        if img_data:
            self.textEdit.setText('<i>正在识别翻译，请稍候...</i>')
            QApplication.processEvents()  # 刷新界面
            # 通过线程进行图像文字识别
            self.ocr_thread = BaiduOCRThread(img_data)
            self.ocr_thread.trigger.connect(self.transImageText)
            self.ocr_thread.start()

    def hide_widget(self):
        """隐藏部件"""
        self.textBrowser.hide()
        self.textBrowser_2.hide()
        self.widget_4.hide()
        self.widget_5.hide()

    def change_widget(self, mode=0):
        """调整部件"""
        self.hide_widget()
        if mode == 1:
            self.widget_4.show()
            self.textBrowser.show()
            self.textBrowser_2.show()
        elif mode == 2:
            self.widget_5.show()
            self.textBrowser_2.show()


class FloatWindow(FloatWidget, Ui_FloatWindow):
    def __init__(self, query: str, *args, **kwargs):
        # 窗口初始化
        super().__init__(*args, **kwargs)
        # 窗口设置
        font = QFont('微软雅黑')
        font.setPixelSize(14)
        self.setFont(font)
        self.setupUi(self)
        # 翻译内容
        self.query = query
        # 信号连接
        self.radioButton.clicked.connect(lambda x: self.radioButtonClicked.emit(self.radioButton.isChecked()))
        self.pushButton.clicked.connect(lambda x: self.pushButtonClicked.emit(self.query))
        self.textBrowser_2.anchorClicked.connect(self.anchorClicked)
        # 初始化输出
        self.textBrowser.setText(self.query)
        self.textBrowser_2.setText("<i style='color: #606060;'>正在翻译...</i>")

    def outResult(self, data):
        """输出翻译结果"""
        trans_result = get_trans_result(data)  # 直译
        word_means = get_word_means(data)  # 释义
        spell_html = get_spell_html(data)  # 音标
        if spell_html:
            explanation_html = '<div style="color: #3C3C3C;"><p>{}</p></div>'.format(spell_html)
            word_means_html = '<div style="color: #3C3C3C;">{}</div>'.format(word_means if word_means else trans_result)
            self.textBrowser_2.setText(explanation_html)
            self.textBrowser_3.setText(word_means_html)
        else:
            trans_result_html = '<div style="color: #3C3C3C;">{}<div>'.format(trans_result)
            self.textBrowser_3.setText(trans_result_html)
            self.textBrowser_2.hide()

    def anchorClicked(self, url):
        """ 点击底部输出框中的链接
        点击输出框中音标发音按钮时，获取单词发音并播放
        点击输出框中文本链接的时候，提取文本并进行翻译
        """
        url = url.url().replace('#', '')
        if url in ['英', '美', '音']:  # 点击发音按钮
            if url == '英':
                lan = 'en'
            elif url == '美':
                lan = 'uk'
            else:
                lan = 'zh'
            # 通过线程下载并播放发音
            self.voice_thread = DownloadVoiceThread(lan, self.query)
            self.voice_thread.trigger.connect(self.playVoice)
            self.voice_thread.start()

    def playVoice(self, voice_data):
        """ 下载单词发音的线程结束
        获取单词发音并创建播放器进行播放
        """
        # 将语音写入缓冲区
        buffer = QBuffer(self)
        buffer.setData(voice_data)
        buffer.open(QIODevice.ReadOnly)
        # 创建播放器
        player = QMediaPlayer(self)
        player.setVolume(100)
        player.setMedia(QMediaContent(), buffer)
        sleep(0.1)  # 延时等待 setMedia 完成。
        # 播放语音
        player.play()


if __name__ == '__main__':
    # 创建QApplication类的实例
    app = QApplication(sys.argv)
    # 汉化右键菜单
    translator = QTranslator()
    translator.load(widgets_zh_CN_qm)
    app.installTranslator(translator)
    # 创建主窗口
    window = MainWindow()
    window.show()
    # 进入程序的主循环，并通过exit函数确保主循环安全结束
    sys.exit(app.exec_())
