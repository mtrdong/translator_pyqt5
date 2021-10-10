# -*- coding: utf-8 -*-
import contextlib
import json
import random
import re

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget
from aip import AipOcr

from baidu_trans_spider import BaiDuTrans

__all__ = [
    'MouseCheckThread',
    'BaiduTransThread',
    'StartTransThread',
    'DownloadVoiceThread',
    'BaiduOCRThread',
    'get_trans_result',
    'get_word_means',
    'get_spell_html',
    'get_comment_html',
    'get_exchange_html',
    'get_example_html',
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
                if not (-20 <= pos.x() <= self.widget.width() and -20 <= pos.y() <= self.widget.height()):
                    # 鼠标超出悬浮窗范围，发送信号并结束循环
                    self.trigger.emit(True)
                    break


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


def baidu_ocr(img_bytes):
    """ 利用百度文字识别API提取图片中的文本
    申请地址：https://console.bce.baidu.com/ai/?_=1630920729906#/ai/ocr/overview/index
    """
    APP_ID = ''
    API_KEY = ''
    SECRECT_KEY = ''
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
    message = client.basicGeneral(img_bytes)  # 通用文字识别（标准版），50000次/天免费
    # message = client.basicAccurate(img_bytes)  # 通用文字识别（高精度版），500次/天免费
    try:
        text = ''.join([words.get('words') for words in message.get('words_result')])
    except:
        return ''
    return text


def get_trans_result(data):
    """获取直译结果"""
    try:
        trans_result = '<br />'.join([d['dst'] for d in data['trans_result']['data']])
    except:
        trans_result = ''
    return trans_result


def get_word_means(data):
    """获取简明释义"""
    try:
        word_means = '; '.join(data['dict_result']['simple_means']['word_means'])
    except:
        word_means = ''
    return word_means


def get_spell_html(data):
    """获取单词音标"""
    spell_list = []
    spell_dict = {
        'ph_en': '英',
        'ph_am': '美',
        'word_symbol': '音',
    }
    html_template = '<span style="font-size: 14px; color: #606060;">{lang} [{spell}] <a style="text-decoration: none;" href="#{lang}">🔊</a></span>'
    try:
        spell = data['dict_result']['simple_means']['symbols'][0]
        for k, v in spell_dict.items():
            if spell.get(k):
                spell_list.append(html_template.format(lang=v, spell=spell.get(k)))
    except:
        return ''
    return '&nbsp;&nbsp;&nbsp;'.join(spell_list)


def get_comment_html(data):
    """获取单词释义"""
    try:
        parts = data["dict_result"]["simple_means"]["symbols"][0]["parts"]
    except:
        return ''
    else:
        comment_list = []
        for part in parts:
            try:
                means_list = [text['text'] for text in part['means']]
            except:
                means_list = part['means']
            comments = []
            for comment in means_list:
                if re.match(r'^[a-zA-Z.\-\'\s]+$', comment):
                    comments.append('<span><a style="text-decoration: none; color: #4395FF;" href="#{comment}">{comment}</a></span>'.format(comment=comment))
                else:
                    comments.append('<span>{comment}</span>'.format(comment=comment))
            part_str = part.get('part') if part.get('part') else part.get('part_name', '')
            if part_str:
                comment_list.append('<div>{}</div>'.format('<span style="color: #A4A4A4;">{}</span>'.format(part_str) + '&nbsp;&nbsp;&nbsp;' + '；'.join(comments)))
            else:
                comment_list.append('；'.join(comments))
        return ''.join(comment_list)


def get_exchange_html(data):
    """获取单词形态"""
    exchange_list = []
    exchange_dict = {
        'word_third': '第三人称单数',
        'word_pl': '复数',
        'word_ing': '现在分词',
        'word_done': '过去式',
        'word_past': '过去分词',
        'word_er': '比较级',
        'word_est': '最高级',
    }
    html_template = '<span><a style="text-decoration: none; color: #4395FF;" href="#{exchange}">{exchange}</a></span>'
    try:
        exchange = data['dict_result']['simple_means']['exchange']
        for k, v in exchange_dict.items():
            if exchange.get(k):
                exchange_list.append('{}：{}'.format(v, html_template.format(exchange=exchange.get(k)[0])))
    except:
        return ''
    return '&nbsp;&nbsp;&nbsp;'.join(exchange_list)


def get_example_html(data):
    """获取例句"""
    try:
        double = json.loads(data['liju_result']['double'])
    except:
        return ''
    query = data['trans_result']['data'][0]['src']
    num = random.randint(0, len(double) - 1)
    if data['trans_result']['from'] == 'en':
        from_text = ''
        for s in [s[0] for s in double[num][:2][0]]:
            if re.match(r'^[a-zA-Z]+$', s):
                from_text = from_text + s + ' '
            else:
                from_text = from_text.strip() + s + ' ' if from_text else s
        to_text = ''.join([s[0] for s in double[num][:2][1]])
    else:
        from_text = ''.join([s[0] for s in double[num][:2][0]])
        to_text = ''
        for s in [s[0] for s in double[num][:2][1]]:
            if re.match(r'^[a-zA-Z]+$', s):
                to_text = to_text + s + ' '
            else:
                to_text = to_text.strip() + s + ' ' if to_text else s
    from_text = re.sub(query, match_case(query), from_text, flags=re.IGNORECASE)
    return '<span>【例】</span><span>{}<br />{}</span>'.format(from_text, to_text)


def match_case(word):
    def inner(match):
        """
        替换字符串并设置样式
        替换字符串与原字符串大小写保持一致
        """
        html_template = '<span style="color: #FF9E45">{}</span>'
        text = match.group()
        if text.isupper():
            return html_template.format(word.upper())
        elif text.islower():
            return html_template.format(word.lower())
        elif text[0].isupper():
            return html_template.format(word.capitalize())
        else:
            return html_template.format(word)
    return inner
