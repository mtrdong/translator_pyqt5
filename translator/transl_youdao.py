# -*- coding: utf-8 -*-
import threading
from hashlib import md5

import requests


class YoudaoTranslate(object):
    """有道翻译爬虫"""
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not hasattr(YoudaoTranslate, '_instance'):
                cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.url = 'https://dict.youdao.com/jsonapi_s?doctype=json&jsonversion=4'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/105.0.0.0 Safari/537.36',
        }

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
        response = requests.post(self.url, data=form_data, headers=self.headers)
        data = response.json()
        print()
        print(f'音标：英/{data["ec"]["word"]["ukphone"]}/ 美/{data["ec"]["word"]["usphone"]}/')
        print(f'释义：{data["ec"]["word"]["trs"]}')
        print(f'词形：{data["expand_ec"]["word"][0]["wfs"] + data["expand_ec"]["word"][1]["wfs"]}')
        print(f'例句：{data["blng_sents_part"]["sentence-pair"]}')
        return data


if __name__ == '__main__':
    yt = YoudaoTranslate()
    yt.translate('good', 'en')
