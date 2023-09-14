# Scrapy-配置化机制-对象加载机制研究

-------------------------------------------------------
## 1. 概述
*Scrapy* 框架通过配置参数来控制其运行状态和行为，其中有一类特殊的配置参数，通过指定一个 *类名字符串* 来替换框架中的组件，本文主要讨论该配置中指定的类的对象加载机制。

### Index
- [Scrapy-配置化机制-对象加载机制研究](#scrapy-配置化机制-对象加载机制研究)
  - [1. 概述](#1-概述)
    - [Index](#index)
    - [Meta](#meta)
  - [2. 机制分析](#2-机制分析)
  - [3. 总结](#3-总结)

### Meta
```json
{
    "node": "8E3D465E-9770-4FEC-932A-FEC2EA97EC3A",
    "name": "Scrapy-配置化机制-对象加载机制研究",
    "author": "Ais",
    "date": "2023-09-07",
    "tag": ["数据采集", "scrapy", "配置化机制", "Settings", "importlib", "动态加载"]
}
```

-------------------------------------------------------
## 2. 机制分析
在 *scrapy* 的默认项目配置 **scrapy.settings.default_settings** 中，可以看到部分配置参数指定的是一个 *类名字符串*：

```py
...
DOWNLOADER = 'scrapy.core.downloader.Downloader'
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'
ITEM_PROCESSOR = 'scrapy.pipelines.ItemPipelineManager'
...
```

下面以常见的去重器配置 *DUPEFILTER_CLASS* 来研究其对象的加载机制。

通过在源码中搜索相关字符串，可以定位到 *DUPEFILTER_CLASS* 配置的应用位置，其位于 **scrapy.core.scheduler.Scheduler** 类的 *from_crawler* 类方法中：

```py
# scrapy.core.scheduler
class Scheduler:
    
    ...

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        dupefilter_cls = load_object(settings['DUPEFILTER_CLASS'])
        dupefilter = create_instance(dupefilter_cls, settings, crawler)
        ...
```

可以看到，上述源码中包含两个关键函数 **load_object** 和 **create_instance**。这两个函数的源码都位于 **scrapy.utils.misc** 模块中。

```py
# scrapy.utils.misc
def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be the import path of a class, function, variable or an
    instance, e.g. 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    try:
        # rindex 函数会获取 "." 所在的最后位置，'scrapy.dupefilters.RFPDupeFilter'.rindex(".") -> 18, 当未包含 "." 字符时将抛出异常。
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    # 解析模块名和类/对象名: module(scrapy.dupefilters), name(RFPDupeFilter)
    module, name = path[:dot], path[dot + 1:]
    # 动态导入模块
    mod = import_module(module)

    try:
        # 在导入的模块中获取指定类/对象
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj
```

*load_object* 函数的实现逻辑很简单，通过 *path* 参数指定的字符串，使用 *import_module(动态导入)* 和 *getattr(查找属性)* 动态地导入类或者对象。

```py
# scrapy.utils.misc
def create_instance(objcls, settings, crawler, *args, **kwargs):
    """Construct a class instance using its ``from_crawler`` or
    ``from_settings`` constructors, if available.

    At least one of ``settings`` and ``crawler`` needs to be different from
    ``None``. If ``settings `` is ``None``, ``crawler.settings`` will be used.
    If ``crawler`` is ``None``, only the ``from_settings`` constructor will be
    tried.

    ``*args`` and ``**kwargs`` are forwarded to the constructors.

    Raises ``ValueError`` if both ``settings`` and ``crawler`` are ``None``.

    .. versionchanged:: 2.2
       Raises ``TypeError`` if the resulting instance is ``None`` (e.g. if an
       extension has not been implemented correctly).
    """
    if settings is None:
        if crawler is None:
            raise ValueError("Specify at least one of settings and crawler.")
        settings = crawler.settings
    # 当 crawler 不为空，使用类的 from_crawler 方法创建实例
    if crawler and hasattr(objcls, 'from_crawler'):
        instance = objcls.from_crawler(crawler, *args, **kwargs)
        method_name = 'from_crawler'
    # 使用类的 from_settings 方法创建实例
    elif hasattr(objcls, 'from_settings'):
        instance = objcls.from_settings(settings, *args, **kwargs)
        method_name = 'from_settings'
    # 传统方法创建实例
    else:
        instance = objcls(*args, **kwargs)
        method_name = '__new__'
    if instance is None:
        raise TypeError("%s.%s returned None" % (objcls.__qualname__, method_name))
    return instance
```

*create_instance* 函数则是使用 *hasattr* 通过查找 objcls(类对象) 是否具有 *from_crawler* 和 *from_settings* 方法来创建其实例。可以看到，如果 objcls 实现了 *from_crawler* 和 *from_settings* 方法则优先采用这两个方法来构建实例，否则采用传统的实例化方法。

同时从上述逻辑中，也可以看到 *scrapy* 的一些框架组件中定义  *from_crawler* 或者 *from_settings* 类方法的原因。这里涉及到另外一个问题 —— 组件实例初始化参数的加载和传递问题。设想这样一个场景，有一个自定义的组件 *Component* 需要在实例化的时候传入一些初始化参数，但是实例化是由框架完成的，无法主动传入参数，因此可以通过添加 *from_crawler* 或者 *from_settings* 方法来实现：

```py
class Component(object):

    def __init__(self, param_a, param_b):
        self.param_a = param_a
        self.param_b = param_b

    @classmethod
    def from_settings(cls, settings):
        param_a = settings.get('COMPONENT_PARAM_A')
        param_b = settings.get('COMPONENT_PARAM_B')
        return cls(param_a, param_b)
    
    ...
```

通过在 settings.py 中配置相关参数来实现组件实例化时初始化参数的加载。

-------------------------------------------------------
## 3. 总结

*scrapy* 框架的对象加载机制通过 *load_object* 和 *create_instance* 的组合使用，来从配置参数中动态地导入模块并进行类的实例化，其核心实现是基于 *动态导入机制(importlib.import_module)* 和 *自省机制(getattr,hasattr)*。这种对象加载机制使框架的扩展性得到了很大地增强，以实现通过自定义组件的替换来契合具体的应用场景。



