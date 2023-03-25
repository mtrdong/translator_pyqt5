# -*- coding: utf-8 -*-
import base64
import json
import re
import time
import uuid
from contextlib import suppress
from hashlib import md5
from threading import Lock

from spider import BaseTranslate
from utils import aes_encrypt


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
            # 获取secretCode，同时请求一下首页以更新客户端的cookies
            # 发送翻译请求时，需使用此code构建请求表单中的s参数值
            response = self._get()
            self.secret_code = self._get_secret_code(response.text)
            # 标记初始化完成
            self._init_flag = True

    @staticmethod
    def _get_secret_code(text: str):
        """从HTML页面中提取secretCode"""
        secret_code = re.findall(r'[\'"]secretCode[\'":\s]{2,}(\d+),', text)[0]
        return secret_code

    def _get_form_data(self, query, from_lan, to_lan):
        """构建表单数据"""
        form_data = {
            'from': from_lan,
            'to': to_lan,
            'text': query,
            'client': 'pc',
            'fr': 'browser_pc',
            'needQc': 1,
            's': md5((from_lan + to_lan + query + self.secret_code).encode('utf-8')).hexdigest(),
            'uuid': uuid.uuid4().__str__(),
            'exchange': False
        }
        return form_data

    def translate(self, query, to_lan, from_lan=None, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        from_lan = from_lan or 'auto'
        if from_lan == to_lan:
            to_lan = 'en' if from_lan == 'zh-CHS' else 'zh-CHS'
        path = 'api/transpc/text/result'
        form_data = self._get_form_data(query, from_lan, to_lan)
        response = self._post(path, json=form_data)
        data = response.json()
        assert data.get('status') == 0, f'翻译失败！（{data["status"]}，{data["info"]}）'
        self.data = data['data']

    def get_translation(self, *args, **kwargs):
        """ 获取译文
        ["你好", ["你好", "zh-CHS"]]
        """
        translation_data = []
        translate = self.data.get('translate')
        if translate['errorCode'] == '0':
            translation_data.append(translate['dit'])
            translation_data.append([translate['dit'], translate['to']])
        return translation_data

    def get_explanation(self, *args, **kwargs):
        """ 获取释义
        [{
            "symbols": [
                ["英 [həˈləʊ]", ["hello", "uk"]],
                ["美 [heˈloʊ]", ["hello", "en"]]
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
        explanation_data = []
        # 解析音标
        symbol_list = []
        translate = self.data['translate']
        phonetic = self.data['voice']['phonetic']
        for item in phonetic:
            voice_type = item.get('type')
            if voice_type:
                voice_url = 'https:' + item.get('filename')
                if voice_type == 'uk':
                    symbol_list.append([f'英 [{item["text"]}]', [translate['orig_text'], translate['from'], voice_url]])
                else:
                    symbol_list.append([f'美 [{item["text"]}]', [translate['orig_text'], translate['from'], voice_url]])
            else:
                symbol_list.append([f'音 [{item["text"]}]', [translate['orig_text'], translate['from']]])
                break
        return explanation_data

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
        sentence_data = []
        with suppress(KeyError, TypeError):
            bilingual = self.data['detail']['bilingual']
            to_lan = self.data['translate']['to']
            from_lan = self.data['translate']['from']
            for item in bilingual:
                sentence_text = item['source'].replace('<em>', '<b>').replace('</em>', '</b>')  # 例句原文
                sentence_tr = item['target']  # 例句译文
                # 构建例句 TTS 获取参数
                text, lan, idx = (sentence_text, from_lan, 0) if self.data.get('dictType') else (sentence_tr, to_lan, 1)
                sentence_speech = [text, lan]
                # 添加例句
                sentence_data.append([sentence_text, sentence_tr, sentence_speech, idx])
        return sentence_data

    def get_tts(self, text, lan, url='', *args, **kwargs):
        """ 获取发音

        :param text: 源文本
        :param lan: 文本语言
        :param url: 单词发音直链
        :return: 文本语音
        """
        if url:
            response = self.session.get(url)
        else:
            params = {
                'S-AppId': 102356845,
                'S-Param': aes_encrypt(
                    json.dumps({
                        'curTime': int(time.time() * 1000),
                        'text': text,
                        'spokenDialect': lan,
                        'rate': '0.8'
                    }),
                    '76350b1840ff9832eb6244ac6d444366',
                    iv=base64.b64decode('AAAAAAAAAAAAAAAAAAAAAA==').decode()
                )
            }
            path = 'openapi/external/getWebTTS'
            response = self._get(path, params)
        content = response.content
        return content

    def get_ocr(self, img, from_lan=None, *args, **kwargs):
        """ 从图片中提取文字
        识别结果为空时，可尝试切换识别语言
        """
        # 请求一下图片翻译页面以更新客户端的cookies
        self._get('picture')
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
    st.translate('你好', 'en')
    translations = st.get_translation()
    explanations = st.get_explanation()
    sentences = st.get_sentence()
    tts = st.get_tts('hello', 'en')
