# -*- coding: utf-8 -*-
import base64
import json
from contextlib import suppress
from threading import Lock

import requests


class GoogleTranslate(object):
    """谷歌翻译爬虫"""
    _lock = Lock()
    _instance = None
    _init_flag = False

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._init_flag:  # 只初始化一次
            self._init_flag = True
            self.session = requests.Session()
            self.url = 'https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute'
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/105.0.0.0 Safari/537.36',
            }
            self.data = None

    def get_translation(self):
        """获取译文"""
        translation_data = []
        with suppress(IndexError, TypeError):
            text = self.data[1][0][0][5][0][0]
            translation_data.append(text)
            translation_data.append([text, self.data[1][1]])
        return translation_data

    def get_spell(self):
        """获取音标/拼音"""
        spell_data = []
        with suppress(IndexError, TypeError):
            spell_data.append([self.data[0][0], [self.data[0][4][0][0], self.data[0][2]]])
        return spell_data

    def get_voice(self, text, lang):
        """获取发音"""
        rpcids = 'jQ1olc'
        form_data = self.get_form_data(rpcids, text, lang)
        response = self.session.post(self.url, data=form_data, headers=self.headers)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        return base64.b64decode(data[0])

    def get_explanation(self):
        """获取释义"""
        explanation_data = []
        with suppress(IndexError, TypeError):
            # 解析读音和释义
            spell_data, trs_data = [], []
            spell_data.append([self.data[0][0], [self.data[0][4][0][0], self.data[0][2]]])
            for i in self.data[3][5][0]:
                trs_data.append([i[0], [[n[0], '；'.join(n[2])] for n in i[1]]])
            # 添加数据
            explanation_data.append([spell_data, explanation_data])
        return explanation_data

    def get_sentence(self):
        """获取例句"""
        sentence_data = []
        with suppress(IndexError, TypeError):
            sentence_pair = self.data[3][2][0]
            for item in sentence_pair:
                sentence_data.append([item[1], [item[1], 'en'], ''])
        return sentence_data

    @staticmethod
    def get_form_data(rpcids, query, from_str, to_str=None):
        """构建表单参数"""
        s = f'[["{query}","{from_str}","{to_str}",true],[null]]' if to_str else f'["{query}","{from_str}",null,null]'
        form_data = {'f.req': json.dumps([[[rpcids, s, None, "generic"]]])}
        return form_data

    def translate(self, query, from_str, to_str):
        """翻译"""
        rpcids = 'MkEWBc'
        form_data = self.get_form_data(rpcids, query, from_str, to_str)
        response = self.session.post(self.url, data=form_data, headers=self.headers)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        self.data = data


if __name__ == '__main__':
    gt = GoogleTranslate()
    gt.translate('good', 'auto', 'zh-CN')
    translation = gt.get_translation()
    explanation = gt.get_explanation()
    a = explanation[0][0][0][1]
    # voice = gt.get_voice(*explanation[0][0][0][1])
    sentence = gt.get_sentence()
    print(gt.data)
