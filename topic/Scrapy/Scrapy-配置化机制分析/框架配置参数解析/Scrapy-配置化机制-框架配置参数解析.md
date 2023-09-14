# Scrapy-配置化机制-框架配置参数解析

-------------------------------------------------------
## 概述
本文主要解析并记录 *Scrapy* 框架中的配置参数，持续更新中。

### Meta
```json
{
    "node": "DF268D16-E5FB-BCF6-C1ED-2DEEBADC82D4",
    "name": "Scrapy-配置化机制-框架配置参数解析",
    "author": "Ais",
    "date": "2023-09-07",
    "tag": ["数据采集", "scrapy", "配置化机制", "Settings"]
}
```

-------------------------------------------------------
## 框架配置参数解析

### COMMANDS_MODULE
* 功能：用于加载自定义的命令行模块，框架会扫描该参数下的模块目录，查找 *scrapy.commands.ScrapyCommand* 子类。
* 样例：`COMMANDS_MODULE = 'demo.tools'`
* 源码：**scrapy.cmdline**
```py
def _get_commands_dict(settings, inproject):
    # 加载默认命令行模块
    cmds = _get_commands_from_module('scrapy.commands', inproject)
    cmds.update(_get_commands_from_entry_points(inproject))
    # 加载自定义命令行模块
    cmds_module = settings['COMMANDS_MODULE']
    if cmds_module:
        cmds.update(_get_commands_from_module(cmds_module, inproject))
    return cmds
```

### DUPEFILTER_CLASS
* 功能：指定框架加载的请求去重器对象，用于自定义请求去重逻辑。
* 样例：`DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'`
* 源码：**scrapy.core.scheduler**
```py
class Scheduler:
    ...

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        # 加载请求去重器类
        dupefilter_cls = load_object(settings['DUPEFILTER_CLASS'])
        # 构建请求去重器实例
        dupefilter = create_instance(dupefilter_cls, settings, crawler)
        ...
```

### JOBDIR
* 功能：指定框架持久化机制的数据缓存目录。
* 样例：`JOBDIR = "./temp"`
* 源码：**scrapy.utils.job**
```py
def job_dir(settings):
    path = settings['JOBDIR']
    # 检查目录是否存在并创建
    if path and not os.path.exists(path):
        os.makedirs(path)
    return path
```

### TEMPLATES_DIR
* 功能：通过指定该参数来加载自定义代码模板，用于命令行模块中的 *startproject* 和 *genspider* 命令。
* 样例： `TEMPLATES_DIR = abspath(join(dirname(__file__), '..','templates'))`
* 源码：**scrapy.commands.startproject** & **scrapy.commands.genspider**
```py
class Command(ScrapyCommand):
    ...

    @property
    def templates_dir(self):
        return join(
            self.settings['TEMPLATES_DIR'] or join(scrapy.__path__[0], 'templates'),
            'project'
        )
``` 

