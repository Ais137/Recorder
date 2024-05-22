# Python中的内省与反射机制及其应用场景

-------------------------------------------------------
## 1. 概述
> 在计算机学中，反射式编程（英语：reflective programming）或反射（英语：reflection），是指计算机程序在运行时（runtime）可以访问、检测和修改它本身状态或行为的一种能力。用比喻来说，反射就是程序在运行的时候能够“观察”并且修改自己的行为。  
>   
> 要注意术语“反射”和“内省”（type introspection）的关系。内省（或称“自省”）机制仅指程序在运行时对自身信息（称为元数据）的检测；反射机制不仅包括要能在运行时对程序自身信息进行检测，还要求程序能进一步根据这些信息改变程序状态或结构。  
> 
> —— wikipedia

*python* 提供了一套灵活的机制来实现内省和反射功能，让程序可以在运行时动态地修改其状态和行为，用来构建灵活的可扩展的模块和框架，本文主要讨论其基本用法及具体应用场景。

* [Python中的内省与反射机制及其应用场景](#python中的内省与反射机制及其应用场景)
    * [1. 概述](#1-概述)
    * [2. 基本用法](#2-基本用法)
        * [2.1. 内置函数](#21-内置函数)
        * [2.2. 特殊属性](#22-特殊属性)
        * [2.3. inspect模块](#23-inspect模块)
            * [2.3.1. 获取成员](#231-获取成员)
            * [2.3.2. 获取源代码](#232-获取源代码)
            * [2.3.3. 类型注解](#233-类型注解)
            * [2.3.4. 类与函数和调用堆栈](#234-类与函数和调用堆栈)
    * [3. 应用场景](#3-应用场景)
        * [3.1. 鸭子类型概念及应用](#31-鸭子类型概念及应用)
        * [3.2. 可扩展数据提取器设计](#32-可扩展数据提取器设计)
        * [3.3. 简单工厂模式扩展性优化](#33-简单工厂模式扩展性优化)
        * [3.4. 运行时参数类型校验](#34-运行时参数类型校验)
        * [3.5. 基于参数签名进行子函数的自动调用](#35-基于参数签名进行子函数的自动调用)
        * [3.6. 文档自动生成](#36-文档自动生成)
    * [4. 总结](#4-总结)
    * [5. 参考](#5-参考)


-------------------------------------------------------
## 2. 基本用法

### 2.1. 内置函数

*内省* 是 *反射式编程* 的基础，在 *python* 中接触到的最常见的相关函数一般是 *dir* 和 *type* 这两个内置函数。 

*dir* 函数在交互式命令行中使用比较频繁，通常用来查看指定模块或对象的属性和方法。

```py
>>> import path
>>> dir(path)
['CaseInsensitivePattern', 'ClassProperty', 'DirectoryNotEmpty', 'FastPath', 'LINESEPS', 'Multi', 'NEWLINE', 'NL_END', 'Path', 'SpecialResolver', 
'TempDir', 'TreeWalkWarning', 'U_LINESEPS', 'U_NEWLINE', 'U_NL_END', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_multi_permission_mask', '_permission_mask', 'compose', 'contextlib', 'errno', 'fnmatch', 'functools', 'glob', 'hashlib', 'importlib', 'io', 'itertools', 'matchers', 'metadata', 'multimethod', 'only_newer', 'operator', 'os', 're', 'shutil', 'simple_cache', 'sys', 'tempdir', 'tempfile', 'warnings', 'win32security']
>>> dir({})
['__class__', '__contains__', '__delattr__', '__delitem__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', 'clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values']
```

*type* 函数则用于动态构建类，但其最常用的用法是 `type(object)`，指定一个对象，返回一个 *type* 对象，可以用该函数来快速查看对象的类型信息。

```py
>>> type({})
<class 'dict'>
```

除了这两个函数外，*python* 还提供了以下与 *内省* 和 *反射* 机制相关的内置函数。

| 函数 | 定义 | 功能 |
| :----: | ---- | ---- |
| **hasatter** | *hasattr(object, name)* | 检查 object 中是否具有 {name} 属性 |
| **getatter** | *getattr(object, name, default)* | 获取 object 的 {name} 属性，当属性不存在时抛出 AttributeError 异常或者返回 default 默认值 | 
| **setattr** | *setattr(object, name, value)* | 更新 object 属性 |
| **delattr** | *delattr(object, name)* | 删除 object 属性 |
| **isinstance** | *isinstance(object, classinfo)* | 判断 object 是否是 {classinfo} 的(直接，间接，虚拟) 子类实例，相比于 type 会考虑继承关系。|
| **issubclass** | *issubclass(class, classinfo)* | 判断 class 是否是 {classinfo} 的子类(直接，间接，虚拟) |
| **globals** | *globals()* | 返回实现当前模块命名空间的字典。对于函数内的代码，这是在定义函数时设置的，无论函数在哪里被调用都保持不变。|
| **locals** | *locals()* | 更新并返回表示当前本地符号表的字典。 在函数代码块但不是类代码块中调用 locals() 时将返回自由变量。|
| **vars** | *vars(object)* | 返回模块、类、实例或任何其它具有 __dict__ 属性的对象的 __dict__ 属性。|

上述内置函数的完整用法参考官方文档 [内置函数](https://docs.python.org/zh-cn/3/library/functions.html)。


### 2.2. 特殊属性
除了内置函数外，python 还支持通过一些 *特殊属性* 来进行 *内省*，这些特殊属性通常以 *\_\_xxx\_\_* 的形式存在。

一个最常见的属性是 ***\_\_name\_\_***，用于存储 类、函数、方法、描述器或生成器实例的名称。

```py
class A(object):

    def __init__(self):
        self.data = ""
        self.__source = ""
        
    def test(self):
        return self.__class__.__name__

class B(object):
    pass

class C(A, B):
    pass

class D(C):
    pass

print(D().test())  
# D
print(D().test.__name__)
# test
print(D().test.__qualname__)
# A.test
```

类似的 ***\_\_qualname\_\_*** 属性用于存储 *限定名称*，详细定义参考 [PEP-3155](https://peps.python.org/pep-3155/)。

另一个常见的特殊属性是 ***\_\_dict\_\_***，这是一个字典或其他类型的映射对象，用于存储对象的（可写）属性。

```py
print(A().__dict__)
# {'data': '', '_A__source': ''}

print(A.__dict__)
# {'__module__': '__main__', '__init__': <function A.__init__ at 0x000002DCFE547B80>, 'test': <function A.test at 0x000002DCFE547C10>, '__dict__': <attribute '__dict__' of 'A' objects>, '__weakref__': <attribute '__weakref__' of 'A' objects>, '__doc__': None}

print(dir(A))
# ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'test']
```

要获取对象所属的类信息可以通过 ***\_\_class\_\_*** 属性，该属性是一个 *\<class 'type'\>* 对象。

```py
obj = D()
print(obj.__class__)
# <class '__main__.D'>

type(obj.__class__)
# <class 'type'>

new_obj = obj.__class__()
print(new_obj.__class__)
# <class '__main__.D'>
```

***\_\_bases\_\_*** 是一个元组，其存储了类对象的基类。

```py
print(D.__bases__)
# (<class '__main__.C'>,)
print(C.__bases__)
# (<class '__main__.A'>, <class '__main__.B'>)
```

可以通过对该属性进行递归遍历来获取指定类的 *继承链*：

```py
def DFS(cls):
    [(print(c), DFS(c)) for c in cls.__bases__]

DFS(D)
# <class '__main__.C'>
# <class '__main__.A'>
# <class 'object'>    
# <class '__main__.B'>
# <class 'object'> 
```

另一个更好的方式是直接使用 ***\_\_mro\_\_*** ，该属性是类组成的元组，用于描述方法解析顺序。**MRO(Method Resolution Order/方法解析顺序)** 的定义参考 [MRO](https://www.python.org/download/releases/2.3/mro/)。

```py
print(D.__mro__)
# (<class '__main__.D'>, <class '__main__.C'>, <class '__main__.A'>, <class '__main__.B'>, <class 'object'>)
```

除了获取类的基类信息，还可以通过 ***\_\_subclasses\_\_*** 方法来获取直接子类的弱引用列表。

```py
print(A.__subclasses__())
# [<class '__main__.C'>]
```

**特殊属性** 的官方文档参考 [Python特殊属性](https://docs.python.org/zh-cn/3/library/stdtypes.html?highlight=__name__#special-attributes)

### 2.3. inspect模块

*内置函数* 和 *特殊属性* 提供了对类和对象的一些基本内省功能，Python标准库中的 **inspect** 模块则提供了更为完善和强大的方法来实现内省机制。

> inspect 模块提供了一些有用的函数帮助获取对象的信息，例如模块、类、方法、函数、回溯、帧对象以及代码对象。例如它可以帮助你检查类的内容，获取某个方法的源代码，取得并格式化某个函数的参数列表，或者获取你需要显示的回溯的详细信息。
>
> 该模块提供了4种主要的功能：类型检查、获取源代码、检查类与函数、检查解释器的调用堆栈。

上述是 *inspect* 模块的官方文档描述。接下来了解一下具体的使用方法。

#### 2.3.1. 获取成员

**inspect.getmembers** 函数用于返回一个对象上的所有成员，其返回值是一个键值对为元素的列表。

```py
import inspect

class Test():

    def __init__(self):
        self.data = {}
        self.path = ""

    def test(self):
        pass

print(inspect.getmembers(Test()))
# [('__class__', <class '__main__.Test'>), ('__delattr__', <method-wrapper '__delattr__' of Test object at 0x0000020A150AFBB0>), ('__dict__', {'data': {}, 'path': ''}), ('__dir__', <built-in method __dir__ of Test object at 0x0000020A150AFBB0>), ('__doc__', None), ('__eq__', <method-wrapper '__eq__' of Test object at 0x0000020A150AFBB0>), ('__format__', <built-in method __format__ of Test object at 0x0000020A150AFBB0>), ('__ge__', <method-wrapper '__ge__' of Test object at 0x0000020A150AFBB0>), ('__getattribute__', <method-wrapper '__getattribute__' of Test object at 0x0000020A150AFBB0>), ('__gt__', <method-wrapper '__gt__' of Test object at 0x0000020A150AFBB0>), ('__hash__', <method-wrapper '__hash__' of Test object at 0x0000020A150AFBB0>), ('__init__', <bound method Test.__init__ of <__main__.Test object at 0x0000020A150AFBB0>>), ('__init_subclass__', <built-in method __init_subclass__ of type object at 0x0000020A151EB210>), ('__le__', <method-wrapper '__le__' of Test object at 0x0000020A150AFBB0>), ('__lt__', <method-wrapper '__lt__' of Test object at 0x0000020A150AFBB0>), ('__module__', '__main__'), ('__ne__', <method-wrapper '__ne__' of Test object at 0x0000020A150AFBB0>), ('__new__', <built-in method __new__ of type object at 0x00007FF80544CB50>), ('__reduce__', <built-in method __reduce__ of Test object at 0x0000020A150AFBB0>), ('__reduce_ex__', <built-in method __reduce_ex__ of Test object at 0x0000020A150AFBB0>), ('__repr__', <method-wrapper '__repr__' of Test object at 0x0000020A150AFBB0>), ('__setattr__', <method-wrapper '__setattr__' of Test object at 0x0000020A150AFBB0>), ('__sizeof__', <built-in method __sizeof__ of Test object at 0x0000020A150AFBB0>), ('__str__', <method-wrapper '__str__' of Test object at 0x0000020A150AFBB0>), ('__subclasshook__', <built-in method __subclasshook__ of type object at 0x0000020A151EB210>), ('__weakref__', None), ('data', {}), ('path', ''), ('test', <bound method Test.test of <__main__.Test object at 0x0000020A150AFBB0>>)]
```

通过可选参数 *predicate* 可以筛选指定的成员，比如获取 *inspect* 模块中以 *is* 开头的 *函数* 成员：

```py
import inspect
print(inspect.getmembers(
    inspect, 
    predicate = lambda obj: inspect.isfunction(obj) and obj.__name__.startswith("is") 
))
# [('isabstract', <function isabstract at 0x0000015547068550>), ('isasyncgen', <function isasyncgen at 0x0000015547068040>), ('isasyncgenfunction', <function isasyncgenfunction at 0x0000015547065F70>), ('isawaitable', <function isawaitable at 0x00000155470681F0>), ('isbuiltin', <function isbuiltin at 0x0000015547068430>), ('isclass', <function isclass at 0x0000015547027940>), ('iscode', <function iscode at 0x00000155470683A0>), ('iscoroutine', <function iscoroutine at 0x0000015547068160>), ('iscoroutinefunction', <function iscoroutinefunction at 0x0000015547065EE0>), ('isdatadescriptor', <function isdatadescriptor at 0x0000015547065B80>), ('isframe', <function isframe at 0x0000015547068310>), ('isfunction', <function isfunction at 0x0000015547065D30>), ('isgenerator', <function isgenerator at 0x00000155470680D0>), ('isgeneratorfunction', <function isgeneratorfunction at 0x0000015547065E50>), ('isgetsetdescriptor', <function isgetsetdescriptor at 0x0000015547065CA0>), ('ismemberdescriptor', <function ismemberdescriptor at 0x0000015547065C10>), ('ismethod', <function ismethod at 0x0000015547065A60>), ('ismethoddescriptor', <function ismethoddescriptor at 0x0000015547065AF0>), ('ismodule', <function ismodule at 0x0000015546FE39D0>), ('isroutine', <function isroutine at 0x00000155470684C0>), ('istraceback', <function istraceback at 0x0000015547068280>)]
```

*inspect* 模块提供了一系列以 *is* 开头的函数，用于对对象的类型进行校验，需要注意的是，这里的 *类型* 指的是更抽象的层面，而非对象的 *class* 类型。

| 函数 | 定义 | 功能 |
| :----: | ---- | ---- |
| **inspect.ismodule** | *inspect.ismodule(object)* | 当该对象是一个模块时返回 True。|
| **inspect.isclass** | *inspect.isclass(object)* | 当该对象是一个类时返回 True，无论是内置类或者 Python 代码中定义的类。|
| **inspect.ismethod** | *inspect.ismethod(object)* | 当该对象是一个 Python 写成的绑定方法时返回 True。|
| **inspect.isfunction** | *inspect.isfunction(object)* | 当该对象是一个 Python 函数时（包括使用 lambda 表达式创造的函数），返回 True。|
| ...... | ...... | ...... |

来分析一下 **inspect.getmembers** 函数的源码实现：

```py
def getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    # 判断 object 是否是一个类并返回其 __mro__ 属性，该属性包含了 object 的继承链上的所有类对象。
    if isclass(object):
        # getmro -> cls.__mro__
        mro = (object,) + getmro(object)
    else:
        mro = ()
    # 存储结果
    results = []
    # 处理结果去重集
    processed = set()
    # 获取 object 的成员名
    names = dir(object)
    # :dd any DynamicClassAttributes to the list of names if object is a class;
    # this may result in duplicate entries if, for example, a virtual
    # attribute with the same name as a DynamicClassAttribute exists
    try:
        # 遍历 object 基类中的成员
        for base in object.__bases__:
            for k, v in base.__dict__.items():
                # 查找 types.DynamicClassAttribute 装饰的属性，与 property 装饰的属性在访问行为上有差异，具体详见 https://docs.python.org/zh-cn/3/library/types.html
                if isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    except AttributeError:
        pass
    for key in names:
        # First try to get the value via getattr.  Some descriptors don't
        # like calling their __get__ (see bug #1785), so fall back to
        # looking in the __dict__.
        try:
            # 优先通过 getattr 函数获取成员
            value = getattr(object, key)
            # handle the duplicate key
            if key in processed:
                raise AttributeError
        except AttributeError:
            # 根据 MRO(方法解析顺序) 查找键名为 key 的成员
            for base in mro:
                if key in base.__dict__:
                    value = base.__dict__[key]
                    break
            else:
                # could be a (currently) missing slot member, or a buggy
                # __dir__; discard and move on
                continue
        # 根据 predicate 参数过滤结果，predicate 是一个可调用对象
        if not predicate or predicate(value):
            results.append((key, value))
        processed.add(key)
    # 将结果安装首字母排序
    results.sort(key=lambda pair: pair[0])
    return results
```

通过上述源码可以看到，**inspect.getmembers** 函数并没有实现新的内省机制，而是基于前述的 *内置函数* 和 *特殊属性* 进行组合实现的。

#### 2.3.2. 获取源代码

*inspect* 模块还提供了一系列方法来获取源代码相关的信息。

*inspect.getdoc* 函数用于获取对象的 *文档字符串*。*文档字符串* 是python中的一个特殊机制，其官方描述如下：
> docstring -- 文档字符串
> 
> 作为类、函数或模块之内的第一个表达式出现的字符串字面值。它在代码执行时会被忽略，但会被解释器识别并放入所在类、函数或模块的 \_\_doc\_\_ 属性中。由于它可用于代码内省，因此是对象存放文档的规范位置。

```py
class Test(object):
    """
    测试类
    """

    def test(self, data: dict) -> bool:
        """测试方法
        
        对指定数据进行测试并返回测试结果的真值。

        Args:
            data(dict): 测试数据

        Returns:
            (bool) 测试结果
        """ 
        pass

import inspect
print(inspect.getdoc(Test))
# 测试类
print(inspect.getdoc(Test.test))
# 测试方法
#
# 对指定数据进行测试并返回测试结果的真值。
#
# Args:
#     data(dict): 测试数据
#
# Returns:
#     (bool) 测试结果
```

*inspect.getmodule* 尝试猜测一个对象是在哪个模块中定义的。 如果无法确定模块则返回 None。

```py
print(inspect.getmodule(Test))
# <module '__main__' from '.\\test.py'>
```

*inspect.getsourcelines* 函数用于返回对象的源代码文本。

```py
print(inspect.getsource(Test.test))
"""
    def test(self, data: dict) -> bool:
        """测试方法

        对指定数据进行测试并返回测试结果的真值。

        Args:
            data(dict): 测试数据

        Returns:
            (bool) 测试结果
        """
        pass
"""
```

其他相关函数参考官方文档 [获取源代码](https://docs.python.org/zh-cn/3/library/inspect.html?highlight=inspect#retrieving-source-code)。

#### 2.3.3. 类型注解

python采用动态类型的设计，使其具有很强的灵活性，但在某些特定场景下，缺失类型信息也为开发和调试带来了麻烦，随着 Python 语言的持续发展，经过一系列的 PEP 提案，为 python 增加了 *类型注解* 的功能。其官方文档描述如下：

> annotation -- 标注
> 
> 关联到某个变量、类属性、函数形参或返回值的标签，被约定作为 类型注解 来使用。
> 
> 局部变量的标注在运行时不可访问，但全局变量、类属性和函数的标注会分别存放模块、类和函数的 __annotations__ 特殊属性中。
> 
> 参见 variable annotation, function annotation, PEP 484 和 PEP 526，对此功能均有介绍。 另请参见 对象注解属性的最佳实践 了解使用标注的最佳实践。

类型注解通过类似元数据的方式来存储变量参数的类型信息，常见形式如下：

```py
def test(data: dict, save: bool = True) -> bool:
    pass
```

可以通过运行时获取对象的 *\_\_annotations\_\_* 特殊属性来查看：

```py
print(test.__annotations__)
# {'data': <class 'dict'>, 'save': <class 'bool'>, 'return': <class 'bool'>}
```

*inspect* 模块提供了 *signature* 函数来对可调用对象的调用签名和返回值标注进行内省。

```py
s = inspect.signature(test)
print(f'[parameters]({s.parameters.__class__}): {s.parameters}')
# [parameters](<class 'mappingproxy'>): OrderedDict([('data', <Parameter "data: dict">), ('save', <Parameter "save: bool = True">), ('kwargs', <Parameter "**kwargs">)])
print(f'[return_annotation]({s.return_annotation.__class__}): {s.return_annotation}')
# [return_annotation](<class 'type'>): <class 'bool'>
```

*inspect.signature* 函数接受 *可调用对象*，并返回一个 *inspect.Signature* 类的实例。*Signature* 对象具有两个主要属性：

  * *parameters*：一个有序字典，存储可调用对象的形式参数信息。
  * *return_annotation*：返回值类型注解

*parameters* 属性的值由 *inspect.Parameter* 类的实例构成，用于描述参数的完整信息，其主要由以下属性：

  * *name*：参数名字符串。
  * *default*：参数的默认值。
  * *annotation*：参数的类型注解。
  * *kind*：描述如何将值绑定到参数，位置参数还是关键字参数等。

```py
[print(f'[{key}]: {getattr(s.parameters["save"], key)}') for key in ["name", "default", "annotation", "kind"]]
# [name]: save
# [default]: True
# [annotation]: <class 'bool'>
# [kind]: 1
```

#### 2.3.4. 类与函数和调用堆栈

除了上述用法外，*inspect* 模块还支持检查类与函数和解释器的调用堆栈，但由于个人在这方面接触到的应用较少，就不在此详解了，*inspect* 模块的完整使用文档，参考官方文档 [inspect --- 检查对象](https://docs.python.org/zh-cn/3/library/inspect.html)


-------------------------------------------------------
## 3. 应用场景

在了解了 Python 中 **内省机制** 的基本用法后，结合具体的应用场景来看看如何实现反射式编程。

### 3.1. 鸭子类型概念及应用
> duck-typing -- 鸭子类型
> 
> 指一种编程风格，它并不依靠查找对象类型来确定其是否具有正确的接口，而是直接调用或使用其方法或属性（“看起来像鸭子，叫起来也像鸭子，那么肯定就是鸭子。”）由于强调接口而非特定类型，设计良好的代码可通过允许多态替代来提升灵活性。鸭子类型避免使用 type() 或 isinstance() 检测。(但要注意鸭子类型可以使用 抽象基类 作为补充。) 而往往会采用 hasattr() 检测或是 EAFP 编程。

鸭子类型强调的是对象的行为，其识别对象的类不是通过类型信息，而是通过对象支持的行为来的。当涉及对象之间的调用关系时，这种方式有很强的灵活性。

python中最常见的应用莫过于各类特殊的 **协议方法**，比如 **上下文管理器协议**。当一个对象实现了 ***\_\_enter\_\_*** 和 ***\_\_exit\_\_*** 方法，则该对象可以被当作一个 **上下文管理器** 被 *with* 调用：

```py
class Test(object):

    def __enter__(self):
        print(f'[{self.__class__.__name__}]: enter')
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(f'[{self.__class__.__name__}]: exit')

with Test() as t:
    pass

# [Test]: enter
# [Test]: exit
```

又或者可以通过实现 ***\_\_call\_\_*** 将一个自定义对象变成可调用对象：

```py
class Test(object):

    def __call__(self, data):
        print(f'[{self.__class__.__name__}]: {data}')

t = Test()
t("data")
# [Test]: data

print(callable(t))
# True
```

同时可以基于前述的内省机制实现自定义的特殊协议方法，比如实现一个自定义的 **可序列化协议**：

```py
import json

class Test(object):

    def __init__(self, data, path="./data"):
        self.data = data
        self.path = path

    # 可序列化协议
    def __serialize__(self) -> str:
        return f'{self.__class__.__name__}({json.dumps({"data": self.data, "path": self.path})})'

# 序列化
def serialize(obj):
    if hasattr(obj, "__serialize__"):
        return obj.__serialize__()
    else:
        raise Exception(f'obj({Test}) is not Serializable')
    
# 判断是否可序列化
def serializable(obj):
    return hasattr(obj, "__serialize__")

t = Test("data")
print(serialize(t))
# Test({"data": "data", "path": "./data"})
print(serializable(t))
# True
print(serialize(123))
# Exception: obj(<class '__main__.Test'>) is not Serializable
print(serializable(123))
# False
```

需要注意的是，应该避免使用 **\_\_xxx\_\_** 方法来实现自定义协议，因为在语言发展过程中，可能会在新特性中使用，从而导致冲突。

自定义对象在实现某些特性时，不需要去显示的继承特定类，而是实现特定方法，对应组件通过检查(内省)目标对象是否具有特定方法来进行调用，正是这种基于鸭子类型的设计，使自定义对象可以通过实现特殊协议方法与内置类型保持一定的一致性。同时也让开发变的更加灵活。

### 3.2. 可扩展数据提取器设计

给定一段文本数据(str)，需要通过一个 *数据提取器* 从该文本数据中提取出结构化的数据对象，常见的设计方法如下：

```py
class Extracter(object):

    def extract(self, data):
        return {
            "title": self.title(data),
            "context": self.context(data),
            "pubdate": self.pubdate(data)
        }
    
    def title(self, data):
        return f"{data}-title"
    
    def context(self, data):
        return f"{data}-context"
    
    def pubdate(self, data):
        return f"{data}-pubdate"
    

data = Extracter().extract("text")
print(data)
# {'title': 'text-title', 'context': 'text-context', 'pubdate': 'text-pubdate'}
```

当新增提取字段时，需要创建对应的提取方法并将其调用代码添加到 *extract* 方法中，这种设计的可扩展性较低，需要频繁的修改 *extract* 方法，因此可以考虑使用内省和反射来提高其扩展性：

```py
import inspect

class Extracter(object):

    def extract(self, data):
        return {
            extract_method_name.split("_", 1)[-1]: extract_method(data)
            for extract_method_name, extract_method in inspect.getmembers(self, inspect.ismethod)
            if extract_method_name.startswith("extract_")
        }

    def extract_title(self, data):
        return f"{data}-title"
    
    def extract_context(self, data):
        return f"{data}-context"
    
    def extract_pubdate(self, data):
        return f"{data}-pubdate"
    

data = Extracter().extract("text")
print(data)
# {'title': 'text-title', 'context': 'text-context', 'pubdate': 'text-pubdate'}
```

新的设计通过 *inspect.getmembers* 函数遍历对象中以 *extract_* 为前缀的方法来实现调用，当新增提取字段时，只需新增一个符合规则的方法即可，而不用修改 *extract* 方法。

### 3.3. 简单工厂模式扩展性优化

> 简单工厂模式(Simple Factory Pattern)：又称为静态工厂方法(Static Factory Method)模式，它属于类创建型模式。在简单工厂模式中，可以根据参数的不同返回不同类的实例。简单工厂模式专门定义一个类来负责创建其他类的实例，被创建的实例通常都具有共同的父类。

简单工厂模式的基本架构如下：

```py
from abc import ABCMeta, abstractmethod

# 产品基类
class Product(metaclass=ABCMeta):
    
    @abstractmethod
    def use(self):
        pass

# 产品A
class ConcreteProductA(Product):
    """A"""

    def use(self):
        print(f'[{self.__class__.__name__}]: use')

# 产品B
class ConcreteProductB(Product):
    """B"""

    def use(self):
        print(f'[{self.__class__.__name__}]: use')


# 工厂
class Factory(object):

    @staticmethod
    def create(product):
        if product == "A":
            return ConcreteProductA()
        elif product == "B":
            return ConcreteProductB()
        else:
            raise ValueError(f'unknown product({product})')
        

Factory.create("A").use()
# [ConcreteProductA]: use
Factory.create("B").use()
# [ConcreteProductB]: use
```

可以看到，当新增产品时，由于 *Factory.create* 中的映射采用硬编码的方式，因此需要对其进行修改，从而导致这种设计的扩展性较差，为了解决这个问题，考虑通过动态的方式来构建映射表：

```py
class Factory(object):

    @staticmethod
    def create(product):
        # 构建映射表
        products = {
            _cls.__doc__: _cls 
            for _cls in Product.__subclasses__()
            if _cls.__doc__ and _cls.__name__ != "Product"
        }
        return products[product]()


Factory.create("A").use()
# [ConcreteProductA]: use
Factory.create("B").use()
# [ConcreteProductB]: use
```

通过 *Product.\_\_subclasses\_\_()* 方法来获取 *Product* 的直接子类，并将产品类的文档字符串作为其键名来动态的构建映射表。通过这种方式，在新增产品类时，不用再修改 *Factory.create* 方法。需要注意的是，*\_\_subclasses\_\_* 方法返回的是直接子类的弱引用列表，如果是多次继承，需要采用递归的方式来获取所有子类，同时由于该方案未经过完整验证与测试，请谨慎用于生产环境。

### 3.4. 运行时参数类型校验

在某些场景下，可能需要对函数的实际参数类型进行校验，一般的方式是在函数中手动添加类型检查逻辑，但是得益于python的 *类型注解* 和 *内省机制*，可以通过一种 “自动化” 的方式进行：

```py
import inspect

# 类型校验器
def type_validator(func):
    # 提取函数签名
    s = inspect.signature(func)
    def type_verified_func(*args, **kwargs):
        # 遍历函数实际参数
        for param, val in s.bind(*args, **kwargs).arguments.items():
            # 通过函数签名中的类型注解对实际参数类型进行校验
            if not isinstance(val, s.parameters[param].annotation):
                raise TypeError(f'param({param}|{type(val)}) is not {s.parameters[param].annotation}')
        # 执行目标函数
        return func(*args, **kwargs)
    return type_verified_func


@type_validator
def test(data:dict, path:str, save:bool=True):
    print(f'data({data}), path({path}), save({save})')


test({"a": 111}, "aaa", save=False)
# data({'a': 111}), path(aaa), save(False)
test(111, "aaa")
# TypeError: param(data|<class 'int'>) is not <class 'dict'>
```

上述 *类型校验器* 的核心实现思路是通过 *inspect.signature* 函数提取目标函数的 *类型注解*，并在函数调用时与实际参数的类型进行对比实现的，需要注意的是，该方法需要依赖于函数的 *类型注解*，样例未考虑注解缺失的情况(可以考虑处理成 Any 类型)。

### 3.5. 基于参数签名进行子函数的自动调用

与 *类型校验器* 相近的一个应用，由于 python 未实现 *函数重载*，因此需要在函数中判断参数类型并进行不同的处理，这种场景同样可以通过 *类型注解* 来实现子函数的动态调用。

```py
import inspect

class SubFuncAutoCaller(object):

    def __init__(self):
        # 子函数映射表
        self.subfunc = {}

    def overload(self, subfunc):
        # 提取函数类型注解
        s = inspect.signature(subfunc)
        # 基于类型注解来生成参数签名
        params_signature = "|".join([t.annotation.__name__ for t in s.parameters.values()])
        self.subfunc[params_signature] = subfunc

    def __call__(self, *args):
        # 基于实参的参数签名进行子函数调用
        params_signature = "|".join([type(p).__name__ for p in args])
        return self.subfunc[params_signature](*args)
    

# 构建调用器
func = SubFuncAutoCaller()

@func.overload
def func_list(data: list):
    print(f'[func_list]: data({type(data)})')
    return data

@func.overload
def func_int(data: int):
    print(f'[func_int]: data({type(data)})')
    return [data]

@func.overload
def func_str(data: str):
    print(f'[func_str]: data({type(data)})')
    return [int(i) for i in  data.replace(" ", "").split(",")]

@func.overload
def func_dict(data: dict):
    print(f'[func_dict]: data({type(data)})')
    return list(data.values())

# 调用测试
print(func("1, 2, 3"))
# [func_str]: data(<class 'str'>)
# [1, 2, 3]
print(func([1, 2, 3]))
# [func_list]: data(<class 'list'>)
# [1, 2, 3]
print(func(1))
# [func_int]: data(<class 'int'>)
# [1]
print(func({"a": 1, "b": 2, "c": 3}))
# [func_dict]: data(<class 'dict'>)
# [1, 2, 3]
```

*SubFuncAutoCaller* 类的 *overload* 是一个装饰器，在对子函数进行装饰时，会提取函数的类型注解并构建一个参数签名做为内部映射表 *subfunc* 的键名。通过实现 *\_\_call\_\_* 让 *SubFuncAutoCaller* 的实例变成一个可调用对象，当该对象被调用时，通过生成实际参数的参数签名来从 *subfunc* 中获取目标函数，从而实现子函数的自动调用。

需要注意的是，上述原型样例只考虑了位置参数的情况，在实际应用时需要处理包含 *kwargs* 的场景。

### 3.6. 文档自动生成

通过 *inspect* 模块从源码中自动生成文档。

```py
import inspect

def doc_extracter(func):
    # 提取函数签名
    func_signature = inspect.signature(func)
    # 解析文档字符串
    doc = {
        "name": func.__name__,
        "desc": inspect.getdoc(func).strip(),
        "args": [
            (p.name, p.annotation.__name__, p.default)
            for p in func_signature.parameters.values()
        ], 
        "return": func_signature.return_annotation.__name__
    }
    doc_str = f'{doc["name"]}:\n'
    doc_str += f'Desc: {doc["desc"]}\n'
    doc_str += f'Args:\n'
    doc_str += "\n".join([
        f'  * {p[0]}({p[1]})' 
        if p[2] is inspect._empty 
        else f'  * {p[0]}({p[1]}): default({p[2]})'
        for p in doc["args"]
    ]) + "\n"
    doc_str += "Returns:\n"
    doc_str += f'    type({doc["return"]})'
    return doc_str

def test(data: dict, export: bool=False) -> bool:
    """
    对指定数据(data)进行测试，并返回测试结果的真值。
    """
    pass

print(doc_extracter(test))
# test:
# Desc: 对指定数据(data)进行测试，并返回测试结果的真值。
# Args:
#   * data(dict)
#   * export(bool): default(False)
# Returns:
#     type(bool)
```
可以基于该原型的思路构建完善的文档自动生成工具。

-------------------------------------------------------
## 4. 总结

通过上述的具体应用场景可以看到，基于 *内省机制* 的 *反射式编程*，可以让组件和模块在运行时采用一种动态的方式进行构建，从而使其具有更灵活的扩展性。但是需要注意的是，这种方式相对于传统方法可能导致程序运行的性能问题，需要开发者根据具体的应用场景在扩展性和性能需求之间进行平衡。

-------------------------------------------------------
## 5. 参考
* [Python官方文档 - 内置函数](https://docs.python.org/zh-cn/3/library/functions.html)
* [Python官方文档 - inspect模块](https://docs.python.org/zh-cn/3/library/inspect.html)
* [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
* [PEP 3107 – Function Annotations](https://peps.python.org/pep-3107/)
* [PEP 526 – Syntax for Variable Annotations](https://peps.python.org/pep-0526/)
* [PEP 3155 – Qualified name for classes and functions](https://peps.python.org/pep-3155/)
