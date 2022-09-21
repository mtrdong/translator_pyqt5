# -*- coding: utf-8 -*-
import base64
import json
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

    def get_spell(self):
        """获取单词的音标/拼音"""
        spell_dict = {}
        try:
            spell_dict['音'] = {'spell': f'[{self.data[0][0]}]', 'speech': [self.data[0][4][0][0], self.data[0][2]]}
        except:
            pass
        return spell_dict

    def get_voice(self, text, lang):
        """获取发音"""
        rpcids = 'jQ1olc'
        form_data = self.get_form_data(rpcids, text, lang)
        response = self.session.post(self.url, data=form_data, headers=self.headers)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        return base64.b64decode(data[0])

    def get_sentence(self):
        """获取例句"""
        sentence_list = []
        try:
            sentence_pair = self.data[3][2][0]
            for item in sentence_pair:
                sentence_list.append({
                    'sentence': item[1],
                    'speech': [item[1], 'en'],
                })
        except:
            return sentence_list
        return sentence_list

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
    gt.translate('word', 'auto', 'zh-CN')
    spell = gt.get_spell()
    # voice = gt.get_voice(*spell['音']['speech'])
    sentence = gt.get_sentence()
    print(gt.data)
