# -*- coding: utf-8 -*-
import json
import threading

import requests


class GoogleTranslate(object):
    """谷歌翻译爬虫"""
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not hasattr(GoogleTranslate, '_instance'):
                cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.url = 'https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/105.0.0.0 Safari/537.36',
        }

    @staticmethod
    def get_form_data(query, from_str, to_str):
        """构建表单参数"""
        form_data = {
            'f.req': json.dumps([[["MkEWBc", f"[[\"{query}\",\"{from_str}\",\"{to_str}\",true],[null]]", None, "generic"]]]),
        }
        return form_data

    def translate(self, query, from_str, to_str):
        """翻译"""
        form_data = self.get_form_data(query, from_str, to_str)
        response = requests.post(self.url, data=form_data, headers=self.headers)
        content = response.content.decode().split('\n\n')[-1]
        data = json.loads(json.loads(content)[0][2])
        print()
        print(f'拼音：{data[0][0]}')
        print(f'结果：{data[1][0][0][5][0][0]}')
        print(f'释义：{data[3][5][0]}')
        print(f'例句：{data[3][2][0]}')
        return data


if __name__ == '__main__':
    gt = GoogleTranslate()
    gt.translate('good', 'auto', 'zh-CN')
