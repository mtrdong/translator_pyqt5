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
            # 中日互译时如果有两种结果，则该标志为 True
            self.reverse_flag = False

    def get_voice(self, audio, le='', type_=2):
        """获取发音"""
        url = 'https://dict.youdao.com/dictvoice'
        params = {'audio': audio, 'le': le, 'type': type_}
        response = self.session.get(url, params=params, headers=self.headers)
        content = response.content
        return content

    def get_explanation(self, reverse=False):
        """获取释义"""
        explanation_data = []
        if self.data.get('fanyi'):
            explanation_data.append([[], [1, [[self.data['fanyi']['tran'], '']]]])
        # 【中英】翻译结果解析
        elif self.data['le'] == 'en':
            word = (self.data.get('ce') or self.data.get('ec'))['word']
            # 解析读音
            spell_data = []
            if word.get('phone'):
                spell_data.append([f'音[{word["phone"]}]', [word['return-phrase']]])
            if word.get("ukphone"):
                spell_data.append([f'英[{word["ukphone"]}]', [word['return-phrase'], '', 1]])
            if word.get("usphone"):
                spell_data.append([f'美[{word["usphone"]}]', [word['return-phrase']]])
            # 解析释义
            trs_data = []
            for index, item in enumerate(word['trs']):
                trs_data.append([
                    item.get('pos') or index + 1,
                    [[item.get('tran') or item.get('#text'), item.get('#tran', '')]]
                ])
            # 添加数据
            explanation_data.append([spell_data, trs_data])
        # 【中法】翻译结果解析
        elif self.data['le'] == 'fr':
            word = (self.data.get('cf') or self.data.get('fc'))['word'][0]
            # 解析读音和释义
            spell_data, trs_data = [], []
            if self.data.get('cf'):  # 中 > 法
                if word.get('phone'):
                    spell_data.append([f'音[{word["phone"]}]', [word['return-phrase']['l']['i']]])
                for index, tr in enumerate(word['trs'][0]['tr']):
                    trs_data.append([index + 1, [[tr['l']['i'][0], '']]])
            elif self.data.get('fc'):  # 法 > 中
                if word.get('phone'):
                    spell_data.append([f'音[{word["phone"]}]', [word['return-phrase']['l']['i'], self.data['le']]])
                for trs in word['trs']:
                    trs_data.append([trs['pos'], [[trs['tr'][0]['l']['i'][0], '']]])
            # 添加数据
            explanation_data.append([spell_data, trs_data])
        # 【中韩】翻译结果解析
        elif self.data['le'] == 'ko':
            word = (self.data.get('ck') or self.data.get('kc'))['word']
            # 解析读音和释义
            spell_data, trs_data = [], []
            if self.data.get('ck'):  # 中 > 韩
                if word[0].get('phone'):
                    spell_data.append([f'音[{word["phone"]}]', [word['return-phrase']['l']['i']]])
                num = 1
                for trs in word[0]['trs']:
                    pos = trs.get('pos')
                    if pos is None:
                        for tr in trs['tr']:
                            pos = num
                            num += 1
                            trs_data.append([pos, [[tr['l']['i'][0], '']]])
                    else:
                        trs_data.append([pos, [[trs['tr'][0]['l']['i'][0], '']]])
            elif self.data.get('kc'):  # 韩 > 中
                for item in word:
                    for trs in item['trs']:
                        tr_list = [[tr['l']['i'][0], ''] for tr in trs['tr']]
                        trs_data.append([trs['pos'], tr_list])
            explanation_data.append([spell_data, trs_data])
        # 【中日】翻译结果解析
        elif self.data['le'] == 'ja':
            newjc = self.data.get('newjc', {}).get('word')
            cj = self.data.get('cj', {}).get('word')
            newjc_data = []  # 「日 > 中」数据
            cj_data = []  # 「中 > 日」数据

            def get_word(word_):
                # 解析读音
                head = word_['head']
                spell_data = []
                if head.get('rs'):
                    spell_data.append([f'{head["pjm"]}[{head["rs"]}]', [head['pjm'], self.data['le']]])
                if head.get('sound'):
                    spell_data.append([f'音[{head["sound"]}]', [head['hw'], '']])
                # 解析释义
                num = 1
                jmsy_data = []
                for sense in word_['sense']:
                    cx = sense.get('cx') or num
                    jmsy_list = [[phrList['jmsy'], phrList.get('jmsyT', '')] for phrList in sense['phrList']]
                    jmsy_data.append([cx, jmsy_list])
                    num += 1
                # 返回数据
                return [spell_data, jmsy_data]

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

    def get_sentence(self):
        """获取例句"""
        sentence_data = []
        with suppress(KeyError, TypeError):
            sentence_pair = self.data["blng_sents_part"]["sentence-pair"]
            for item in sentence_pair:
                speech = parse_qs('audio=' + (item.get('sentence-speech') or item.get('sentence-translation-speech')))
                sentence_data.append([
                    item.get('sentence-eng') or item.get('sentence'),
                    [speech.get('audio', [''])[0], speech.get('le', [''])[0], speech.get('type', [''])[0]],
                    item.get('sentence-translation'),
                ])
        return sentence_data

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
        if le == 'ja':  # 【中日】互译时检查是否有两种结果
            newjc = self.data.get('newjc', {}).get('word')
            cj = self.data.get('cj', {}).get('word')
            self.reverse_flag = True if newjc and cj else False


if __name__ == '__main__':
    yt = YoudaoTranslate()
    yt.translate('막다', 'ko')
    explanation = yt.get_explanation()
    # voice_uk = yt.get_voice(*explanation[0][0][0][1])
    # voice_us = yt.get_voice(*explanation[0][0][1][1])
    sentence = yt.get_sentence()
    print(yt.data)
