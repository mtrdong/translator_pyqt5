# -*- coding: utf-8 -*-
import sys
from time import sleep

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtMultimedia
from PyQt5 import QtWidgets
from system_hotkey import SystemHotkey
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE, SWP_SHOWWINDOW, HWND_NOTOPMOST
from win32gui import SetWindowPos

from rc import images_rc  # 导入图片资源
from res import widgets_zh_CN_qm
from threads import *
from ui.MainWindow_ui import Ui_MainWindow
from utils import *
from widgets import FramelessWidget
from window.FloatWindow import FloatWindow
from window.ScreenshotWindow import ScreenshotWindow

# 百度翻译语言选项
lang_baidu = {
    '自动检测': '',
    '中文(简体)': 'zh',
    '英语': 'en',
    '日语': 'jp',
    '泰语': 'th',
    '西班牙语': 'spa',
    '阿拉伯语': 'ara',
    '法语': 'fra',
    '韩语': 'kor',
    '俄语': 'ru',
    '德语': 'de',
    '葡萄牙语': 'pt',
    '意大利语': 'it',
    '希腊语': 'el',
    '荷兰语': 'nl',
    '波兰语': 'pl',
    '芬兰语': 'fin',
    '捷克语': 'cs',
    '保加利亚语': 'bul',
    '丹麦语': 'dan',
    '爱沙尼亚语': 'est',
    '匈牙利语': 'hu',
    '罗马尼亚语': 'rom',
    '斯洛文尼亚语': 'slo',
    '瑞典语': 'swe',
    '越南语': 'vie',
    '中文(粤语)': 'yue',
    '中文(繁体)': 'cht',
    '中文(文言文)': 'wyw',
    '南非荷兰语': 'afr',
    '阿尔巴尼亚语': 'alb',
    '阿姆哈拉语': 'amh',
    '亚美尼亚语': 'arm',
    '阿萨姆语': 'asm',
    '阿斯图里亚斯语': 'ast',
    '阿塞拜疆语': 'aze',
    '巴斯克语': 'baq',
    '白俄罗斯语': 'bel',
    '孟加拉语': 'ben',
    '波斯尼亚语': 'bos',
    '缅甸语': 'bur',
    '加泰罗尼亚语': 'cat',
    '宿务语': 'ceb',
    '克罗地亚语': 'hrv',
    '世界语': 'epo',
    '法罗语': 'fao',
    '菲律宾语': 'fil',
    '加利西亚语': 'glg',
    '格鲁吉亚语': 'geo',
    '古吉拉特语': 'guj',
    '豪萨语': 'hau',
    '希伯来语': 'heb',
    '印地语': 'hi',
    '冰岛语': 'ice',
    '伊博语': 'ibo',
    '印尼语': 'id',
    '爱尔兰语': 'gle',
    '卡纳达语': 'kan',
    '克林贡语': 'kli',
    '库尔德语': 'kur',
    '老挝语': 'lao',
    '拉丁语': 'lat',
    '拉脱维亚语': 'lav',
    '立陶宛语': 'lit',
    '卢森堡语': 'ltz',
    '马其顿语': 'mac',
    '马拉加斯语': 'mg',
    '马来语': 'may',
    '马拉雅拉姆语': 'mal',
    '马耳他语': 'mlt',
    '马拉地语': 'mar',
    '尼泊尔语': 'nep',
    '新挪威语': 'nno',
    '波斯语': 'per',
    '萨丁尼亚语': 'srd',
    '塞尔维亚语(拉丁文)': 'srp',
    '僧伽罗语 ': 'sin',
    '斯洛伐克语': 'sk',
    '索马里语': 'som',
    '斯瓦希里语': 'swa',
    '他加禄语': 'tgl',
    '塔吉克语': 'tgk',
    '泰米尔语': 'tam',
    '鞑靼语': 'tat',
    '泰卢固语': 'tel',
    '土耳其语': 'tr',
    '土库曼语': 'tuk',
    '乌克兰语': 'ukr',
    '乌尔都语': 'urd',
    '奥克语': 'oci',
    '吉尔吉斯语': 'kir',
    '普什图语': 'pus',
    '高棉语': 'hkm',
    '海地语': 'ht',
    '书面挪威语': 'nob',
    '旁遮普语': 'pan',
    '阿尔及利亚阿拉伯语': 'arq',
    '比斯拉马语': 'bis',
    '加拿大法语': 'frn',
    '哈卡钦语': 'hak',
    '胡帕语': 'hup',
    '印古什语': 'ing',
    '拉特加莱语': 'lag',
    '毛里求斯克里奥尔语': 'mau',
    '黑山语': 'mot',
    '巴西葡萄牙语': 'pot',
    '卢森尼亚语': 'ruy',
    '塞尔维亚-克罗地亚语': 'sec',
    '西里西亚语': 'sil',
    '突尼斯阿拉伯语': 'tua',
    '亚齐语': 'ach',
    '阿肯语': 'aka',
    '阿拉贡语': 'arg',
    '艾马拉语': 'aym',
    '俾路支语': 'bal',
    '巴什基尔语': 'bak',
    '本巴语': 'bem',
    '柏柏尔语': 'ber',
    '博杰普尔语': 'bho',
    '比林语': 'bli',
    '布列塔尼语': 'bre',
    '切罗基语': 'chr',
    '齐切瓦语': 'nya',
    '楚瓦什语': 'chv',
    '康瓦尔语': 'cor',
    '科西嘉语': 'cos',
    '克里克语': 'cre',
    '克里米亚鞑靼语': 'cri',
    '迪维希语': 'div',
    '古英语': 'eno',
    '中古法语': 'frm',
    '弗留利语': 'fri',
    '富拉尼语': 'ful',
    '盖尔语': 'gla',
    '卢干达语': 'lug',
    '古希腊语': 'gra',
    '瓜拉尼语': 'grn',
    '夏威夷语': 'haw',
    '希利盖农语': 'hil',
    '伊多语': 'ido',
    '因特语': 'ina',
    '伊努克提图特语': 'iku',
    '爪哇语': 'jav',
    '卡拜尔语': 'kab',
    '格陵兰语': 'kal',
    '卡努里语': 'kau',
    '克什米尔语': 'kas',
    '卡舒比语': 'kah',
    '卢旺达语': 'kin',
    '刚果语': 'kon',
    '孔卡尼语': 'kok',
    '林堡语': 'lim',
    '林加拉语': 'lin',
    '逻辑语': 'loj',
    '低地德语': 'log',
    '下索布语': 'los',
    '迈蒂利语': 'mai',
    '曼克斯语': 'glv',
    '毛利语': 'mao',
    '马绍尔语': 'mah',
    '南恩德贝莱语': 'nbl',
    '那不勒斯语': 'nea',
    '西非书面语': 'nqo',
    '北方萨米语': 'sme',
    '挪威语': 'nor',
    '奥杰布瓦语': 'oji',
    '奥里亚语': 'ori',
    '奥罗莫语': 'orm',
    '奥塞梯语': 'oss',
    '邦板牙语': 'pam',
    '帕皮阿门托语': 'pap',
    '北索托语': 'ped',
    '克丘亚语': 'que',
    '罗曼什语': 'roh',
    '罗姆语': 'ro',
    '萨摩亚语': 'sm',
    '梵语': 'san',
    '苏格兰语': 'sco',
    '掸语': 'sha',
    '修纳语': 'sna',
    '信德语': 'snd',
    '桑海语': 'sol',
    '南索托语': 'sot',
    '叙利亚语': 'syr',
    '德顿语': 'tet',
    '提格利尼亚语': 'tir',
    '聪加语': 'tso',
    '契维语': 'twi',
    '高地索布语': 'ups',
    '文达语': 'ven',
    '瓦隆语': 'wln',
    '威尔士语': 'wel',
    '西弗里斯语': 'fry',
    '沃洛夫语': 'wol',
    '科萨语': 'xho',
    '意第绪语': 'yid',
    '约鲁巴语': 'yor',
    '扎扎其语': 'zaz',
    '祖鲁语': 'zul',
    '巽他语': 'sun',
    '苗语': 'hmn',
    '塞尔维亚语(西里尔文)': 'src'
}
# 有道词典语言选项
lang_youdao = {
    '中英': 'en',
    '中法': 'fr',
    '中韩': 'ko',
    '中日': 'ja',
}
# 谷歌翻译语言选项
lang_google = {
    '检测语言': 'auto',
    '阿尔巴尼亚语': 'sq',
    '阿拉伯语': 'ar',
    '阿姆哈拉语': 'am',
    '阿萨姆语': 'as',
    '阿塞拜疆语': 'az',
    '埃维语': 'ee',
    '艾马拉语': 'ay',
    '爱尔兰语': 'ga',
    '爱沙尼亚语': 'et',
    '奥利亚语': 'or',
    '奥罗莫语': 'om',
    '巴斯克语': 'eu',
    '白俄罗斯语': 'be',
    '班巴拉语': 'bm',
    '保加利亚语': 'bg',
    '冰岛语': 'is',
    '波兰语': 'pl',
    '波斯尼亚语': 'bs',
    '波斯语': 'fa',
    '博杰普尔语': 'bho',
    '布尔语': 'af',
    '鞑靼语': 'tt',
    '丹麦语': 'da',
    '德语': 'de',
    '迪维希语': 'dv',
    '蒂格尼亚语': 'ti',
    '多格来语': 'doi',
    '俄语': 'ru',
    '法语': 'fr',
    '梵语': 'sa',
    '菲律宾语': 'tl',
    '芬兰语': 'fi',
    '弗里西语': 'fy',
    '高棉语': 'km',
    '格鲁吉亚语': 'ka',
    '贡根语': 'gom',
    '古吉拉特语': 'gu',
    '瓜拉尼语': 'gn',
    '哈萨克语': 'kk',
    '海地克里奥尔语': 'ht',
    '韩语': 'ko',
    '豪萨语': 'ha',
    '荷兰语': 'nl',
    '吉尔吉斯语': 'ky',
    '加利西亚语': 'gl',
    '加泰罗尼亚语': 'ca',
    '捷克语': 'cs',
    '卡纳达语': 'kn',
    '科西嘉语': 'co',
    '克里奥尔语': 'kri',
    '克罗地亚语': 'hr',
    '克丘亚语': 'qu',
    '库尔德语（库尔曼吉语）': 'ku',
    '库尔德语（索拉尼）': 'ckb',
    '拉丁语': 'la',
    '拉脱维亚语': 'lv',
    '老挝语': 'lo',
    '立陶宛语': 'lt',
    '林格拉语': 'ln',
    '卢干达语': 'lg',
    '卢森堡语': 'lb',
    '卢旺达语': 'rw',
    '罗马尼亚语': 'ro',
    '马尔加什语': 'mg',
    '马耳他语': 'mt',
    '马拉地语': 'mr',
    '马拉雅拉姆语': 'ml',
    '马来语': 'ms',
    '马其顿语': 'mk',
    '迈蒂利语': 'mai',
    '毛利语': 'mi',
    '梅泰语（曼尼普尔语）': 'mni-Mtei',
    '蒙古语': 'mn',
    '孟加拉语': 'bn',
    '米佐语': 'lus',
    '缅甸语': 'my',
    '苗语': 'hmn',
    '南非科萨语': 'xh',
    '南非祖鲁语': 'zu',
    '尼泊尔语': 'ne',
    '挪威语': 'no',
    '旁遮普语': 'pa',
    '葡萄牙语': 'pt',
    '普什图语': 'ps',
    '齐切瓦语': 'ny',
    '契维语': 'ak',
    '日语': 'ja',
    '瑞典语': 'sv',
    '萨摩亚语': 'sm',
    '塞尔维亚语': 'sr',
    '塞佩蒂语': 'nso',
    '塞索托语': 'st',
    '僧伽罗语': 'si',
    '世界语': 'eo',
    '斯洛伐克语': 'sk',
    '斯洛文尼亚语': 'sl',
    '斯瓦希里语': 'sw',
    '苏格兰盖尔语': 'gd',
    '宿务语': 'ceb',
    '索马里语': 'so',
    '塔吉克语': 'tg',
    '泰卢固语': 'te',
    '泰米尔语': 'ta',
    '泰语': 'th',
    '土耳其语': 'tr',
    '土库曼语': 'tk',
    '威尔士语': 'cy',
    '维吾尔语': 'ug',
    '乌尔都语': 'ur',
    '乌克兰语': 'uk',
    '乌兹别克语': 'uz',
    '西班牙语': 'es',
    '希伯来语': 'iw',
    '希腊语': 'el',
    '夏威夷语': 'haw',
    '信德语': 'sd',
    '匈牙利语': 'hu',
    '修纳语': 'sn',
    '亚美尼亚语': 'hy',
    '伊博语': 'ig',
    '伊洛卡诺语': 'ilo',
    '意大利语': 'it',
    '意第绪语': 'yi',
    '印地语': 'hi',
    '印尼巽他语': 'su',
    '印尼语': 'id',
    '印尼爪哇语': 'jw',
    '英语': 'en',
    '约鲁巴语': 'yo',
    '越南语': 'vi',
    '中文（繁体）': 'zh-TW',
    '中文（简体）': 'zh-CN',
    '宗加语': 'ts',
}

