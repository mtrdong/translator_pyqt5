# -*- coding: utf-8 -*-
import json
import uuid
from threading import Lock

from spider import BaseTranslate


class SougouTranslate(BaseTranslate):
    """搜狗翻译爬虫"""
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
            super(SougouTranslate, self).__init__()
            # 搜狗翻译主页
            self.home = 'https://fanyi.sogou.com/'
            # 添加请求头
            response = self._get()
            self.headers.update(cookie='; '.join([f'{k}={v}' for k, v in response.cookies.items()]))
            # 标记初始化完成
            self._init_flag = True

    def translate(self, query, to_lan, from_lan=None, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        pass

    def get_translation(self, *args, **kwargs):
        """ 获取译文
        ["你好", ["你好", "zh"]]
        """
        pass

    def get_explanation(self, *args, **kwargs):
        """ 获取释义
        [{
            "symbols": [
                ["英[həˈləʊ]", ["hello", "uk"]],
                ["美[heˈloʊ]", ["hello", "en"]]
            ],
            "explains": [
                {
                    "part": "int./n",
                    "means": [
                        ["你好；(用于问候、接电话或引起注意)喂；(表示惊讶或认为别人说了蠢话或没有注意听)嘿", "", False]
                    ]
                }
            ],
            "grammars": [
                {
                    "name": "复数",
                    "value": "hellos"
                }
            ]
        }]
        """
        pass

    def get_sentence(self, *args, **kwargs):
        """ 获取例句
        [
            [
                "‘ Oh, hello, ’ he said, with a smile.",
                "“嗨，你好。”他微笑着说。",
                ["‘ Oh, hello, ’ he said, with a smile.", "en"],
                0
            ],
            [
                "Hello, Mr Brown.",
                "你好，布朗先生。",
                ["Hello, Mr Brown.", "en"],
                0
            ]
        ]
        """
        pass

    def get_tts(self, text, lan, *args, **kwargs):
        """ 获取发音

        :param text: 源文本
        :param lan: 文本语言
        :return: 文本语音
        """
        pass

    def get_ocr(self, img, from_lan=None, *args, **kwargs):
        """ 从图片中提取文字
        识别结果为空时，可尝试切换识别语言
        """
        # 更新Cookie
        path = 'picture'
        response = self._get(path)
        fqv = response.cookies.get('FQV')
        self.headers.update(cookie=self.headers['cookie'] + f'; {fqv}')
        # 上传图片
        path = 'api/transpc/picture/upload'
        form_data = {
            'fuuid': uuid.uuid4().__str__(),
            'extraData': json.dumps({'from': from_lan or 'auto', 'to': 'zh-CHS', 'imageName': 'image.png'})
        }
        files = {'fileData': img}
        response = self._post(path, form_data, files)
        data = response.json().get('data') or {}
        result = data.get('result', [])
        src = '\n'.join([item['content'] for item in result])
        return src


if __name__ == '__main__':
    st = SougouTranslate()
    st.translate('hello', 'zh')
