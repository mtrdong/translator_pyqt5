import httpx


class BaseTranslate(object):
    """翻译爬虫的基类"""

    def __init__(self):
        self.session = httpx.Client()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/106.0.0.0 Safari/537.36'
        }
        # 主页
        self.home = None
        # 翻译结果
        self.data = None

    def translate(self, query, from_lan, to_lan, *args, **kwargs):
        """ 启动翻译

        :param query: 翻译内容
        :param from_lan: 目标语言
        :param to_lan: 源语言
        :return:
        """
        pass

    def get_translation(self, *args, **kwargs):
        """获取译文"""
        pass

    def get_explanation(self, *args, **kwargs):
        """获取释义"""
        pass

    def get_sentence(self, *args, **kwargs):
        """获取例句"""
        pass

    def get_tts(self, text, lan, *args, **kwargs) -> bytes:
        """ 获取发音

        :param text: 源文本
        :param lan: 文本语言
        :return: 文本语音
        """
        pass
