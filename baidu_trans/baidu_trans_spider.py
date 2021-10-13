# -*- coding: utf-8 -*-
import json
import math
import re
import threading

import requests
from retrying import retry


def n(r: int, o: str):
    for t in range(0, len(o) - 2, 3):
        a = o[t + 2]
        a = ord(a[0]) - 87 if a >= "a" else int(a)
        a = r >> a if o[t + 1] == "+" else r << a
        r = r + a & 4294967295 if o[t] == "+" else r ^ a
    return r


def e(r: str):
    i = "320305.131321201"
    o = re.findall("[\U00010000-\U0010ffff]", r)
    if not o:
        t = len(r)
        if t > 30:
            r = r[:10] + r[math.floor(t / 2) - 5: math.floor(t / 2) + 5] + r[-10:]
    else:
        e = re.split("[\U00010000-\U0010ffff]", r)
        h, f = len(e), []
        for C in range(0, h):
            if e[C]:
                f.extend(e[C])
            if C != h - 1:
                f.append(o[C])
        g = len(f)
        if g > 30:
            r = "".join(f[:10] + f[math.floor(g / 2) - 5: math.floor(g / 2) + 5] + f[-10:])
    d = i.split(".")
    S, v = [], 0
    while v < len(r):
        A = ord(r[v])
        if 128 > A:
            S.append(A)
        elif 2048 > A:
            S.extend([A >> 6 | 192, 63 & A | 128])
        elif (64512 & A) == 55296 and len(r) > v + 1 and (64512 & ord(r[v + 1])) == 56320:
            # TODO 翻译内容中包含 emoji 表情时无法得到正确的 sign
            #  由于 Python 与 JavaScript 对 emoji 表情字符的编码不一样
            #  输入 emoji 表情时，Python 的 ord() 与 JavaScript 的 charCodeAt() 返回的值不一样
            A = 65536 + ((1023 & A) << 10) + (1023 & ord(r[++v]))
            S.extend([A >> 18 | 240, A >> 12 & 63 | 128, A >> 6 & 63 | 128, 63 & A | 128])
        else:
            S.extend([A >> 12 | 224, A >> 6 & 63 | 128, 63 & A | 128])
        v += 1
    m, s, F, D = int(d[0]) | 0, int(d[1]) | 0, "+-a^+6", "+-3^+b+-f"
    p = m
    for b in range(0, len(S)):
        p += S[b]
        p = n(p, F)
    p = n(p, D) ^ s
    if p < 0:
        p = (2147483647 & p) + 2147483648
    p = int(p % 1e6)
    return f"{p}.{p ^ m}"


