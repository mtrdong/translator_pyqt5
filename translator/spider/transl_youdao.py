# -*- coding: utf-8 -*-
from hashlib import md5
from threading import Lock

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
        if not self._init_flag:
            self._init_flag = True
            self.session = requests.Session()
            self.url = 'https://dict.youdao.com/jsonapi_s?doctype=json&jsonversion=4'
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/105.0.0.0 Safari/537.36',
            }
            self.data = None

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

    def get_sentence(self):
        """获取例句"""
        sentence_list = []
        try:
            sentence_pair = self.data["blng_sents_part"]["sentence-pair"]
            for item in sentence_pair:
                sentence_list.append({
                    'sentence': item.get('sentence-eng') or item.get('sentence'),
                    'translation': item.get('sentence-translation'),
                    'speech': 'audio=' + (item.get('sentence-speech') or item.get('sentence-translation-speech')),
                })
        except KeyError:
            return sentence_list
        return sentence_list

    def get_voice(self, params):
        """获取发音"""
        url = 'https://dict.youdao.com/dictvoice'
        response = self.session.get(url, params=params, headers=self.headers)
        content = response.content
        return content

    def translate(self, query, le):
        """翻译"""
        form_data = self.get_form_data(query, le)
        response = self.session.post(self.url, data=form_data, headers=self.headers)
        self.data = response.json()


if __name__ == '__main__':
    yt = YoudaoTranslate()
    yt.translate('你好', 'en')
    sentence = yt.get_sentence()
