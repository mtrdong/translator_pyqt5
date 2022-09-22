# -*- coding: utf-8 -*-
from contextlib import suppress
from hashlib import md5
from threading import Lock
from urllib.parse import parse_qs

import requests


class YoudaoTranslate(object):
    """有道翻译爬虫"""
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
            self.url = 'https://dict.youdao.com/jsonapi_s?doctype=json&jsonversion=4'
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/105.0.0.0 Safari/537.36',
            }
            self.data = None

    def get_spell(self):
        """获取单词的音标/拼音"""
        spell_dict = {}
        try:
            spell_dict['英'] = {
                'spell': f'[{self.data["simple"]["word"][0]["ukphone"]}]',
                'speech': [self.data['simple']['query'], '', 1]
            }
            spell_dict['美'] = {
                'spell': f'[{self.data["simple"]["word"][0]["usphone"]}]',
                'speech': [self.data['simple']['query']]
            }
        except (KeyError, TypeError):
            with suppress(KeyError, TypeError):
                spell_dict['音'] = {
                    'spell': f'[{self.data["simple"]["word"][0]["phone"]}]',
                    'speech': [self.data['simple']['query']]
                }
        return spell_dict

    def get_voice(self, audio, le='', type_=2):
        """获取发音"""
        url = 'https://dict.youdao.com/dictvoice'
        params = {'audio': audio, 'le': le, 'type': type_}
        response = self.session.get(url, params=params, headers=self.headers)
        content = response.content
        return content

    def get_explanation(self):
        """获取释义"""
        explanation_dict = {}
        try:
            word = (self.data.get('ce') or self.data.get('ec') or
                    self.data.get('cf') or self.data.get('fc') or
                    self.data.get('ck') or self.data.get('kc') or
                    self.data.get('cj') or self.data.get('jc'))['word']
        except (AttributeError, TypeError):
            return explanation_dict

    def get_sentence(self):
        """获取例句"""
        sentence_list = []
        with suppress(KeyError, TypeError):
            sentence_pair = self.data["blng_sents_part"]["sentence-pair"]
            for item in sentence_pair:
                speech = parse_qs('audio=' + (item.get('sentence-speech') or item.get('sentence-translation-speech')))
                sentence_list.append({
                    'sentence': item.get('sentence-eng') or item.get('sentence'),
                    'translation': item.get('sentence-translation'),
                    'speech': [speech.get('audio', [''])[0], speech.get('le', [''])[0], speech.get('type', [''])[0]],
                })
        return sentence_list

    @staticmethod
    def get_form_data(text, le):
        """构建表单参数"""
        v = 'Mk6hqtUp33DGGtoS63tTJbMUYjRrG1Lu'
        _ = 'webdict'
        x = 'web'

        r = text + _
        time = len(r) % 10
        n = md5(r.encode('utf-8')).hexdigest()
        o = x + text + str(time) + v + n
        f = md5(o.encode('utf-8')).hexdigest()

        form_data = {
            'q': text,
            'le': le,
            't': time,
            'client': x,
            'sign': f,
            'keyfrom': _,
        }
        return form_data

    def translate(self, query, le):
        """翻译"""
        form_data = self.get_form_data(query, le)
        response = self.session.post(self.url, data=form_data, headers=self.headers)
        self.data = response.json()


if __name__ == '__main__':
    yt = YoudaoTranslate()
    yt.translate('你好', 'ja')
    spell = yt.get_spell()
    # voice_uk = yt.get_voice(*spell['英']['speech'])
    # voice_us = yt.get_voice(*spell['美']['speech'])
    explanation = yt.get_explanation()
    sentence = yt.get_sentence()
    print(yt.data)
