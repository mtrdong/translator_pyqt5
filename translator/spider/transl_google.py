# -*- coding: utf-8 -*-
import base64
import json
from contextlib import suppress
from threading import Lock

from retrying import retry

from spider import BaseTranslate


class GoogleTranslate(BaseTranslate):
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
        super(GoogleTranslate, self).__init__()
        if not self._init_flag:  # 只初始化一次
            # 谷歌翻译主页
            self.home = 'https://translate.google.cn/'
            # 发送请求检查服务是否可用
            self._get()
            # 标记初始化完成
            self._init_flag = True

    @retry(stop_max_attempt_number=3)
    def _post(self, path='', form_data=None, params=None):
        """发送请求"""
        return self.session.post(self.home + path, data=form_data, params=params, headers=self.headers)

    @retry(stop_max_attempt_number=3)
    def _get(self, path='', params=None):
        """发送请求"""
        return self.session.get(self.home + path, params=params, headers=self.headers)

    @staticmethod
    def _get_form_data(rpcids, query, from_lan, to_lan=None):
        """构建表单参数"""
        list_ = [query, from_lan, to_lan, bool(to_lan) or None]
        if to_lan:
            list_ = [list_, [None]]
        form_data = {'f.req': json.dumps([[[rpcids, json.dumps(list_), None, "generic"]]])}
        return form_data

    def translate(self, query, from_lan, to_lan, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        rpcids = 'MkEWBc'
        form_data = self._get_form_data(rpcids, query, from_lan, to_lan)
        path = '_/TranslateWebserverUi/data/batchexecute'
        response = self._post(path, form_data)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        self.data = data

    def get_translation(self, *args, **kwargs):
        """ 获取译文
        ["你好", ["你好", "zh"]]
        """
        translation_data = []
        with suppress(IndexError, TypeError):
            text = self.data[1][0][0][5][0][0]
            translation_data.append(text)
            translation_data.append([text, self.data[1][1]])
        return translation_data

    def get_explanation(self, *args, **kwargs):
        """ 获取释义
        [{
            "symbols": [
                ["音 [ɡo͝od]", ["good", "en"]]
            ],
            "explains": [
                {
                    "part": "形容词",
                    "means": [
                        ["好", "good", False],
                        ["良好", "good, well, favorable, fine, favourable", True]
                    ]
                },
                {
                    "part": "名词",
                    "means": [
                        ["益处", "benefit, good, profit", False],
                        ["甜头", "good, sweet taste, pleasant flavor", True]
                    ]
                }
            ]
        }]
        """
        explanation_data = []
        with suppress(IndexError, TypeError):
            # 解析音标和释义
            symbol_list, explain_list = [], []
            symbol_list.append([f'音 [{self.data[0][0]}]', [self.data[0][4][0][0], self.data[0][2]]])
            for i in self.data[3][5][0]:
                explain_list.append({'part': i[0], 'means': [[n[0], '；'.join(n[2]), True] for n in i[1]]})
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list})
        return explanation_data

    def get_sentence(self, *args, **kwargs):
        """ 获取例句
        [
            [
                "hello there, Katie!",
                "",
                ["hello there, Katie!", "en"],
                0
            ]
        ]
        """
        sentence_data = []
        with suppress(IndexError, TypeError):
            sentence_pair = self.data[3][2][0]
            for item in sentence_pair:
                sentence_data.append([item[1], '', [item[1], 'en'], 0])
        return sentence_data

    def get_tts(self, text, lan, *args, **kwargs):
        """获取发音"""
        rpcids = 'jQ1olc'
        form_data = self._get_form_data(rpcids, text, lan)
        path = '_/TranslateWebserverUi/data/batchexecute'
        response = self._post(path, form_data)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        return base64.b64decode(data[0])


if __name__ == '__main__':
    gt = GoogleTranslate()
    gt.translate('hello', 'auto', 'zh-CN')
    translations = gt.get_translation()
    explanations = gt.get_explanation()
    tts = gt.get_tts(*explanations[0]['symbols'][0][1])
    sentences = gt.get_sentence()
    print(gt.data)
