# -*- coding: utf-8 -*-
import json
import math
import re
from threading import Lock

import requests
from retrying import retry


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


class BaiduTranslate(object):
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
            self._init_flag = True
            self.session = requests.Session()
            self.url = 'https://fanyi.baidu.com'
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/106.0.0.0 Safari/537.36',
                'acs-token': ''  # TODO 新增请求头。服务端尚未做校验，暂时为空
            }
            response = self.session.get(self.url, headers=self.headers)
            self.headers['cookie'] = response.headers.get('Set-Cookie')
            response = self.session.get(url=self.url, headers=self.headers)
            self.form_data = {
                'token': re.findall(r'token:[\s\'\"]+([a-z\d]+)[\'\"]', response.content.decode())
            }
            self.data = None

    @retry(stop_max_attempt_number=3)
    def _post(self, path='', form_data=None, files=None):
        """发送请求"""
        return self.session.post(url=self.url + path, headers=self.headers, data=form_data, files=files, timeout=5)

    @retry(stop_max_attempt_number=3)
    def _get(self, path=''):
        """发送请求"""
        return self.session.post(url=self.url + path, headers=self.headers, timeout=5)

    def _get_lan(self, query):
        """查询语言种类"""
        path = '/langdetect'
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

    def translate(self, query, to_lan, from_lan=None):
        """ 启动翻译
        翻译成功后返回百度翻译的源数据
        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        """
        if not from_lan:
            from_lan = self._get_lan(query)  # 自动检测源语言
        if from_lan == to_lan:
            to_lan = 'en' if from_lan == 'zh' else 'zh'
        path = f'/v2transapi?from={from_lan}&to={to_lan}'
        self._update_form_data(query, to_lan, from_lan)
        response = self._post(path, self.form_data)
        assert response.status_code == 200, f'翻译失败({response.status_code})！'
        self.data = json.loads(response.content)

    def get_translation(self):
        """获取译文"""
        translation_data = []
        dst = '\n'.join([data['dst'] for data in self.data['trans_result']['data']])
        translation_data.append(dst)
        translation_data.append([dst, self.data['trans_result']['to']])
        return translation_data

    def get_explanation(self):
        """ 获取释义
        [{
            "symbols": [
                ["英[həˈləʊ]", ["hello", "", 1]],
                ["美[heˈloʊ]", ["hello", "", 2]]
            ],
            "explains": [
                {
                    "part": "int.",
                    "means": [
                        ["喂，你好（用于问候或打招呼）；喂，你好（打电话时的招呼语）；喂，你好（引起别人注意的招呼语）；<非正式>喂，嘿 (认为别人说了蠢话或分心)；<英，旧>嘿（表示惊讶）", ""]
                    ]
                },
                {
                    "part": "n.",
                    "means": [
                        ["招呼，问候；（Hello）（法、印、美、俄）埃洛（人名）", ""]
                    ]
                }
            ],
            "grammars": [
                {
                    "name": "复数",
                    "value": "hellos"
                },
                {
                    "name": "过去式",
                    "value": "helloed"
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
                part = parts.get('part') or parts.get('part_name') or index + 1
                means = []
                if isinstance(parts['means'][0], dict):
                    for mean in parts['means']:
                        means.append(['；'.join(mean['means']), mean['text']])
                else:
                    means.append(['；'.join(parts['means']), ''])
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
            }
            exchange = simple_means.get('exchange', {})
            for k, v in exchange.items():
                grammar_list.append({'name': exchange_dict.get(k), 'value': v[0]})
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list, 'grammars': grammar_list})
        return explanation_data

    def get_sentence(self):
        """获取例句"""
        sentence_data = []
        from_lan = self.data['trans_result']['from']
        double_list = json.loads(self.data['liju_result']['double'])
        for double in double_list:
            # 解析例句
            sentence = ''
            for item in double[0]:
                string = f'<b>{item[0]}</b>' if item[3] == 1 else item[0]  # 标记查询的单词
                sentence += string if item[-1] == 0 else string + ' '
            # 解析例句翻译
            sentence_transl = ''
            for item in double[1]:
                sentence_transl += item[0] if item[-1] == 0 else item[0] + ' '
            # 构建例句 TTS 获取参数
            sentence_speech = [sentence if from_lan == 'en' else sentence_transl, 'en']
            sentence_data.append([sentence, sentence_transl, sentence_speech])
        return sentence_data

    def get_tts(self, text: str, lan: str):
        """获取单词发音"""
        spd = 5 if lan == 'zh' else 3
        path = f'/gettts?lan={lan}&text={text}&spd={spd}&source=web'
        content = self._get(path).content
        return content

    def get_ocr(self, img: bytes):
        """从图片中提取文字(精度差)"""
        path = '/getocr'
        form_data = {'from': 'auto', 'to': 'zh'}
        files = {'image': img}
        response = self._post(path, form_data, files)
        data = json.loads(response.content)
        src = '\n'.join(data['data'].get('src'))
        return src


if __name__ == '__main__':
    bt = BaiduTranslate()
    bt.translate('result', 'zh')
    translations = bt.get_translation()
    explanations = bt.get_explanation()
    # tts = bt.get_tts(*explanations[0]['symbols'][0][1])
    sentences = bt.get_sentence()
    print(bt.data)
