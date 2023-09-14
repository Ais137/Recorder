# Name: 测试服务器
# Date: 2023-08-22
# Author: Ais
# Desc: None


from scrapy.commands import ScrapyCommand


class TestServer(ScrapyCommand):

    default_settings = {
        "TEST": "BBB"
    }

    def short_desc(self):
        return "测试服务器"
    
    def run(self, args, opts):
        print("----------" * 5)
        print(f'[{self.__class__.__name__}]: ')
        print(f"[args]: {args}")
        print(f"[opts]: {opts}")
        