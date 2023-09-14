# Scrapy-配置化机制-配置容器结构分析

## 1. 概述
*Scrapy* 框架支持从多个源加载配置参数，比如通过 *settings.py* 模块，又或者是在 *Spider* 类的 *custom_settings* 中设置。这些配置参数在框架运行时是如何存储的(配置容器结构分析)，不同的配置源中相同的配置之间是如何覆盖的(配置加载流程分析)等问题，是本文的主要探究目标。

### Index
- [Scrapy-配置化机制-配置容器结构分析](#scrapy-配置化机制-配置容器结构分析)
  - [1. 概述](#1-概述)
    - [Index](#index)
    - [Meta](#meta)
  - [2. 结构分析](#2-结构分析)
    - [2.1. *settings.py* 配置模块的加载机制分析](#21-settingspy-配置模块的加载机制分析)
    - [2.2. *get\_project\_settings* 函数实现逻辑](#22-get_project_settings-函数实现逻辑)
    - [2.3. 配置容器结构分析](#23-配置容器结构分析)
    - [2.4. 配置加载流程分析](#24-配置加载流程分析)
  - [3. 总结](#3-总结)

### Meta
```json
{
    "node": "E39245A2-3097-DD83-5267-7C2DCC8FC5D6",
    "name": "Scrapy-配置化机制-配置容器结构分析",
    "author": "Ais",
    "date": "2023-08-30",
    "tag": ["数据采集", "scrapy", "配置化机制", "Settings"]
}
```

-------------------------------------------------------
## 2. 结构分析

在使用 *startproject* 命令生成 *scrapy* 代码框架时，会在项目目录生成一个 *settings.py* 模块，该模块包含了一系列配置参数，用于对框架进行自定义。比如请求的并发数配置，中间件配置，数据管道配置等。通过配置这些参数，可以让框架的运行状态与具体的应用场景更加匹配。

```py
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'demo.middlewares.DownloaderMiddleware': 543,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'demo.pipelines.Pipeline': 300,
}

...
```

下面通过分析具体的源码实现，来看看这些配置在框架中是如何加载和存储的。

### 2.1. *settings.py* 配置模块的加载机制分析 

要分析 *settings.py* 配置模块的加载机制，首先需要了解框架的启动流程，最简单的方式是通过 *crwal* 命令启动一个爬虫。

```sh
scrapy crawl spider
```

通过之前的一篇文章 [Scrapy-命令行模块架构分析](../../Scrapy-命令行模块架构分析/Scrapy-命令行模块架构分析.md)，可以定位到 *crawl* 命令的源码位置，即 ***scrapy.commands.crawl*** 模块。核心逻辑如下: 

```py
def run(self, args, opts):
    if len(args) < 1:
        raise UsageError()
    elif len(args) > 1:
        raise UsageError("running 'scrapy crawl' with more than one spider is no longer supported")
    spname = args[0]

    # 关键代码
    crawl_defer = self.crawler_process.crawl(spname, **opts.spargs)

    if getattr(crawl_defer, 'result', None) is not None and issubclass(crawl_defer.result.type, Exception):
        self.exitcode = 1
    else:
        # 关键代码
        self.crawler_process.start()

        if (
            self.crawler_process.bootstrap_failed
            or hasattr(self.crawler_process, 'has_exception') and self.crawler_process.has_exception
        ):
            self.exitcode = 1
```

其中 *self.crawler_process* 对象用于控制爬虫的启动和运行，其实际的构建和加载位置位于 ***scrapy.cmdline*** 模块的 *execute* 方法中: 

```py
cmd.crawler_process = CrawlerProcess(settings)
```

可以看到 *crawler_process* 属性是一个 *CrawlerProcess* 类的实例，其初始化参数是一个 *settings* 对象，其加载逻辑同样位于 *execute* 方法中, 相关代码如下: 

```py
def execute(argv=None, settings=None):
    ...

    if settings is None:
        settings = get_project_settings()
        # set EDITOR from environment if available
        try:
            editor = os.environ['EDITOR']
        except KeyError:
            pass
        else:
            settings['EDITOR'] = editor

    ...

    cmd = cmds[cmdname]
    settings.setdict(cmd.default_settings, priority='command')
    cmd.settings = settings
    
    ...
```

当 *execute* 未传入 *settings* 参数时， *settings* 对象是由 *get_project_settings* 函数的返回值创建的。

### 2.2. *get_project_settings* 函数实现逻辑

*get_project_settings* 函数的源码位于 ***scrapy.utils.project*** 模块中，其实现逻辑如下：

```py
# 获取项目配置
def get_project_settings():
    # 初始化环境变量
    if ENVVAR not in os.environ:
        project = os.environ.get('SCRAPY_PROJECT', 'default')
        # 1. 设置 SCRAPY_SETTINGS_MODULE 环境变量, 值为 scrapy.cfg 中的 [settings] 参数
        # 2. 将 scrapy.cfg 所在目录添加到环境路径中
        init_env(project)

    # 核心逻辑: 构建配置容器对象 
    settings = Settings()
    # 加载 settings 模块: 从 scrapy.cfg 中的 [settings] 参数加载 settings.py 模块的配置到 settings 对象中。 
    settings_module_path = os.environ.get(ENVVAR)
    # settings_module_path = os.environ.get('SCRAPY_SETTINGS_MODULE')
    if settings_module_path:
        settings.setmodule(settings_module_path, priority='project')

    # (弃用)从 SCRAPY_PICKLED_SETTINGS_TO_OVERRIDE 的二进制对象中加载配置
    pickled_settings = os.environ.get("SCRAPY_PICKLED_SETTINGS_TO_OVERRIDE")
    if pickled_settings:
        warnings.warn("Use of environment variable "
                      "'SCRAPY_PICKLED_SETTINGS_TO_OVERRIDE' "
                      "is deprecated.", ScrapyDeprecationWarning)
        settings.setdict(pickle.loads(pickled_settings), priority='project')

    # 遍历环境变量，查找以 SCRAPY_ 开头的环境变量。
    scrapy_envvars = {k[7:]: v for k, v in os.environ.items() if
                      k.startswith('SCRAPY_')}

    # (弃用)无效代码
    # valid_envvars = {
    #     'CHECK',
    #     'PICKLED_SETTINGS_TO_OVERRIDE',
    #     'PROJECT',
    #     'PYTHON_SHELL',
    #     'SETTINGS_MODULE',
    # }
    # setting_envvars = {k for k in scrapy_envvars if k not in valid_envvars}
    # if setting_envvars:
    #     setting_envvar_list = ', '.join(sorted(setting_envvars))
    #     warnings.warn(
    #         'Use of environment variables prefixed with SCRAPY_ to override '
    #         'settings is deprecated. The following environment variables are '
    #         'currently defined: {}'.format(setting_envvar_list),
    #         ScrapyDeprecationWarning
    #     )

    # 加载环境变量到 settings 对象中
    settings.setdict(scrapy_envvars, priority='project')

    return settings
```

由上述源码可知，*get_project_settings* 函数主要流程如下:
1. 初始化环境变量：通过 *init_env* 函数查找 *scrapy.cfg* 文件，并将 *settings.py* 模块路径 *SCRAPY_SETTINGS_MODULE* 添加到环境变量。
2. 构建配置容器：构建 *scrapy.settings.Settings* 类的对象实例。
3. 加载配置模块：通过 *settings* 对象的 *setmodule* 方法将项目配置模块 *settings.py* 中的配置参数加载到 *settings* 对象中。
4. 加载环境变量：查找以 *SCRAPY_* 开头的环境变量并加载到 *settings* 对象中。

因此 *settings.py* 配置模块在框架运行时，是通过 *get_project_settings* 函数加载到 *settings* 对象中进行存储的。


### 2.3. 配置容器结构分析

通过对 *get_project_settings* 函数的实现逻辑分析可以发现，其返回值 *settings* 对象是 *scrapy.settings.Settings* 类的实例，同时也是 *settings.py* 项目配置模块的存储对象。所以 ***scrapy.settings*** 是框架配置容器所在的关键模块。

***scrapy.settings*** 模块中包含三个核心类：
1. *scrapy.settings.Settings* ：配置容器
1. *scrapy.settings.BaseSettings* ：配置容器基类
2. *scrapy.settings.SettingsAttribute* ：配置属性容器

*Settings* 类是 *BaseSettings* 的派生子类，因此 **配置参数** 的实际存储逻辑是在 *BaseSettings* 中实现的，其主要结构如下： 

```py
class BaseSettings(MutableMapping):
    """
    Instances of this class behave like dictionaries, but store priorities
    """

    def __init__(self, values=None, priority='project'):
        # 冻结标记，当使用 self.freeze 方法时，该标记将设置为 True
        self.frozen = False
        # 实际存储结构(dict)
        self.attributes = {}
        # 更新值
        self.update(values, priority)

    def __getitem__(self, opt_name):
        if opt_name not in self:
            return None
        return self.attributes[opt_name].value

    def __contains__(self, name):
        return name in self.attributes

    # 获取值
    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    def __setitem__(self, name, value):
        self.set(name, value)

    # 设置值
    def set(self, name, value, priority='project'):
        # 检测对象是否冻结(self.frozen)
        self._assert_mutability()
        # 转换优先级(str->int)
        priority = get_settings_priority(priority)
        # 将 value 封装成 SettingsAttribute 对象存储到 self.attributes 属性中
        if name not in self:
            if isinstance(value, SettingsAttribute):
                self.attributes[name] = value
            else:
                self.attributes[name] = SettingsAttribute(value, priority)
        else:
            self.attributes[name].set(value, priority)

    # 更新值(批量设置值)
    def update(self, values, priority='project'):
        # 检测对象是否冻结(self.frozen)
        self._assert_mutability()
        # 将字符串类型的值转换成字典
        if isinstance(values, str):
            values = json.loads(values)
        # 遍历 values 对象并设置值
        if values is not None:
            if isinstance(values, BaseSettings):
                for name, value in values.items():
                    self.set(name, value, values.getpriority(name))
            else:
                for name, value in values.items():
                    self.set(name, value, priority)

    ...
```

**scrapy.settings.BaseSettings** 作为框架的配置容器，采用了一种类字典的结构设计，内部使用 *self.attributes* 属性(dict)作为实际的值存储结构。但是与传统的字典不同，引入了一种 *优先级* 的存储机制。*set* 方法是值的存储入口。其定义如下：

```py
def set(self, name, value, priority='project'):
    ...
    if name not in self:
        if isinstance(value, SettingsAttribute):
            self.attributes[name] = value
        else:
            self.attributes[name] = SettingsAttribute(value, priority)
    else:
        self.attributes[name].set(value, priority)
```

除了 *name(键)*，*value(值)* 两个参数外，还具有一个 *priority(优先级)* 参数。*value* 在存储到 *self.attributes* 属性中时，会被封装成 *SettingsAttribute* 对象，并将值的实际存储过程托管给 *SettingsAttribute* 类来处理：

```py
class SettingsAttribute:

    """Class for storing data related to settings attributes.

    This class is intended for internal usage, you should try Settings class
    for settings configuration, not this one.
    """

    def __init__(self, value, priority):
        self.value = value
        if isinstance(self.value, BaseSettings):
            self.priority = max(self.value.maxpriority(), priority)
        else:
            self.priority = priority

    def set(self, value, priority):
        """Sets value if priority is higher or equal than current priority."""
        if priority >= self.priority:
            if isinstance(self.value, BaseSettings):
                value = BaseSettings(value, priority=priority)
            self.value = value
            self.priority = priority

    ...
```

*SettingsAttribute* 类包含两个主要属性：
1. self.value：实际值
2. self.priority：优先级

*SettingsAttribute.set* 方法用于设置 *value* 属性，其同样具有一个 *priority* 参数。从该方法的实现逻辑可以看出，只有当 *priority >= self.priority*，即设置的值的优先级大于等于当前优先级时，*self.value* 属性值才会更新。这意味着对于 *BaseSettings* 类，如果两个相同名称的配置在加载时，只有优先级高的值才会被实际存储，低优先级的值无法覆盖高优先级的值。

优先级的可选值(字符串)位于模块的 *SETTINGS_PRIORITIES* 属性中：

```py
SETTINGS_PRIORITIES = {
    'default': 0,
    'command': 10,
    'project': 20,
    'spider': 30,
    'cmdline': 40,
}
```

需要注意的是，*BaseSettings* 在使用 *set* 方法时，*priority* 参数的值不单是可以使用上述字符串，还支持直接使用数字。

```py
def get_settings_priority(priority):
    if isinstance(priority, str):
        return SETTINGS_PRIORITIES[priority]
    else:
        return priority
```

除了 *get*, *set*, *update* 这几个关键方法，*BaseSettings* 还提供了 *setmodule* 方法通过 **动态导入(import_module)** 从模块中加载配置参数，即项目配置模块(settings.py)的加载逻辑：

```py
def setmodule(self, module, priority='project'):
    # 检测对象是否冻结(self.frozen)
    self._assert_mutability()
    # 动态导入目标模块
    if isinstance(module, str):
        module = import_module(module)
    # 遍历模块属性并加载配置
    for key in dir(module):
        # 只有全大写的属性名才会被加载
        if key.isupper():
            self.set(key, getattr(module, key), priority)

```

同时还额外提供了一些方法用于在获取值时进行类型转换：
 * getbool(): 布尔类型
 * getint(): 整型
 * getfloat(): 浮点数
 * getlist(): 列表
 * getdict(): 字典


### 2.4. 配置加载流程分析

在理解了 *settings* 对象的内部结构后，现在来分析其完整加载流程以及优先级机制在其中的作用，看看不同的配置源中相同的配置之间是如何覆盖的。下述讨论基于 *crwal* 命令。

1. **project** 优先级：
 
*settings* 对象的实例化位于 ***scrapy.cmdline*** 的 *execute* 方法中：
```py
def execute(argv=None, settings=None):
    ...
    if settings is None:
        settings = get_project_settings()
    ...
    settings.setdict(cmd.default_settings, priority='command')
    ...
    cmd.crawler_process = CrawlerProcess(settings)
    ...
```
当 *settings* 参数为 None 时，会通过 *get_project_settings* 函数创建：
```py
def get_project_settings():
    ...
    settings = Settings()
    settings_module_path = os.environ.get(ENVVAR)
    if settings_module_path:
        settings.setmodule(settings_module_path, priority='project')
    ...
```
此时加载的配置是由项目配置模块 *settings.py* 提供的(具体以 *scrapy.cfg* 中的配置为准)，且具有 *project* 优先级。

2. **command** 优先级：

*execute* 方法同时会将 *cmd.default_settings* 中的配置进行合并，*default_settings* 是在 *ScrapyCommand* 子类中定义的配置，需要注意的是，该配置具有 *command* 优先级，由于该配置优先级低于 *project*，因此对于相同的配置，*settings.py* 模块中的配置不会被覆盖。 
```py
def execute(argv=None, settings=None):
    ...
    settings.setdict(cmd.default_settings, priority='command')
    ...
```

3. **cmdline** 优先级：

在使用 *crawl* 等命令时，还可以通过 *-s* 参数添加额外的配置，此时的配置具有 *cmdline* 优先级，这是字符串类型的优先级中最高的，将覆盖 *settings* 对象中的相同配置。该配置的加载位置位于 ***scrapy.commands.ScrapyCommand*** 类的 *process_options* 方法中。
```py
def process_options(self, args, opts):
    try:
        self.settings.setdict(arglist_to_dict(opts.set), priority='cmdline')
    except ValueError:
        raise UsageError("Invalid -s value, use -s NAME=VALUE", print_help=False)
    ...
```

4. **spider** 优先级：

**spider** 优先级的配置是在 *scrapy.spiders.Spider(爬虫类)* 中定义的 *custom_settings* 属性，并通过 *update_settings* 方法加载。
```py
class Spider(object_ref):

    name = None
    custom_settings = None

    ...

    @classmethod
    def update_settings(cls, settings):
        settings.setdict(cls.custom_settings or {}, priority='spider')

    ...
```
由于 *priority(spider>project)* 因此，项目配置模块中的同名配置将被爬虫类属性中的配置覆盖。

上述就是 *crawl* 命令启动爬虫时，所有优先级配置的加载流程:
  1. **cmdline**：*crawl* 命令的 *-s* 参数设置的配置具有最高优先级 。
  2. **spider**：*Spider* 类中的 *custom_settings* 配置属性具有第二优先级。
  3. **project**：*settings.py* 模块中的配置具有 *project* 优先级，该优先级低于 *spider* 优先级，因此同名配置将被 *Spider.custom_settings* 覆盖。
  4. **command**：具有除 **default** 外的最低优先级。一般在自定义命令工具中使用。

-------------------------------------------------------
## 3. 总结

**scrapy.settings** 模块是 *scrapy* 框架实现配置化的核心组件。其中 **scrapy.settings.BaseSettings** 类作为配置容器用于存储框架运行所需的配置参数，并通过一种优先级机制，来处理从多个源加载的相同配置的不同优先级之间的覆盖问题。*scrapy* 框架在运行时，会通过这些配置参数来控制组件的行为，从而实现配置化的自定义运行。

关于具体的配置如果实际影响 *scrapy* 框架的行为，一般是通过配置参数来运行不同的代码段，但是还有一类 “特殊” 的配置，这类配置一般是通过指定一个 **类的字符串**，例如 *DUPEFILTER_CLASS = "scrapy.dupefilters.RFPDupeFilter"*，框架对这些配置有一套额外的处理机制，该机制的具体讨论在后续的文章中进行研究。

从该技术节点中可以衍生出两个新节点:
1. [Scrapy-配置化机制-框架配置参数解析](../框架配置参数解析/Scrapy-配置化机制-框架配置参数解析.md)：讨论具体的配置参数如何实际的影响框架的运行行为。
2. [Scrapy-配置化机制-对象加载机制研究](../对象加载机制研究/Scrapy-配置化机制-对象加载机制研究.md)：研究框架是如果通过配置来动态地加载类并构建其实例。

