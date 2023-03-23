# -*- coding: utf-8 -*-
import json
import math
import re
from threading import Lock

from spider import BaseTranslate


def n(r: int, o: str):
    for t in range(0, len(o) - 2, 3):
        a = o[t + 2]
        a = ord(a[0]) - 87 if a >= 'a' else int(a)
        a = r >> a if '+' == o[t + 1] else r << a
        r = r + a & 4294967295 if '+' == o[t] else r ^ a
    return r


def e(r: str):
    i = '320305.131321201'
    o = re.findall('[\U00010000-\U0010ffff]', r)
    if not o:
        t = len(r)
        if t > 30:
            r = r[:10] + r[math.floor(t / 2) - 5: math.floor(t / 2) + 5] + r[-10:]
    else:
        e = re.split('[\U00010000-\U0010ffff]', r)
        h, f = len(e), []
        for C in range(0, h):
            if e[C]:
                f.extend(e[C])
            if C != h - 1:
                f.append(o[C])
        g = len(f)
        if g > 30:
            r = ''.join(f[:10] + f[math.floor(g / 2) - 5: math.floor(g / 2) + 5] + f[-10:])
    d = i.split('.')
    S, v = [], 0
    while v < len(r):
        A = ord(r[v])
        if 128 > A:
            S.append(A)
        elif 2048 > A:
            S.extend([A >> 6 | 192, 63 & A | 128])
        elif 55296 == (64512 & A) and v + 1 < len(r) and 56320 == (64512 & ord(r[v + 1])):
            A = 65536 + ((1023 & A) << 10) + (1023 & ord(r[++v]))
            S.extend([A >> 18 | 240, A >> 12 & 63 | 128, A >> 6 & 63 | 128, 63 & A | 128])
        else:
            S.extend([A >> 12 | 224, A >> 6 & 63 | 128, 63 & A | 128])
        v += 1
    m, s, F, D = int(d[0]) | 0, int(d[1]) | 0, '+-a^+6', '+-3^+b+-f'
    p = m
    for b in range(0, len(S)):
        p += S[b]
        p = n(p, F)
    p = n(p, D) ^ s
    if p < 0:
        p = (2147483647 & p) + 2147483648
    p = int(p % 1e6)
    return f'{p}.{p ^ m}'


