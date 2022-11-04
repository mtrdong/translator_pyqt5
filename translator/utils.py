# -*- coding: utf-8 -*-
import base64
import html
import json
import random

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QWidget
from aip import AipOcr

__all__ = [
    'move_widget',
    'baidu_ocr',
    'b64encode',
    'b64decode',
    'generate_output',
]


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


def baidu_ocr(img_bytes):
    """ 利用百度文字识别API提取图片中的文本
    申请地址：https://console.bce.baidu.com/ai/?_=1630920729906#/ai/ocr/overview/index
    """
    APP_ID = ''
    API_KEY = ''
    SECRECT_KEY = ''
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
    # 通用文字识别（标准版），50000次/天免费
    message = client.basicGeneral(img_bytes, options={'detect_language': 'true'})
    # 通用文字识别（高精度版），500次/天免费
    # message = client.basicAccurate(img_bytes, options={'language_type': 'auto_detect'})
    try:
        text = '\n'.join([words.get('words') for words in message.get('words_result')])
    except:
        return ''
    return text


def b64encode(o):
    """base64编码"""
    b64ec = base64.b64encode(json.dumps(o).encode())
    return b64ec.decode()


def b64decode(s):
    """base64解码"""
    b64dc = base64.b64decode(s)
    return json.loads(b64dc.decode())


def generate_output(obj, more=False, reverse=False):
    """ 生成HTML输出内容

    :param obj: 翻译引擎对象
    :param more: 显示更多内容（默认不添加单词语法和双语例句）
    :param reverse: 有道词典--中日互译 结果切换
    :return: HTML字符串
    """
    # 输出内容1：译文
    translation_text, _ = obj.get_translation()
    translation_html = '<div style="font-size: 16px; color: #3C3C3C;">{}</div>'
    translation_contents = translation_html.format(html.escape(translation_text).replace('\n', '<br>'))

    # 输出内容2：释义
    explanations = obj.get_explanation(reverse)
    if not explanations:
        # 没有释义时直接返回译文
        return translation_contents, ''
    no_html = '<span style="color: #8C8C8C;">{}&nbsp;&nbsp;</span>'
    explanation_html = '<div style="font-size: 14px; color: #3C3C3C;">{}</div>'
    explanation_list = []
    for explanation in explanations:
        # 音标/读音
        symbol_html = '<span style="color: #8C8C8C; font-weight: bold;">' \
                      '{} <a style="text-decoration: none;" href="#{}">🔊</a>' \
                      '</span>'
        symbol_list = [symbol_html.format(symbol[0], b64encode(symbol[1])) for symbol in explanation.get('symbols', [])]
        symbol_contents = '&nbsp;&nbsp;&nbsp;'.join(symbol_list)
        if symbol_contents:
            explanation_list.append(explanation_html.format(symbol_contents))
        # 简明释义
        explain_html = '<span><i style="color: #8C8C8C;">{}</i><hr>{}</span>'
        explain_list = []
        for explain in explanation.get('explains', []):
            part = f"No.{explain['part']}" if isinstance(explain['part'], int) else explain['part']
            mean_list = []
            for index, mean in enumerate(explain['means']):
                text = mean[0]
                text_tr = mean[1]
                if mean[2]:
                    a_html = '<a style="text-decoration: none; color: #506EFF;" href="#{}">{}</a>'
                    text = a_html.format(b64encode(mean[0]), mean[0])
                if mean[1]:
                    span_html = '<br><span style="color: #8C8C8C;">{}</span>'
                    text_tr = span_html.format(mean[1])
                text_contents = text + text_tr
                if len(explain['means']) > 1:
                    text_contents = no_html.format(index + 1) + text_contents
                mean_list.append(text_contents)
            mean_contents = '<br>'.join(mean_list)
            explain_list.append(explain_html.format(part, mean_contents))
        explain_contents = '<br><br>'.join(explain_list)
        if explain_contents:
            explanation_list.append(explanation_html.format(explain_contents))
        if more:
            # 单词语法
            grammar_html = '<span>' \
                           '<span style="color: #8C8C8C;">{}</span>&nbsp;&nbsp;&nbsp;' \
                           '<a style="text-decoration: none; color: #506EFF;" href="#{}">{}</a>' \
                           '</span>'
            grammar_list = []
            for grammar in explanation.get('grammars', []):
                grammar_list.append(grammar_html.format(grammar['name'], b64encode(grammar['value']), grammar['value']))
            grammar_contents = '<br>'.join(grammar_list)
            if grammar_contents:
                explanation_list.append(explanation_html.format(grammar_contents))
    if more:
        # 双语例句
        sentence_html = '<span style="font-size: 14px;">{}</span>'
        a_html = ' <a style="text-decoration: none;" href="#{}">🔊</a>'
        sentence_list = []
        sentences = obj.get_sentence(True)
        if len(sentences) > 3:
            # 例句数量大于3条时，随机选取其中3条例句
            sentences = random.sample(sentences, 3)
        for index, sentence in enumerate(sentences):
            replace = '<b style="color: #F0374B;">'
            sentence_text = sentence[0].replace('<b>', replace)
            sentence_tr = sentence[1].replace('<b>', replace)
            if sentence_tr:
                span_html = '<br><span style="color: #8C8C8C;">{}</span>'
                sentence_tr = span_html.format(sentence_tr)
            if sentence[3] == 0:
                sentence_text += a_html.format(b64encode(sentence[2]))
            elif sentence_tr:
                sentence_tr += a_html.format(b64encode(sentence[2]))
            no = no_html.format(index + 1)
            sentence_list.append(sentence_html.format(no + sentence_text + sentence_tr))
        sentence_contents = '<br><br>'.join(sentence_list)
        if sentence_contents:
            explanation_list.append(explanation_html.format(sentence_contents))
    # 拼接HTML内容
    explanation_contents = '<hr width=0>'.join(explanation_list)

    return translation_contents, explanation_contents
