from time import sleep

from PyQt5.QtCore import QIODevice, QBuffer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QApplication

from ui.FloatWindow_ui import Ui_FloatWindow
from threads import DownloadVoiceThread
from utils import get_trans_result, get_word_means, get_spell_html
from widgets import FloatWidget


class FloatWindow(FloatWidget, Ui_FloatWindow):
    """悬浮窗口"""
    radioButtonClicked = pyqtSignal(bool)
    pushButtonClicked = pyqtSignal(str)

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
        self.setQuery(self.query)

    def setQuery(self, s):
        self.query = s
        self.textBrowser.setText("<strong>{}</strong>".format(s))
        self.textBrowser_2.setText("<i style='color: #606060;'>正在翻译...</i>")
        self.textBrowser_2.show()
        self.textBrowser_3.clear()

    def outResult(self, data):
        """输出翻译结果"""
        trans_result = get_trans_result(data)  # 直译
        word_means = get_word_means(data)  # 释义
        spell_html = get_spell_html(data)  # 音标
        if not (trans_result or word_means):
            self.textBrowser_3.setText('<div style="color: #FF3C3C;">翻译结果为空，请重试</div>')
            self.textBrowser_2.hide()
        elif spell_html:
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
        sleep(0.01)  # 延时等待 setMedia 完成。
        # 播放语音
        player.play()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = FloatWindow('测试')
    window.show()
    sys.exit(app.exec_())