class BaiduTranslate(BaseTranslate):
    """百度翻译爬虫"""
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
            super(BaiduTranslate, self).__init__()
            # 百度翻译主页
            self.home = 'https://fanyi.baidu.com/'
            # 添加请求头
            response = self._get()
            self.headers.update({
                'cookie': '; '.join([f'{k}={v}' for k, v in response.cookies.items()]),
                'acs-token': ''  # TODO 新增请求头。服务端尚未做校验，暂时为空
            })
            # 获取Token
            response = self._get()
            self.form_data = {
                'token': re.findall(r'token:[\s\'\"]+([a-z\d]+)[\'\"]', response.content.decode())
            }
            # 标记初始化完成
            self._init_flag = True

    def _get_lan(self, query):
        """查询语言种类"""
        path = 'langdetect'
        form_data = {
            'query': query,
        }
        response = self._post(path, form_data)
        content = json.loads(response.content)
        return content.get('lan')

    def _update_form_data(self, query, to_lan, from_lan):
        """构建表单参数"""
        # with open(index_d52622f_js, 'r', encoding='UTF-8') as f:
        #     js = f.read()
        # eval_js = js2py.eval_js(js)
        # sign = eval_js(query)
        sign = e(query)
        self.form_data.update({
            'to': to_lan,
            'from': from_lan,
            'query': query,
            'sign': sign,
        })

    def translate(self, query, to_lan, from_lan=None, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        if not from_lan:
            from_lan = self._get_lan(query)  # 自动检测源语言
        if from_lan == to_lan:
            to_lan = 'en' if from_lan == 'zh' else 'zh'
        path = 'v2transapi'
        params = {'from': from_lan, 'to': to_lan}
        self._update_form_data(query, to_lan, from_lan)
        response = self._post(path, self.form_data, params=params)
        data = json.loads(response.content)
        assert data.get('errno') is None, f'翻译失败！（{data["errno"]}，{data["errmsg"]}）'
        self.data = data

    def get_translation(self, *args, **kwargs):
        """ 获取译文
        ["你好", ["你好", "zh"]]
        """
        translation_data = []
        dst = '\n'.join([data['dst'] for data in self.data['trans_result']['data']])
        translation_data.append(dst)
        translation_data.append([dst, self.data['trans_result']['to']])
        return translation_data

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
        explanation_data = []
        simple_means = self.data.get('dict_result', {}).get('simple_means')
        if simple_means:
            symbols = simple_means['symbols'][0]
            # 解析音标
            symbol_list = []
            if symbols.get('word_symbol'):
                symbol_list.append([f'音 [{symbols["word_symbol"]}]', [simple_means["word_name"], 'zh']])
            if symbols.get('ph_en'):
                symbol_list.append([f'英 [{symbols["ph_en"]}]', [simple_means["word_name"], 'uk']])
            if symbols.get('ph_am'):
                symbol_list.append([f'美 [{symbols["ph_am"]}]', [simple_means["word_name"], 'en']])
            # 解析释义
            explain_list = []
            for index, parts in enumerate(symbols['parts']):
                if isinstance(parts['means'][0], dict):
                    for index2, mean in enumerate(parts['means']):
                        part = index2 + 1
                        means = [[mean['text'], '；'.join(mean.get('means', [])), True]]
                        explain_list.append({'part': part, 'means': means})
                else:
                    part = parts.get('part') or parts.get('part_name') or index + 1
                    means = [['；'.join(parts['means']), '', False]]
                    explain_list.append({'part': part, 'means': means})
            # 解析语法
            grammar_list = []
            exchange_dict = {
                'word_third': '第三人称单数',
                'word_pl': '复数',
                'word_ing': '现在分词',
                'word_done': '过去式',
                'word_past': '过去分词',
                'word_er': '比较级',
                'word_est': '最高级',
                'word_proto': '原形',
            }
            exchange = simple_means.get('exchange', {})
            for k, v in exchange.items():
                if v:
                    grammar_list.append({'name': exchange_dict.get(k), 'value': v[0]})
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list, 'grammars': grammar_list})
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
        from_lan = self.data['trans_result']['from']
        double_list = json.loads(self.data['liju_result']['double']) if self.data['liju_result']['double'] else []
        for double in double_list:
            # 解析例句
            sentence = ''
            sentence_text = ''
            for item in double[0]:
                string = f'<b>{item[0]}</b>' if item[3] == 1 else item[0]  # 标记查询的单词
                sentence += string + (item[-1] if len(item) == 5 else '')
                sentence_text += item[0] + (item[-1] if len(item) == 5 else '')
            # 解析例句翻译
            sentence_tr = ''
            for item in double[1]:
                sentence_tr += item[0] + (item[-1] if len(item) == 5 else '')
            # 构建例句 TTS 获取参数
            sentence_speech = [sentence_text if from_lan == 'en' else sentence_tr, 'en']
            sentence_data.append([sentence, sentence_tr, sentence_speech, 0 if from_lan == 'en' else 1])
        return sentence_data

    def get_tts(self, text, lan, *args, **kwargs):
        """ 获取发音

        :param text: 源文本
        :param lan: 文本语言
        :return: 文本语音
        """
        spd = 5 if lan == 'zh' else 3
        path = 'gettts'
        params = {'lan': lan, 'text': text, 'spd': spd, 'source': 'web'}
        response = self._get(path, params)
        content = response.content
        return content

    def get_ocr(self, img, from_lan=None, *args, **kwargs):
        """ 从图片中提取文字(精度差)
        识别结果为空时，可尝试切换识别语言
        """
        path = 'getocr'
        form_data = {'from': from_lan or 'auto', 'to': 'zh'}
        files = {'image': img}
        response = self._post(path, form_data, files)
        data = json.loads(response.content)
        src = ' '.join(data.get('data', {}).get('src', []))
        return src


if __name__ == '__main__':
    bt = BaiduTranslate()
    bt.translate('hello', 'zh')
    translations = bt.get_translation()
    explanations = bt.get_explanation()
    tts = bt.get_tts(*explanations[0]['symbols'][0][1])
    sentences = bt.get_sentence()
    print(bt.data)
