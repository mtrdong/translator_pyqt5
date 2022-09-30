# -*- coding: utf-8 -*-
import os.path
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
    '自动检测语言': '',
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
    '有道词典': 'youdao',
    '谷歌翻译': 'google',
}

# 窗口最大高度
MAX_H = 682


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
        self.comboBox_2DisableIndex = 0  # 源语言下拉列表禁用的的索引
        self.comboBox_3DisableIndex = 0  # 目标语言下拉列表禁用的的索引
        self.comboBox_2.currentIndexChanged.connect(self.comboBox_2CurrentIndexChanged)
        self.comboBox_3.currentIndexChanged.connect(self.comboBox_3CurrentIndexChanged)
        self.setLangItems()  # 设置源语言/目标语言下拉选项
        # 通过线程创建翻译引擎对象
        self.transl_engine = None  # 翻译引擎对象
        self.transl_result = None  # 翻译结果
        self.getTranslEngine()  # 创建翻译引擎对象
        # 监听剪切板。开启监听时，当剪切板内容发生变化时，自动获取剪切板文本发起翻译（伪划词翻译）
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clipboardChanged)
        self.clipboard_flag = False  # 监听标志（True-开启监听；False-关闭监听）
        # 翻译定时器。输入框内容发生变化时，延时一定时间后自动发起翻译
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.startTransl)
        # 文本输入框当前内容。记录当前翻译内容，防止连续输入相同内容时，再次触发自动翻译（不影响主动翻译）
        self.textEditCurrentContent = ''
        # 全局截屏翻译快捷键
        self.screen_trans_hot_key = SystemHotkey()
        self.screen_trans_hot_key.register(['f1'], callback=lambda x: self.pushButton_4.click())
        # 翻译状态（True-正在翻译；False-翻译结束）。当有正在进行的翻译时，不允许发起二次翻译
        self.transl_started = False

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

            def completed(img_data):
                """截屏完成，显示主窗口并启动识别翻译"""
                self.activateWindow()  # 主窗口变为活动窗口
                self.showNormal()  # 显示主窗口
                QtWidgets.QApplication.processEvents()  # 刷新界面
                if img_data:
                    self.textEdit.blockSignals(True)
                    self.textEdit.setText('<i>正在识别翻译，请稍候...</i>')
                    self.textEdit.blockSignals(False)
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
        if engine.get(self.comboBox.currentText()) != 'youdao':
            if self.source_lang and self.source_lang != 'auto':
                combobox_2_index = self.comboBox_2.currentIndex()
                combobox_3_index = self.comboBox_3.currentIndex()
                # 保持源语言信号连接，暂停目标语言信号连接，防止自动触发两次翻译
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
        self.timer.stop()  # 每当文本框内容发生变化时停止定时翻译，防止连续输入触发多次定时翻译
        text = self.textEdit.toPlainText().strip()
        if text:  # 有内容输入
            if text.find('file:///') == 0:  # 输入文件时，如果输入的是图片则进行识别翻译（多张图片只取一张），否则弹窗提示
                self.textEdit.blockSignals(True)  # 关闭信号连接
                self.textEdit.setText('<i>正在识别翻译，请稍候...</i>')
                self.textEdit.blockSignals(False)  # 恢复信号连接
                QtWidgets.QApplication.processEvents()  # 刷新界面
                file_list = text.split('\n')
                for file in file_list:
                    file_name = file.split('file:///')[-1]
                    if os.path.splitext(file_name)[-1] in ['.jpg', '.png']:
                        break
                else:
                    QtWidgets.QMessageBox.information(self, '提示', '仅支持 jpg 或 png 格式的图片')
                    self.textEdit.clear()
                    return None
                with open(file_name, 'rb') as f:
                    img_data = f.read()
                self.ocr(img_data)  # 识别图片中的文本并发起翻译
            elif text != self.textEditCurrentContent:  # 检查输入文本是否和上一次翻译的文本相同，如果相同则跳过，否则启动但是翻译
                self.timer.start(1000)  # 启动定时翻译
            self.textEditCurrentContent = text  # 记录当前输入内容
        else:  # 输入内容为空或空白字符时收起输出文本框
            self.textBrowser.clear()  # 清空输出框内容
            self.textBrowser_2.clear()
            self.modifyUI()  # 收起输出文本框
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
            mime_data = self.clipboard.mimeData()

            if 'text/plain' in mime_data.formats():

                if not hasattr(self, 'float_window'):

                    def clicked(s):
                        """从悬浮窗口转到主窗口"""
                        self.float_window.deleteLater()
                        self.activateWindow()
                        self.showNormal()
                        self.textEdit.setText(s)
                        QtWidgets.QApplication.processEvents()

                    def destroyed():
                        """回收悬浮窗口"""
                        del self.float_window

                    # 显示悬浮窗
                    self.float_window = FloatWindow(mime_data.text())  # 创建悬浮窗
                    self.float_window.pushButtonClicked.connect(clicked)
                    self.float_window.radioButtonClicked.connect(self.checkBox.click)
                    self.float_window.destroyed.connect(destroyed)
                    self.float_window.show()
                else:
                    self.float_window.setQuery(mime_data.text())

                def trigger(data):
                    """翻译结果输出到悬浮窗口"""
                    self.start_trans_thread.deleteLater()
                    self.transl_started = False  # 标记本次翻译结束
                    if hasattr(self, 'float_window'):
                        self.float_window.outResult(data)  # 将结果输出到悬浮窗

                # 通过线程发起翻译
                self.start_trans_thread = StartTransThread(mime_data.text(), self.target_lang)
                self.start_trans_thread.trigger.connect(trigger)
                self.start_trans_thread.start()
                # 标记正在翻译
                self.transl_started = True

    def getTranslEngine(self):
        """通过线程创建翻译引擎对象"""
        def trigger(obj):
            """设置翻译引擎"""
            self.transl_thread.deleteLater()
            if obj is None:
                msg = QtWidgets.QMessageBox.information(
                    self,
                    '程序初始化失败',
                    '网络似乎不可用，请检查网络后重试！',
                    QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Close,
                    QtWidgets.QMessageBox.Retry
                )
                if msg == QtWidgets.QMessageBox.Retry:
                    self.getTranslEngine()
                else:
                    self.close()
            self.transl_engine = obj

        self.transl_thread = TranslThread(engine.get(self.comboBox.currentText()))
        self.transl_thread.trigger.connect(trigger)
        self.transl_thread.start()

    def setLangItems(self):
        """设置源语言和目标语言下拉列表"""
        engine_val = engine.get(self.comboBox.currentText())
        if engine_val == 'youdao':
            youdao_keys = list(lang_youdao.keys())
            source_lang_items = [youdao_keys.pop(0)]
            target_lang_items = youdao_keys
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
        if engine_val == 'youdao':
            # TODO 切换有道翻译中日互译时的输出结果
            if self.comboBox_2.currentIndex() == 0:  # 输出“中译日”结果
                pass
            else:  # 输出“日译中”结果
                pass
        else:
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
        if engine_val == 'youdao':
            # 有道词典切换目标语言为“中日”时，由于翻译结果会有“中译日”和“日译中”两种
            # 因此源语言选项修改为 ['中文 >> 日语', '日语 >> 中文']，用于切换输出结果
            # TODO 此处还需根据翻译结果判断是否需要修改源语言下拉选项
            items = ['中文 >> 日语', '日语 >> 中文'] if self.target_lang == 'ja' else [list(lang_youdao.keys())[0]]
            self.comboBox_2.blockSignals(True)
            self.comboBox_2.clear()
            self.comboBox_2.addItems(items)
            self.comboBox_2.setCurrentIndex(0)
            self.comboBox_2.blockSignals(False)
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

    def startTransl(self):
        """启动翻译并输出翻译结果"""
        self.timer.stop()  # 主动发起翻译时，关闭自动翻译定时器
        if engine.get(self.comboBox.currentText()) != 'baidu':  # TODO 暂时仅支持百度翻译
            QtWidgets.QMessageBox.information(self, '提示', '目前仅支持百度翻译！')
            return None
        if self.transl_started:  # 上一次翻译上尚未结束
            return None
        if self.transl_engine is None:  # 翻译引擎为空
            QtWidgets.QMessageBox.information(self, '提示', '程序正在初始化中，请稍候重试！')
            return None
        query = self.textEdit.toPlainText().strip()
        if not query:  # 没有翻译内容
            QtWidgets.QMessageBox.information(self, '提示', '请输入翻译内容')
            return None

        def trigger(data):
            """输出翻译结果"""
            self.transl_started = False  # 标记本次翻译结束
            if not self.textEdit.toPlainText().strip():  # 没有翻译内容
                return None
            if not data:  # 没有翻译结果
                QtWidgets.QMessageBox.information(self, '提示', '翻译结果为空，请重试！')
                return None
            self.transl_result = data  # 翻译结果
            trans_result = get_trans_result(data)  # 直译
            spell_html = get_spell_html(data)  # 音标
            comment_html = get_comment_html(data)  # 释义
            exchange_html = get_exchange_html(data)  # 形态
            example_html = get_example_html(data)  # 例句
            if spell_html or comment_html:
                trans_result_html = '<div style="font-size: 16px; color: #3C3C3C;"><h4>{}</h4></div>'.format(
                    trans_result)
                explanation_html = '<div style="font-size: 16px; color: #3C3C3C;"><p>{}</p><p>{}</p><p>{}</p><p>{}</p></div>'.format(
                    spell_html, comment_html, exchange_html, example_html)
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
            # 自动纠正目标语言选项
            to_str = data['trans_result']['to']
            if self.target_lang != to_str:
                self.target_lang = to_str
                index = list(eval(f'lang_{engine.get(self.comboBox.currentText())}.values()')).index(to_str) - 1
                self.comboBox_3.blockSignals(True)  # 关闭信号连接
                self.comboBox_3.setCurrentIndex(index)
                self.comboBox_3.blockSignals(False)  # 恢复信号连接
                self.refreshDisableIndex()

        # 通过线程发起翻译
        kwargs = {'query': query, 'to_lang': self.target_lang}
        if engine.get(self.comboBox.currentText()) != 'youdao':
            kwargs['from_lang'] = self.source_lang
        self.start_trans_thread = StartTransThread(self.transl_engine, **kwargs)
        self.start_trans_thread.trigger.connect(trigger)
        self.start_trans_thread.start()
        self.transl_started = True  # 标记本次翻译正在进行

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
        """播放语音"""
        # 将语音写入缓冲区
        buffer = QtCore.QBuffer(self)
        buffer.setData(voice_data)
        buffer.open(QtCore.QIODevice.ReadOnly)
        # 创建播放器
        player = QtMultimedia.QMediaPlayer(self)
        player.setVolume(100)
        player.setMedia(QtMultimedia.QMediaContent(), buffer)
        sleep(0.1)  # 延时等待 setMedia 完成。
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

        def finished():
            """调整输出框"""
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
            self.hideWidget()
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
        num = 30

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

    def ocr(self, img_data):
        """ 文字识别
        识别图片中的文本并发起翻译
        """
        def trigger(text):
            """将识别到的文本设置到输入框进行翻译。如果没有识别到文本则弹窗提示"""
            self.ocr_thread.deleteLater()
            if text:
                self.textEdit.setText(text)
            else:
                QtWidgets.QMessageBox.information(self, '提示', '没有从图片中识别到文字！')
                self.textEdit.clear()

        # 通过线程进行图像文字识别
        self.ocr_thread = BaiduOCRThread(img_data)
        self.ocr_thread.trigger.connect(trigger)
        self.ocr_thread.start()


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
