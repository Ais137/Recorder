# Name: 任务调度器
# Date: 2023-08-22
# Author: Ais
# Desc: None


from scrapy.commands import ScrapyCommand


class TaskScheduler(ScrapyCommand):

    def short_desc(self):
        return "任务调度器"
    
    def run(self, args, opts):
        print("----------" * 5)
        print(f'[{self.__class__.__name__}]: ')
        print(f"[args]: {args}")
        print(f"[opts]: {opts}")

        print(self.settings.get("TEST"))
        