# 翻译引擎
engine = {
    '百度翻译': 'baidu',
    '有道翻译': 'youdao',
    '谷歌翻译': 'google',
}

# 窗口最大高度
MAX_H = 735


class MainWindow(FramelessWidget, Ui_MainWindow):
    """主窗口"""
    def __init__(self, *args, **kwargs):
        # 窗口设置
        super().__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(':icon/favicon.ico'))
        font = QtGui.QFont('微软雅黑')
        font.setPixelSize(14)
        self.setFont(font)
        self.setupUi(self)
        self.resize(self.minimumSize())
        # 隐藏输入框清空按钮
        self.pushButton_7.hide()
        # 隐藏输出框和输出控件
        self.hideWidget()
        # 通过线程调整部件透明度实现淡入效果
        self.fade_in_thread = FadeInThread(self.widget_2)
        # 语音和复制按钮点击事件
        self.pushButton_8.clicked.connect(self.voiceButtonClicked)
        self.pushButton_10.clicked.connect(self.voiceButtonClicked)
        self.pushButton_9.clicked.connect(self.copyButtonClicked)
        self.pushButton_11.clicked.connect(self.copyButtonClicked)
        # 底部输出框链接点击事件
        self.textBrowser_2.anchorClicked.connect(self.anchorClicked)
        # 下拉列表初始化
        self.comboBox.addItems(engine.keys())
        self.comboBox.setCurrentIndex(0)
        self.comboBox.currentIndexChanged.connect(self.comboBoxCurrentIndexChanged)
        self.source_lang = None  # 源语言代码
        self.target_lang = None  # 目标语言代码
        self.comboBox_2DisableIndex = 0
        self.comboBox_3DisableIndex = 0
        self.comboBox_2.currentIndexChanged.connect(self.comboBox_2CurrentIndexChanged)
        self.comboBox_3.currentIndexChanged.connect(self.comboBox_3CurrentIndexChanged)
        self.setLangItems()
        # 通过线程创建翻译引擎对象
        self.transl_engine = None  # 翻译引擎对象
        self.transl_result = None  # 翻译结果
        self.getTranslEngine()
        # 监听剪切板
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clipboardChanged)
        self.clipboard_flag = False
        # 翻译定时器
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.startTransl)
        # 文本输入框当前内容
        self.textEditCurrentContent = ''
        # 全局截屏翻译快捷键
        self.screen_trans_hot_key = SystemHotkey()
        self.screen_trans_hot_key.register(['f1'], callback=lambda x: self.pushButton_4.click())
        # 翻译状态（True-正在翻译；False-翻译结束）
        self.transl_started = False
        # 主窗口大小变化动画
        self.animation = QtCore.QPropertyAnimation(self, b"size", self)
        self.animation.setDuration(200)  # 动画持续时间
        # 屏幕缩放时自动调整窗口尺寸
        self.sizeChanged.connect(lambda x: self.resize(self.minimumSize()))

    @QtCore.pyqtSlot()
    def on_checkBox_clicked(self):
        """ 复选按钮状态变更
        1. 勾选状态开启复制翻译
        2. 取消勾选关闭复制翻译
        """
        state = self.checkBox.checkState()
        if state == 2:
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
        if not hasattr(self, 'screenshot_window'):
            self.hide()  # 隐藏主窗口
            self.screenshot_window = ScreenshotWindow()  # 创建截屏窗口
            self.screenshot_window.completed.connect(self.screenshotCompleted)
            self.screenshot_window.destroyed.connect(self.deleteScreenshotWindow)
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
        if engine.get(self.comboBox.currentText()) != 'youdao':
            if self.source_lang and self.source_lang != 'auto':
                combobox_2_index = self.comboBox_2.currentIndex()
                combobox_3_index = self.comboBox_3.currentIndex()
                self.comboBox_2.setCurrentIndex(combobox_3_index + 1)
                self.comboBox_3.blockSignals(True)  # 关闭信号连接
                self.comboBox_3.setCurrentIndex(combobox_2_index - 1)
                self.comboBox_3.blockSignals(False)  # 恢复信号连接

    @QtCore.pyqtSlot()
    def on_textEdit_textChanged(self):
        """ 文本输入框内容变更
        文本输入框内容发生变化时对内容进行检查
        如果输入内容为图片，则对图片进行识别并发起翻译
        如果输入内容为文本，则设置一个定时器，定时结束时自动发起翻译
        """
        self.timer.stop()  # 文本框内容发生变化时停止定时器
        text = self.textEdit.toPlainText().strip()
        if text:
            if text.find('file:///') == 0:  # 如果文本框输入文件则对文件进行检查，如果输入的是图片则进行识别翻译，否则弹窗提示
                file_name = text.split('\n')[0].replace('file:///', '')
                self.textEdit.blockSignals(True)  # 关闭信号连接
                self.textEdit.setText('<i>正在识别翻译，请稍候...</i>')
                QtWidgets.QApplication.processEvents()  # 刷新界面
                if file_name.split('.')[-1:][0].lower() not in ['jpg', 'png']:
                    QtWidgets.QMessageBox.information(self, '提示', '仅支持 jpg 或 png 格式的图片')
                    self.textEdit.clear()
                    return None
                self.textEdit.blockSignals(False)  # 恢复信号连接
                with open(file_name, 'rb') as f:
                    img = f.read()
                # 通过线程进行图像文字识别
                self.ocr_thread = BaiduOCRThread(img)
                self.ocr_thread.trigger.connect(self.translImageText)
                self.ocr_thread.start()
            elif text != self.textEditCurrentContent:
                self.timer.start(1000)  # 如果文本框输入的不是文件且内容不为空则启动 1000ms 定时器
            self.textEditCurrentContent = text
        else:
            # 清空输出框内容
            self.textBrowser.clear()
            self.textBrowser_2.clear()
            # 重设窗口大小
            self.modifyUI()
        # 输入框内容不为空时显示清空按钮，否则隐藏清空按钮
        if self.textEdit.toPlainText():
            self.pushButton_7.show()
        else:
            self.pushButton_7.hide()

    def clipboardChanged(self):
        """ 剪切板数据变更
        开启复制翻译时，获取剪切板内容并发起翻译
        """
        if self.clipboard_flag and not self.transl_started:
            data = self.clipboard.mimeData()
            if 'text/plain' in data.formats():
                # 通过线程发起翻译
                self.start_trans_thread = StartTransThread(data.text(), self.target_lang)
                self.start_trans_thread.trigger.connect(self.outToFloatWindow)
                self.start_trans_thread.start()
                if not hasattr(self, 'float_window'):
                    # 显示悬浮窗
                    self.float_window = FloatWindow(data.text())
                    self.float_window.pushButtonClicked.connect(self.gotoMainWindow)
                    self.float_window.radioButtonClicked.connect(self.checkBox.click)
                    self.float_window.destroyed.connect(self.deleteFloatWindow)
                    self.float_window.show()
                # 标记正在翻译
                self.transl_started = True

    def outToFloatWindow(self, data):
        """翻译结果输出到悬浮窗口"""
        # 标记翻译结束
        self.transl_started = False
        if hasattr(self, 'float_window'):
            self.float_window.outResult(data)

    def gotoMainWindow(self, s):
        """从悬浮窗口转到主窗口"""
        self.float_window.close()
        if self.isMinimized() or not self.isVisible():  # 窗口最小化或不可见
            self.hide()
            self.showNormal()
        self.textEdit.setText(s)
        self.startTransl()

    def getTranslEngine(self):
        """通过线程创建翻译引擎对象"""
        self.transl_thread = TranslThread(engine.get(self.comboBox.currentText()))
        self.transl_thread.trigger.connect(self.setTranslEngine)
        self.transl_thread.start()

    def setTranslEngine(self, obj):
        """创建翻译引擎对象的线程结束"""
        if obj is None:
            msg = QtWidgets.QMessageBox.question(
                self,
                '错误',
                '程序初始化失败，可能是网络不佳所致。是否重试？',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes
            )
            if msg == QtWidgets.QMessageBox.Yes:
                self.getTranslEngine()
            else:
                self.close()
        self.transl_engine = obj

    def setLangItems(self):
        """设置源语言和目标语言下拉列表"""
        engine_val = engine.get(self.comboBox.currentText())
        if engine_val == 'youdao':
            source_lang_items = ['自动检测语言']
            target_lang_items = list(lang_youdao.keys())
        else:
            source_lang_items = list(eval(f'lang_{engine_val}.keys()'))
            target_lang_items = source_lang_items.copy()
            target_lang_items.pop(0)
        # 源语言下拉列表
        self.comboBox_2.blockSignals(True)  # 关闭信号连接
        self.comboBox_2.clear()
        self.comboBox_2.addItems(source_lang_items)
        self.comboBox_2.setCurrentIndex(0)
        self.comboBox_2.blockSignals(False)  # 恢复信号连接
        # 目标语言下拉列表
        self.comboBox_3.blockSignals(True)
        self.comboBox_3.clear()
        self.comboBox_3.addItems(target_lang_items)
        self.comboBox_3.setCurrentIndex(0)
        self.comboBox_3.blockSignals(False)
        # 设置源语言和目标语言，并刷新源语言/目标语言下拉列表禁用选项
        self.source_lang = eval(f'lang_{engine_val}.get("{source_lang_items[0]}")')
        self.target_lang = eval(f'lang_{engine_val}.get("{target_lang_items[0]}")')
        self.refreshDisableIndex()

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
        engine_val = engine.get(self.comboBox.currentText())
        self.source_lang = eval(f'lang_{engine_val}.get("{self.comboBox_2.currentText()}")')
        if engine_val != 'youdao':
            self.refreshDisableIndex()
            if engine_val == 'baidu':  # TODO 暂时仅支持百度翻译
                if self.textEdit.toPlainText():
                    self.startTransl()

    def comboBox_3CurrentIndexChanged(self):
        """ 目标语言下拉列表索引变更
        1. 获取目标语言代码
        2. 刷新语言下拉禁用选项
        3. 发起翻译
        """
        engine_val = engine.get(self.comboBox.currentText())
        self.target_lang = eval(f'lang_{engine_val}.get("{self.comboBox_3.currentText()}")')
        if engine_val != 'youdao':
            self.refreshDisableIndex()
            if engine_val == 'baidu':  # TODO 暂时仅支持百度翻译
                if self.textEdit.toPlainText():
                    self.startTransl()

    def refreshDisableIndex(self):
        """刷新源语言/目标语言下拉禁用选项"""
        if engine.get(self.comboBox.currentText()) != 'youdao':
            # 解除上次禁用选项
            self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 1 | 32, QtCore.Qt.UserRole - 1)
            self.comboBox_3.setItemData(self.comboBox_3DisableIndex, 1 | 32, QtCore.Qt.UserRole - 1)
            if self.source_lang and self.source_lang != 'auto':
                self.comboBox_2DisableIndex = self.comboBox_3.currentIndex() + 1
                self.comboBox_3DisableIndex = self.comboBox_2.currentIndex() - 1
                self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 0, QtCore.Qt.UserRole - 1)
                self.comboBox_3.setItemData(self.comboBox_3DisableIndex, 0, QtCore.Qt.UserRole - 1)
            else:
                self.comboBox_2DisableIndex = self.comboBox_3.currentIndex() + 1
                self.comboBox_2.setItemData(self.comboBox_2DisableIndex, 0, QtCore.Qt.UserRole - 1)

    def screenshotCompleted(self, img):
        """ 截屏完成
        获取屏幕截图，并进行文字识别
        """
        self.showNormal()  # 显示主窗口
        img_data = img.data()  # 获取截图
        if img_data:
            self.textEdit.blockSignals(True)
            self.textEdit.setText('<i>正在识别翻译，请稍候...</i>')
            self.textEdit.blockSignals(False)
            QtWidgets.QApplication.processEvents()  # 刷新界面
            # 通过线程进行图像文字识别
            self.ocr_thread = BaiduOCRThread(img_data)
            self.ocr_thread.trigger.connect(self.translImageText)
            self.ocr_thread.start()

    def translImageText(self, text):
        """ OCR线程结束
        获取识别文本，并进行翻译
        """
        if text:
            self.textEdit.setText(text)
            self.startTransl()
        else:
            QtWidgets.QMessageBox.information(self, '提示', '没有从图片中识别到文字！')
            self.textEdit.blockSignals(True)
            self.textEdit.clear()
            self.textEdit.blockSignals(False)

    def startTransl(self):
        """启动翻译并输出翻译结果"""
        self.timer.stop()  # 主动发起翻译时关闭定时器
        if engine.get(self.comboBox.currentText()) != 'baidu':  # TODO 暂时仅支持百度翻译
            QtWidgets.QMessageBox.information(self, '提示', '目前仅支持百度翻译！')
            return None
        if self.transl_started:
            return None
        if self.transl_engine is None:
            QtWidgets.QMessageBox.information(self, '提示', '程序正在初始化中，请稍候重试！')
            return None
        query = self.textEdit.toPlainText().strip()
        if not query:
            QtWidgets.QMessageBox.information(self, '提示', '请输入翻译内容')
            return None
        # 通过线程发起翻译
        self.start_trans_thread = StartTransThread(query, self.target_lang, self.source_lang)
        self.start_trans_thread.trigger.connect(self.outResult)
        self.start_trans_thread.start()
        self.transl_started = True

    def outResult(self, data):
        """ 发起翻译的线程结束
        线程结束时获取翻译结果并输出
        """
        self.transl_started = False
        if not self.textEdit.toPlainText().strip():
            # 输入框没有内容则直接返回
            return None
        if not data:
            QtWidgets.QMessageBox.information(self, '提示', '翻译结果为空，请重试！')
            return None
        self.transl_result = data  # 翻译结果
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
            self.modifyUI(1)
        else:
            trans_result_html = '<div style="font-size: 16px; color: #3C3C3C;">{}<div>'.format(trans_result)
            # 设置输出内容
            self.textBrowser_2.setText(trans_result_html)
            # 重设窗口大小
            self.modifyUI(2)
        # 自动纠正目标语言
        to_str = data['trans_result']['to']
        if self.target_lang != to_str:
            index = list(eval(f'lang_{engine.get(self.comboBox.currentText())}.values()')).index(to_str) - 1
            self.comboBox_3.blockSignals(True)  # 关闭信号连接
            self.comboBox_3.setCurrentIndex(index)
            self.comboBox_3.blockSignals(False)  # 恢复信号连接
            self.refreshDisableIndex()

    def voiceButtonClicked(self):
        """点击语音播报按钮"""
        text = self.transl_result['trans_result']['data'][0].get('dst')
        lan = self.transl_result['trans_result'].get('to')
        # 通过线程下载并播放发音
        self.voice_thread = DownloadVoiceThread(lan, text)
        self.voice_thread.trigger.connect(self.playVoice)
        self.voice_thread.start()

    def copyButtonClicked(self):
        """点击复制内容按钮"""
        text = self.transl_result['trans_result']['data'][0].get('dst')
        self.clipboard.setText(text)

    def anchorClicked(self, url):
        """ 点击底部输出框中的链接
        点击输出框中音标发音按钮时，获取单词发音并播放
        点击输出框中文本链接的时候，提取文本并进行翻译
        """
        url = url.url().replace('#', '')
        if url in ['英', '美', '音']:  # 点击发音按钮
            text = self.transl_result['trans_result']['data'][0].get('src')
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
            self.startTransl()

    def playVoice(self, voice_data):
        """ 下载单词发音的线程结束
        获取单词发音并创建播放器进行播放
        """
        # 将语音写入缓冲区
        buffer = QtCore.QBuffer(self)
        buffer.setData(voice_data)
        buffer.open(QtCore.QIODevice.ReadOnly)
        # 创建播放器
        player = QtMultimedia.QMediaPlayer(self)
        player.setVolume(100)
        player.setMedia(QtMultimedia.QMediaContent(), buffer)
        sleep(0.01)  # 延时等待 setMedia 完成。
        # 播放语音
        player.play()

    def hideWidget(self):
        """隐藏部件"""
        self.textBrowser.hide()
        self.textBrowser_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()

    def modifyUI(self, mode=0):
        """布局调整"""
        size = None
        if mode == 0:
            size = QtCore.QSize(QtCore.QSize(self.width(), 0))
        elif mode == 1:
            size = QtCore.QSize(self.width(), MAX_H)
        elif mode == 2:
            h = self.widget_3.height() + self.textBrowser.height()
            size = QtCore.QSize(self.width(), MAX_H - h)
        if size is not None:
            self.hideWidget()
            self.animation.setEndValue(size)
            self.animation.finished.connect(lambda: self.animationFinished(mode))
            self.animation.start()

    def animationFinished(self, i):
        """动画完成后调整布局"""
        self.animation.disconnect()  # 断开信号连接
        if i == 1:
            self.widget_3.show()
            self.textBrowser.show()
            self.textBrowser_2.show()
            self.fade_in_thread.start()  # 开启淡入效果
        elif i == 2:
            self.widget_4.show()
            self.textBrowser_2.show()
            self.fade_in_thread.start()

    def deleteScreenshotWindow(self):
        """回收截图窗口"""
        del self.screenshot_window

    def deleteFloatWindow(self):
        """回收悬浮窗口"""
        del self.float_window


if __name__ == '__main__':
    # 高分辨率屏幕自适应
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # 创建QApplication类的实例
    app = QtWidgets.QApplication(sys.argv)
    # 汉化右键菜单
    translator = QtCore.QTranslator()
    translator.load(widgets_zh_CN_qm)
    app.installTranslator(translator)
    # 创建主窗口
    window = MainWindow()
    window.show()
    # 进入程序的主循环，并通过exit函数确保主循环安全结束
    sys.exit(app.exec_())
