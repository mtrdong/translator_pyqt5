# -*- coding: utf-8 -*-
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
                              'Chrome/106.0.0.0 Safari/537.36',
            }
            self.data = None
            # 中日互译时如果有两种结果，则该标志为 True
            self.reverse_flag = False

    @staticmethod
    def _get_form_data(text, le):
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

    def translate(self, query, to_lan):
        """翻译"""
        form_data = self._get_form_data(query, to_lan)
        response = self.session.post(self.url, data=form_data, headers=self.headers)
        assert response.status_code == 200, f'翻译失败({response.status_code})！'
        self.data = response.json()
        if to_lan == 'ja':  # 【中日】互译时检查是否有两种结果
            newjc = self.data.get('newjc', {}).get('word')
            cj = self.data.get('cj', {}).get('word')
            self.reverse_flag = True if newjc and cj else False

    def get_explanation(self, reverse=False):
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
        if self.data.get('fanyi'):
            explanation_data.append({'explains': [{'part': 1, 'means': [[self.data['fanyi']['tran'], '']]}]})
        # 【中英】翻译结果解析
        elif self.data.get('le') == 'en':
            word = (self.data.get('ce') or self.data.get('ec'))['word']
            # 解析音标
            symbol_list = []
            if word.get('phone'):
                symbol_list.append([f'音 [{word["phone"]}]', [word['return-phrase']]])
            if word.get("ukphone"):
                symbol_list.append([f'英 [{word["ukphone"]}]', [word['return-phrase'], '', 1]])
            if word.get("usphone"):
                symbol_list.append([f'美 [{word["usphone"]}]', [word['return-phrase']]])
            # 解析释义
            explain_list = []
            for index, trs in enumerate(word['trs']):
                explain_list.append({
                    'part': trs.get('pos') or index + 1,
                    'means': [[trs.get('tran') or trs.get('#text'), trs.get('#tran', '')]]
                })
            # 解析语法
            grammar_list = [item['wf'] for item in word.get('wfs', [])]
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list, 'grammars': grammar_list})
        # 【中法】翻译结果解析
        elif self.data.get('le') == 'fr':
            word = (self.data.get('cf') or self.data.get('fc'))['word'][0]
            # 解析音标和释义
            symbol_list, explain_list = [], []
            if self.data.get('cf'):  # 中 > 法
                if word.get('phone'):
                    symbol_list.append([f'音 [{word["phone"]}]', [word['return-phrase']['l']['i']]])
                for index, tr in enumerate(word['trs'][0]['tr']):
                    explain_list.append([index + 1, [[tr['l']['i'][0], '']]])
            elif self.data.get('fc'):  # 法 > 中
                if word.get('phone'):
                    symbol_list.append([f'音 [{word["phone"]}]', [word['return-phrase']['l']['i'], self.data['le']]])
                for trs in word['trs']:
                    explain_list.append({'part': trs['pos'], 'means': [[trs['tr'][0]['l']['i'][0], '']]})
            # 添加数据
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list})
        # 【中韩】翻译结果解析
        elif self.data.get('le') == 'ko':
            word = (self.data.get('ck') or self.data.get('kc'))['word']
            # 解析音标和释义
            symbol_list, explain_list = [], []
            if self.data.get('ck'):  # 中 > 韩
                if word[0].get('phone'):
                    symbol_list.append([f'音 [{word[0]["phone"]}]', [word[0]['return-phrase']['l']['i']]])
                num = 1
                for trs in word[0]['trs']:
                    pos = trs.get('pos')
                    if pos is None:
                        for tr in trs['tr']:
                            pos = num
                            num += 1
                            explain_list.append({'part': pos, 'means': [[tr['l']['i'][0], '']]})
                    else:
                        explain_list.append({'part': pos, 'means': [[trs['tr'][0]['l']['i'][0], '']]})
            elif self.data.get('kc'):  # 韩 > 中
                for item in word:
                    for trs in item['trs']:
                        tr_list = [[tr['l']['i'][0], ''] for tr in trs['tr']]
                        explain_list.append({'part': trs['pos'], 'means': tr_list})
            explanation_data.append({'symbols': symbol_list, 'explains': explain_list})
        # 【中日】翻译结果解析
        elif self.data.get('le') == 'ja':
            newjc = self.data.get('newjc', {}).get('word')
            cj = self.data.get('cj', {}).get('word')
            newjc_data = []  # 「日 > 中」数据
            cj_data = []  # 「中 > 日」数据

            def get_word(word_):
                # 解析音标
                head = word_['head']
                symbol_list = []
                if head.get('rs'):
                    symbol_list.append([f'{head["pjm"]} [{head["rs"]}]', [head['pjm'], self.data['le']]])
                if head.get('sound'):
                    symbol_list.append([f'音 [{head["sound"]}]', [head['hw'], '']])
                # 解析释义
                num = 1
                explain_list = []
                for sense in word_['sense']:
                    cx = sense.get('cx') or num
                    jmsy_list = [[phrList['jmsy'], phrList.get('jmsyT', '')] for phrList in sense['phrList']]
                    explain_list.append({'part': cx, 'means': jmsy_list})
                    num += 1
                # 返回数据
                return {'symbols': symbol_list, 'explains': explain_list}

            # 解析翻译结果
            if newjc:  # 日 > 中
                word_data = get_word(newjc)
                newjc_data.append(word_data)
                # 同一个词语有多个读音和释义
                for mPhonicD in newjc.get('mPhonicD', []):
                    word_data = get_word(mPhonicD)
                    newjc_data.append(word_data)
            if cj:  # 中 > 日
                word_data = get_word(cj)
                cj_data.append(word_data)

            # 【中日】互译时如果有两个结果：
            # 1. 默认返回「中 > 日」结果
            # 2. 参数 reverse=True 时返回「日 > 中」结果
            if newjc and cj:
                explanation_data = newjc_data if reverse else cj_data
            else:
                explanation_data = newjc_data or cj_data

        return explanation_data

    def get_sentence(self, more=False):
        """获取例句"""
        sentence_data = []
        if more:
            query = f'lj:{self.data["meta"]["input"]}'
            le = self.data['meta']['le']
            form_data = self._get_form_data(query, le)
            response = self.session.post(self.url, data=form_data, headers=self.headers)
            body = response.json()
            sentence_pair = body.get('blng_sents', {}).get('sentence-pair', [])
        else:
            sentence_pair = self.data.get('blng_sents_part', {}).get('sentence-pair', [])
        for item in sentence_pair:
            # 补全获取例句语音的参数，然后再通过 urllib.parse.parse_qs 解析参数
            speech = parse_qs('audio=' + (item.get('sentence-speech') or item.get('sentence-translation-speech')))
            sentence_data.append([
                item.get('sentence-eng') or item.get('sentence'),  # 例句
                item.get('sentence-translation'),  # 例句翻译
                [speech.get('audio', [''])[0], speech.get('le', [''])[0]]  # 例句语音获取参数
            ])
        return sentence_data

    def get_tts(self, audio, le='', type_=2):
        """获取发音"""
        url = 'https://dict.youdao.com/dictvoice'
        params = {'audio': audio, 'le': le, 'type': type_}
        response = self.session.get(url, params=params, headers=self.headers)
        content = response.content
        return content


if __name__ == '__main__':
    yt = YoudaoTranslate()
    yt.translate('good', 'en')
    explanations = yt.get_explanation()
    # tts_uk = yt.get_tts(*explanations[0]['symbols'][0][1])
    # tts_us = yt.get_tts(*explanations[0]['symbols'][1][1])
    sentences = yt.get_sentence(True)
    print(yt.data)