class BaiDuTrans(object):
    """ 百度翻译爬虫
    实例化爬虫后调用`start_trans()`方法进行翻译，调用`get_result()`方法获取翻译结果用于控制台输出
    调用`get_tts()`方法可获取发音
    调用`get_str_from_img()`方法可获取图片中的文字
    """
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not hasattr(BaiDuTrans, '_instance'):
                cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self._trans_flag = False
        self._result = {}
        self._url = 'https://fanyi.baidu.com'
        self._headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.182 Safari/537.36',
        }
        response = requests.get(url=self._url, headers=self._headers)
        self._cookie = response.headers.get('Set-Cookie')
        self._headers['cookie'] = self._cookie
        response = requests.get(url=self._url, headers=self._headers)
        self._token = re.findall(r'token:[\s\'\"]+([a-z0-9]+)[\'\"]', response.content.decode())

    @retry(stop_max_attempt_number=3)
    def _post(self, path='', form_data=None, files=None):
        """发送请求"""
        return requests.post(url=self._url + path, headers=self._headers, data=form_data, files=files, timeout=5)

    @retry(stop_max_attempt_number=3)
    def _get(self, path=''):
        """发送请求"""
        return requests.post(url=self._url + path, headers=self._headers, timeout=5)

    def _get_lan(self, query):
        """查询语言种类"""
        path = '/langdetect'
        form_data = {
            'query': query,
        }
        response = self._post(path, form_data)
        content = json.loads(response.content)
        return content.get('lan')

    def _get_form_data(self, query, from_str, to_str):
        """构建表单参数"""
        # with open(index_d52622f_js, 'r', encoding='utf-8') as f:
        #     js = f.read()
        # sign = execjs.compile(js).call('e', query)
        sign = e(query)
        form_data = {
            'from': from_str,
            'to': to_str,
            'query': query,
            'sign': sign,
            'token': self._token,
        }
        return form_data

    def _get_comment_str(self):
        """获取单词释义"""
        try:
            parts = self._result["dict_result"]["simple_means"]["symbols"][0]["parts"]
        except:
            return ''
        else:
            comment_list = []
            for part in parts:
                try:
                    means_list = [text['text'] for text in part['means']]
                except:
                    means_list = part['means']
                part_str = part.get('part') if part.get('part') else part.get('part_name', '')
                if part_str:
                    comment_list.append(part_str + ' ' + '；'.join(means_list))
                else:
                    comment_list.append('；'.join(means_list))
            return '\n'.join(comment_list)

    def _get_spell_str(self):
        """获取单词音标"""
        spell_list = []
        spell_dict = {
            'ph_en': '英',
            'ph_am': '美',
            'word_symbol': '音',
        }
        try:
            spell = self._result['dict_result']['simple_means']['symbols'][0]
            for k, v in spell_dict.items():
                if spell.get(k):
                    spell_list.append(f'{v} [{spell.get(k)}]')
        except:
            return ''
        return '   '.join(spell_list)

    def _get_exchange_str(self):
        """获取单词形态"""
        exchange_list = []
        exchange_dict = {
            'word_third': '第三人称单数',
            'word_pl': '复数',
            'word_ing': '现在分词',
            'word_done': '过去式',
            'word_past': '过去分词',
            'word_er': '比较级',
            'word_est': '最高级',
        }
        try:
            exchange = self._result['dict_result']['simple_means']['exchange']
            for k, v in exchange_dict.items():
                if exchange.get(k):
                    exchange_list.append(f'{v}：{exchange.get(k)[0]}')
        except:
            return ''
        return '   '.join(exchange_list)

    def _get_keywords_str(self):
        """获取重点词汇"""
        keywords_list = []
        try:
            keywords_dict = self._result['trans_result']['keywords']
            for keywords in keywords_dict:
                keywords_list.append(keywords['word'] + '   ' + '；'.join([s for s in keywords['means']]))
        except:
            return ''
        return '重点词汇：\n' + '\n'.join(keywords_list)

    def _get_explanation(self):
        """获取简明释义"""
        result_str = '\n\n'.join(
            [s for s in [self._get_spell_str(), self._get_comment_str(), self._get_exchange_str()] if s]
        )
        if not result_str:
            result_str = self._get_keywords_str()
        return result_str

    def _get_trans_result(self):
        """获取直译结果"""
        try:
            trans_result = '\n'.join([data['dst'] for data in self._result['trans_result']['data']])
        except:
            trans_result = ''
        return trans_result

    def _get_example(self):
        """获取例句"""
        try:
            example = json.loads(self._result['liju_result']['double'])[0][:2]  # 只取第一条例句
        except:
            return ''
        en_str = ''
        for s in [s[0] for s in example[0]]:
            if re.match(r'^[a-zA-Z]+$', s):
                en_str = en_str + ' ' + s
            else:
                en_str = en_str + s
        zh_str = ''.join([s[0] for s in example[1]])
        return en_str.strip(), zh_str

    def start_trans(self, query: str, to_str: str):
        """ 启动翻译
        翻译成功后返回百度翻译的源数据
        :param query: 翻译内容
        :param to_str: 目标语言
        """
        self._result = {}
        lan = self._get_lan(query)
        from_str = lan
        if lan == to_str:
            to_str = 'en' if lan == 'zh' else 'zh'
        path = f'/v2transapi?from={from_str}&to={to_str}'
        form_data = self._get_form_data(query, from_str, to_str)
        response = self._post(path, form_data)
        self._result = json.loads(response.content)
        if self._result.get('error'):
            raise Exception('度娘翻译官没有给到想要的结果')
        self._trans_flag = True
        return self._result

    def get_result(self):
        """ 获取翻译结果
        获取翻译结果前须调用 start_trans(query, to_str) 方法启动翻译
        翻译结果以字符串列表形式返回。第一个元素为直译结果，第二各元素为简明释义
        """
        if self._trans_flag:
            return self._get_trans_result(), self._get_explanation(), self._get_example()
        raise Exception('获取翻译结果失败')

    def get_tts(self, lan: str, text: str):
        """获取单词发音"""
        spd = 5 if lan == 'zh' else 3
        path = f'/gettts?lan={lan}&text={text}&spd={spd}&source=web'
        try:
            content = self._get(path).content
        except:
            content = None
        return content

    def get_str_from_img(self, img: bytes):
        """从图片中提取文字(精度差)"""
        path = '/getocr'
        form_data = {
            'from': 'auto',
            'to': 'en'
        }
        files = {'image': img}
        response = self._post(path, form_data, files)
        data = json.loads(response.content)
        try:
            return ''.join(data['data'].get('src'))
        except:
            return ''


if __name__ == '__main__':
    bt = BaiDuTrans()
    while 1:
        word = input('请输入您要翻译的内容（仅支持中英互译）: ')
        if not word:
            select = input('您要退出吗（Y/N）: ')
            if select.lower() == 'y':
                break
        else:
            to_lan = 'zh' if re.findall('[\u4e00-\u9fa5]+', word) else 'en'
            try:
                bt.start_trans(word, to_lan)
            except Exception as e:
                print(f'【翻译出错啦】{e}')
            else:
                result, explanation, example = bt.get_result()
                print(f'【译】: {result}')
                print(f'【典】: \n{explanation}\n')
                print(f'【例】: \n{example[0]}\n{example[1]}\n')
