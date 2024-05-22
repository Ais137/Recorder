# Scrapy-命令行模块架构分析

## 1. 概述
*Scrapy* 命令行模块封装了开发过程中的一些常用操作，比如项目构建，基准测试，爬虫启动等功能。

在我个人观点看来，框架相关的开发工具链与框架本身具有相同的重要程度，因此在基于 *scrapy* 二次开发的框架中，怎样将业务相关的开发工具整合到框架中是一个值得探讨的问题。

为此，本文的主要目的是通过分析 *Scrapy* 框架命令行模块的源码实现来了解其架构设计，从而解决自定义的需求。

* [Scrapy-命令行模块架构分析](#scrapy-命令行模块架构分析)
    * [1. 概述](#1-概述)
    * [2. 源码分析](#2-源码分析)
        * [2.1. 从 *scrapy startproject demo* 开始](#21-从-scrapy-startproject-demo-开始)
        * [2.2. *startproject* 命令源码分析](#22-startproject-命令源码分析)
        * [2.3. 核心类 *ScrapyCommand* 分析](#23-核心类-scrapycommand-分析)
        * [2.4. *ScrapyCommand* 对象执行流程分析](#24-scrapycommand-对象执行流程分析)
    * [3. 架构设计](#3-架构设计)
    * [4. 自定义](#4-自定义)
        * [自定义命令模块](#自定义命令模块)
        * [自定义爬虫模板](#自定义爬虫模板)
    * [5. 总结](#5-总结)


-------------------------------------------------------
## 2. 源码分析

### 2.1. 从 *scrapy startproject demo* 开始
*scrapy startproject demo* 可以算是学习 *scrapy* 框架时接触到的第一条命令。该命令用于创建 *scrapy* 项目的代码框架。其会在当前目录生下成一个 *demo* 目录，并包含一系列的模板代码。现在通过该命令来分析其源码实现和命令行模块的架构设计。

### 2.2. *startproject* 命令源码分析
*startproject* 命令的源码实现位于 ***scrapy.commands.startproject*** 模块中。核心逻辑位于 *Command(ScrapyCommand)* 类的 *run* 方法中。

```py
class Command(ScrapyCommand):

    ...

    def run(self, args, opts):
        
        # 检测参数数量
        if len(args) not in (1, 2):
            raise UsageError()

        # 调用参数: 项目名/项目目录
        project_name = args[0]
        project_dir = args[0]
        if len(args) == 2:
            project_dir = args[1]

        # 检查项目目录下是否包含scrapy.cfg文件
        if exists(join(project_dir, 'scrapy.cfg')):
            self.exitcode = 1
            print(f'Error: scrapy.cfg already exists in {abspath(project_dir)}')
            return

        # 检测项目名是否合法
        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return

        # 复制模板文件到项目目录
        self._copytree(self.templates_dir, abspath(project_dir))

        # 修改模板文件的模块名(set:project_name)
        move(join(project_dir, 'module'), join(project_dir, project_name))

        # TEMPLATES_TO_RENDER -> 待渲染的模板文件列表
        for paths in TEMPLATES_TO_RENDER:
            # 拼接路径: '${project_name}/settings.py.tmpl'
            path = join(*paths)
            # 构建模板文件路径
            tplfile = join(project_dir, string.Template(path).substitute(project_name=project_name))
            # 渲染模板文件
            render_templatefile(tplfile, project_name=project_name, ProjectName=string_camelcase(project_name))

        # 输出
        print(f"New Scrapy project '{project_name}', using template directory "
                f"'{self.templates_dir}', created in:")
        print(f"    {abspath(project_dir)}\n")
        print("You can start your first spider with:")
        print(f"    cd {project_dir}")
        print("    scrapy genspider example example.com")

    ...
```

通过对上述源码分析发现，*startproject* 命令的主要功能如下
* 将 **模板目录** 下的文件渲染后(值填充)复制到 **项目目录**。
* 默认的模板目录位于 ***scrapy.templates***
* 可以通过在设置 **TEMPLATES_DIR** 参数来自定义模板目录
* 当检测到项目目录下存在 *scrapy.cfg* 文件时会抛出异常。
* 通过指定可选参数(project_dir)来设置项目目录，否则默认项目目录为(./project_name/)


### 2.3. 核心类 *ScrapyCommand* 分析
了解了 *startproject* 的实现逻辑，现在来分析其调用流程。通过对 *scrapy.commands* 下子模块的观察发现，其大多数都是通过继承 *ScrapyCommand* 类并重写 *run* 方法来实现主要功能。*ScrapyCommand* 类的实现位于 ***scrapy.commands.\_\_init\_\_*** :

```py
class ScrapyCommand:

    requires_project = False
    crawler_process = None

    # default settings to be used for this command instead of global defaults
    default_settings = {}

    exitcode = 0

    def __init__(self):
        self.settings = None  # set in scrapy.cmdline

    def set_crawler(self, crawler):
        if hasattr(self, '_crawler'):
            raise RuntimeError("crawler already set")
        self._crawler = crawler

    # 命令语法规则
    def syntax(self):
        """
        Command syntax (preferably one-line). Do not include command name.
        """
        return ""

    # 命令的简单描述
    def short_desc(self):
        """
        A short description of the command
        """
        return ""

    # 命令的完整描述
    def long_desc(self):
        """A long description of the command. Return short description when not
        available. It cannot contain newlines, since contents will be formatted
        by optparser which removes newlines and wraps text.
        """
        return self.short_desc()

    # 帮助信息
    def help(self):
        """An extensive help for the command. It will be shown when using the
        "help" command. It can contain newlines, since no post-formatting will
        be applied to its contents.
        """
        return self.long_desc()

    # 添加命令参数
    def add_options(self, parser):
        """
        Populate option parse with options available for this command
        """
        ...

    # 处理命令参数
    def process_options(self, args, opts):
        ...

    # 核心逻辑
    def run(self, args, opts):
        """
        Entry point for running commands
        """
        raise NotImplementedError
```

### 2.4. *ScrapyCommand* 对象执行流程分析

继续追踪分析 *ScrapyCommand* 对象的执行流程可以发现，其调用入口位于 ***scrapy.cmdline*** 模块的 *execute* 方法中:

```py
def execute(argv=None, settings=None):
    if argv is None:
        argv = sys.argv
    
    # 加载项目配置 (1)
    if settings is None:
        settings = get_project_settings()
        # set EDITOR from environment if available
        try:
            editor = os.environ['EDITOR']
        except KeyError:
            pass
        else:
            settings['EDITOR'] = editor

    # 判断是否在项目中(内部调用 closest_scrapy_cfg 方法从当前目录递归向上遍历查找 scrapy.cfg 文件)
    inproject = inside_project()
    # 核心逻辑: 构建命令映射表(命令名->ScrapyCommand实例) (2)
    cmds = _get_commands_dict(settings, inproject)
    # 获取当前调用的命令名 (3)
    cmdname = _pop_command_name(argv)
    # 构建命令行解析器 
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(),
                                   conflict_handler='resolve')
    # 校验 cmdname 的合法性
    if not cmdname:
        _print_commands(settings, inproject)
        sys.exit(0)
    elif cmdname not in cmds:
        _print_unknown_command(settings, cmdname, inproject)
        sys.exit(2)

    # 通过 命令映射表 获取指定 cmdname 的命令对象 
    cmd = cmds[cmdname]
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    settings.setdict(cmd.default_settings, priority='command')
    cmd.settings = settings
    # 添加并处理 cmd 对象中的自定义命令参数 (4)
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=argv[1:])
    _run_print_help(parser, cmd.process_options, args, opts)

    cmd.crawler_process = CrawlerProcess(settings)
    # 在 _run_command 中调用 cmd.run 方法 (5)
    _run_print_help(parser, _run_command, cmd, args, opts)
    sys.exit(cmd.exitcode)
```

通过上述源码可以清晰的明白命令的执行流程如下:  
1. 通过 *get_project_settings* 方法加载项目配置。
2. (核心逻辑)构建命令映射表对象 *cmds* -> {命令名: ScrapyCommand子类实例}。 
3. 解析当前执行的命令名 *cmdname*，并从 *cmds* 中获取对应的 *cmd* 对象。
4. 添加并处理 *cmd* 对象中的自定义命令参数
5. 调用 *cmd.run* 方法执行目标命令

在命令的整个执行流程中，最有意思的地方在于命令映射表对象 *cmds* 的构建，其完整的构建流程如下：

```py
def execute(argv=None, settings=None):
    ...
    cmds = _get_commands_dict(settings, inproject)
    ...

def _get_commands_dict(settings, inproject):
    # 通过框架默认命令模块 scrapy.commands 构建命令映射表
    cmds = _get_commands_from_module('scrapy.commands', inproject)
    # ?
    cmds.update(_get_commands_from_entry_points(inproject))
    # 从自定义配置参数 COMMANDS_MODULE 中构建命令映射表
    cmds_module = settings['COMMANDS_MODULE']
    if cmds_module:
        cmds.update(_get_commands_from_module(cmds_module, inproject))
    return cmds

def _get_commands_from_module(module, inproject):
    """
    遍历 module 下的所有 ScrapyCommand 子类, 并将其所在的
    模块名作为命令名，实例作为值，构建命令映射表。
    """
    d = {}
    # 遍历 module 下的所有 ScrapyCommand 子类
    for cmd in _iter_command_classes(module):
        if inproject or not cmd.requires_project:
            # ScrapyCommand 子类所在的模块名作为命令名
            cmdname = cmd.__module__.split('.')[-1]
            # 构建实例并绑定到 d 字典对象上
            d[cmdname] = cmd()
    return d

def _iter_command_classes(module_name):
    """
    通过 pkgutil(walk_modules) 迭代扫描 module_name 目录下的所有
    子模块，并遍历模块中的所有对象，从而提取 ScrapyCommand 的子类。
    """
    # 遍历所有模块(walk_modules 内部使用 pkgutil.iter_modules 实现)
    for module in walk_modules(module_name):
        # vars()函数返回对象object的属性和属性值的字典对象
        for obj in vars(module).values():
            if (
                # 判断是否是类
                inspect.isclass(obj)
                # 是否是 ScrapyCommand 的子类
                and issubclass(obj, ScrapyCommand)
                and obj.__module__ == module.__name__
                # 过滤 ScrapyCommand 基类
                and not obj == ScrapyCommand
            ):
                yield obj
```

*cmds* 的构建原理是通过迭代扫描 *scrapy.commands* 和 *COMMANDS_MODULE* 模块目录下的所有子模块，并从中提取和构建 *ScrapyCommand* 的实例来构建命令映射表对象。这种 *动态加载* 的机制相对于 *硬编码导入* 的方式有更高的扩展性。


-------------------------------------------------------
## 3. 架构设计
通过前述的源码分析，现在对 *Scrapy* 的命令行模块的架构设计进行总结。

*Scrapy* 命令行模块包含两个主要模块
* *scrapy.cmdline* : 命令行模块的调用入口，*ScrapyCommand* 子类的核心处理模块。
* *scrapy.commands* : 框架内置的命令模块。

其中核心类为 ***ScrapyCommand***，通过继承并重写指定方法来实现命令逻辑的封装。

*scrapy.cmdline* 模块在执行命令时，会通过一种 *动态加载* 机制，扫描 *scrapy.commands* 和 项目配置 *COMMANDS_MODULE* 下的所有 *ScrapyCommand* 子类来构建一张 *命令映射表*，并通过传入的命令参数，调用并执行对应的 *ScrapyCommand* 实例，以实现命令的执行。 


-------------------------------------------------------
## 4. 自定义
在理解 *scrapy* 命令行模块的整体架构后，来研究一下怎样对其进行自定义。

### 自定义命令模块
在之前的源码分析中发现，有一个配置参数 *COMMANDS_MODULE* 可以用来加载额外的命令模块，因此可以通过启用该参数来实现自定义命令与框架的整合。流程如下:

1. 在框架目录构建自定义命令包 *tools*。
```
demo
├─spiders
│  └─ __init__.py
├─tools
│  │  __int__.py
│  │  task.py
│  └─ server.py
│  __init__.py
└─ settings.py
```

2. 在 *tools* 中添加命令模块，通过继承 *ScrapyCommand* 类并重写指定方法来封装命令逻辑。
```py
# demo.tools.server
from scrapy.commands import ScrapyCommand


class TestServer(ScrapyCommand):

    def short_desc(self):
        return "测试服务器"
    
    def run(self, args, opts):
        print("----------" * 5)
        print(f'[{self.__class__.__name__}]: ')
        print(f"[args]: {args}")
        print(f"[opts]: {opts}")
```
需要注意的是，模块名将作为命令名。

3. 在 *settings* 中通过 **COMMANDS_MODULE** 参数配置自定义模块。
```py
COMMANDS_MODULE = 'demo.tools'
```

4. 使用在项目目录下使用 *scrapy -h* 查看当前所有命令，验证自定义模块是否加载成功。
```
Scrapy 2.3.0 - project: demo

Usage:
  scrapy <command> [options] [args]

Available commands:
  ...
  crawl         Run a spider
  server        测试服务器
  settings      Get settings values
  shell         Interactive scraping console
  startproject  Create new project
  task          任务调度器
  ...
```
命令的描述信息为 *short_desc* 方法中返回的字符串。

5. 运行命令进行验证。
```
> scrapy server start

--------------------------------------------------
[TestServer]:
[args]: ['start']
[opts]: {'logfile': None, 'loglevel': None, 'nolog': None, 'profile': None, 'pidfile': None, 'set': [], 'pdb': None}
```

### 自定义爬虫模板
另一个比较常见的自定义场景是爬虫模板的生成。*Scrapy* 框架通过 *genspider* 命令提供了一个爬虫模板生成工具。可以通过以下命令生成一个爬虫模块：

```sh
> scrapy genspider testspider "https://www.test.com" -t "crawl"

Created spider 'testspider' using template 'crawl' in module:
  demo.spiders.testspider
```

通过 *-t* 参数指定生成的爬虫模板，爬虫代码会生成到配置文件中 *NEWSPIDER_MODULE* 指定的地方。

如果想要加载自定义的配置模板，可以通过以下流程实现：

1. 创建 */demo/templates/spiders* 目录。
```
demo
├─ spiders
|   |  __init__.py
|   └─ testspider.py
|
├─ templates
│   ├─ project
│   └─ spiders
│      └─ test.tmpl
|
...
```

2. 创建 *test.tmpl* 模板文件, *$name* 等变量为后续模板填充值的占位符。 
```py
import scrapy


class $classname(scrapy.Spider):

    name = '$name'

    # 数据源信息
    source = {
        "name": "",
        "url": "https://$domain/"
    }

    # 自定义配置
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {

        },
        "ITEM_PIPELINES": {

        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url = "",
            callback = self.parse,
            dont_filter = True,
        )
```

3. 在配置文件中指定 **TEMPLATES_DIR** 参数，注意需要使用绝对路径。
```py
TEMPLATES_DIR = os.path.abspath('./templates')
```

4. 使用自定义模板生成爬虫文件。
```sh
scrapy genspider testspider "https://www.test.com" -t "test"
```

需要注意的是，*TEMPLATES_DIR* 参数不单会影响 *genspider* 的模板加载位置，还会影响 *startproject* 命令。这意味着同样可以自定义 *scrapy* 项目模板(*/demo/templates/project*)。

-------------------------------------------------------
## 5. 总结

通过对 *scrapy* 命令行模块源码实现的分析理解了其架构设计，其中最有趣的设计在于 *ScrapyCommand* 类的 **动态搜索与加载机制**，在 *scrapy* 框架中是采用 *pkgutil* 和 *importlib* 模块结合 *vars()* 函数实现的，另一个思路是通过 *\_\_subclasses\_\_*  方法来实现。这种动态机制相对于传统的硬编码导入使其具有更好的扩展性。后续考虑进一步研究这种动态机制(自省机制)在框架中的实现和应用场景。

