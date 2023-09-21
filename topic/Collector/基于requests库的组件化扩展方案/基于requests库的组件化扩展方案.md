# 基于requests库的组件化扩展方案

-------------------------------------------------------
## 1. 概述

> Requests is an elegant and simple HTTP library for Python, built for human beings.

本文主要介绍一种基于 *requests* 库的组件化功能扩展方案，通过一个 **全局钩子系统** 来实现 **组件化** 的自定义功能扩展。完整代码详见 [requests_extender](./src/requests_extender.py)


- [基于requests库的组件化扩展方案](#基于requests库的组件化扩展方案)
    - [1. 概述](#1-概述)
    - [2. 问题场景](#2-问题场景)
    - [3. 原生钩子系统](#3-原生钩子系统)
    - [4. 组件化扩展方案](#4-组件化扩展方案)
        - [4.1. 关键函数](#41-关键函数)
        - [4.2. 核心设计](#42-核心设计)
        - [4.3. 扩展器设计](#43-扩展器设计)
        - [4.4. 其他功能](#44-其他功能)
    - [5. 测试样例](#5-测试样例)
    - [6. 总结](#6-总结)


* Meta
```json
{
    "node": "F40298BA-7E28-D52F-DEED-CFE8DD6428C8",
    "name": "基于requests库的组件化功能扩展方案",
    "author": "Ais",
    "date": "2023-09-21",
    "tag": ["collector", "requests", "钩子系统", "hook", "RequestsExtender"] 
}
```

-------------------------------------------------------
## 2. 问题场景

在基于 *requests* 库构建数据采集项目时，在某些场景下，需要对请求进行统一处理，比如添加特定请求头或代理参数等。又或者是在分析目标网站的API结构时，需要通过不同的请求参数来测试回传数据，并保存请求体和请求结果。因此需要一种方案来对原有的 *requests* 功能进行自定义的扩展，同时需要考虑扩展代码的复用性问题。

通常方案是对 *requests* 库进行简单的二次封装，并添加扩展处理逻辑来实现。但是这种方案的局限性在于扩展性较低的同时无法复用，针对不同的场景要进行重新封装。又或是通过库提供的钩子系统来进行功能扩展，但由于原有的钩子系统设计比较简单，因此无法适应复杂的需求场景。

为此考虑通过一个 **全局钩子系统** 来实现 **组件化** 的自定义功能扩展。

-------------------------------------------------------
## 3. 原生钩子系统

*requests* 库提供了一个原生的 **钩子系统** 用于进行简单的功能扩展，使用样例如下：

```py
import requests

# 扩展函数
def print_url(res, *args, **kwargs):
    print(res.url)

res = requests.get("https://www.python.org/", hooks={"response": print_url})
# https://www.python.org/
```

上述代码通过 *hooks* 参数在 *response* 事件上传注册了一个 *print_url* 函数。当 *response* 事件触发时，将调用 *print_url* 函数进行处理，具体的处理逻辑位于 ***requests.sessions.Session*** 的 *send* 方法中：

```py
# requests.sessions
class Session(SessionRedirectMixin):
    
    def send(self, request, **kwargs):
        ...
        hooks = request.hooks
        ...
        r = dispatch_hook("response", hooks, r, **kwargs)
        ...
```

其中 *hooks/request.hooks* 是 *PreparedRequest* 的实例属性。构建过程的相关逻辑如下：

```py
# requests.models
class PreparedRequest(RequestEncodingMixin, RequestHooksMixin):

    def __init__(self):
        # default_hooks 函数返回一个字典 -> {"response": []}
        self.hooks = default_hooks()

    def prepare_hooks(self, hooks):
        """Prepares the given hooks."""
        hooks = hooks or []
        # 遍历 hooks 并注册到钩子系统中的指定事件上
        for event in hooks:
            self.register_hook(event, hooks[event])


# requests.hooks
HOOKS = ["response"]
def default_hooks():
    return {event: [] for event in HOOKS}


# requests.models
class RequestHooksMixin:

    def register_hook(self, event, hook):
        """Properly register a hook."""
        # 校验事件类型的合法性
        if event not in self.hooks:
            raise ValueError(f'Unsupported event specified, with event name "{event}"')
        # 将 hook(可调用对象或者可迭代对象) 添加到 self.hooks[event] 的数组中
        if isinstance(hook, Callable):
            self.hooks[event].append(hook)
        elif hasattr(hook, "__iter__"):
            self.hooks[event].extend(h for h in hook if isinstance(h, Callable))
```

从上述构建逻辑可以看到，*request.hooks* 的最终结构如下：

```py
{
    "response": [func1, func2, func3, ...]
}
```

同时从 *RequestHooksMixin.register_hook* 的逻辑可以发现，通过 *Session.request* 传入的 *hooks* 参数，即可以支持可调用对象，也可以支持可迭代对象(只会处理其中的可调用对象)，同时 *event* 参数只支持 *response* 事件。

```py
res = requests.get(
    url = "https://www.python.org/", 
    hooks = {
        "response": [print_url, print_status]
    }
) 

res = requests.get(
    url = "https://www.python.org/", 
    hooks = {
        "request": add_headers,
        "response": print_url
    },
    proxies = {"https": "http://127.0.0.1:7890"},
) 
# ValueError: Unsupported event specified, with event name "request"
```

*dispatch_hook* 函数用于处理上述 *hooks* 变量，具体处理逻辑位于 ***requests.hooks*** 中：

```py
# r = dispatch_hook("response", hooks, r, **kwargs)

def dispatch_hook(key, hooks, hook_data, **kwargs):
    """Dispatches a hook dictionary on a given piece of data."""
    hooks = hooks or {}
    # 获取注册到 response 事件上的函数列表
    hooks = hooks.get(key)
    if hooks:
        if hasattr(hooks, '__call__'):
            hooks = [hooks]
        # 通过 函数列表(hooks["response"]) 依次处理 r(Response) 对象
        for hook in hooks:
            _hook_data = hook(hook_data, **kwargs)
            if _hook_data is not None:
                hook_data = _hook_data
    return hook_data
```

从上述源码逻辑可以看到原生钩子系统的局限性，其仅支持 *response* 事件，即请求调用后对其返回值进行处理，无法解决在请求之前进行统一处理的需求。

-------------------------------------------------------
## 4. 组件化扩展方案

由于原生钩子系统的局限性，通过构建一种 *组件化的扩展方案* 来解决两个核心问题：

  1. 解决在请求之前进行统一处理的需求。
  2. 通过组件化来实现不同场景下的复用问题。

核心实现思路是通过 **hook** requests库的 **关键函数** 来注入自定义代码，以实现组件化的可扩展功能。

### 4.1. 关键函数
*requests* 提供了一系列的函数来提供不同 *http* 方法的请求调用：

```py
# requests.api

def get(url, params=None, **kwargs):
    return request("get", url, params=params, **kwargs)

def post(url, data=None, json=None, **kwargs):
    return request("post", url, data=data, json=json, **kwargs)

def options(url, **kwargs):
    return request("options", url, **kwargs)
...
```

通过分析其源码实现可以发现，其内部逻辑都使用了 `requests.api.request` 函数，这正是要找的 **关键函数**，通过替换该函数就可以影响 *get*，*post* 等方法，而不需要单独对每个方法进行替换。

### 4.2. 核心设计

***RequestsExtender(requests扩展器)*** 的核心设计如下：

```py
class RequestsExtender(object):
    """requests扩展器

    基于 requests 库的组件化功能扩展方案
    """

    # 可注册事件
    HOOK_EVENTS: list = ["request", "response"]
    # 已注册扩展器
    extenders: dict = {event:[] for event in HOOK_EVENTS}
    # 原始请求方法(requests.api.request)
    source_request_method = None

    @staticmethod
    def register(extenders: dict):
        """注册扩展器

        注册扩展器到指定事件，基于 hook 增强原始请求方法(requests.api.request)
        """
        # 校验注册事件的合法性
        if set(extenders) - set(RequestsExtender.HOOK_EVENTS):
            raise ValueError(f'Unsupported event in extenders({list(extenders)})')
        # 注册扩展器
        [RequestsExtender.extenders[event].extend(_extenders) for event, _extenders in extenders.items()]
        # 固定原始请求方法
        if RequestsExtender.source_request_method is not None:
            return 
        RequestsExtender.source_request_method = requests.api.request
        # 请求扩展函数
        def request_extension(method, url, **kwargs):
            # 请求参数字典
            req = {"method": method, "url": url, "headers": {}, **kwargs}
            # [request]事件处理节点
            req = reduce(lambda req, extender: extender(req), [req, *RequestsExtender.extenders["request"]])
            # 调用原始请求方法
            res = RequestsExtender.source_request_method(req.pop("method"), req.pop("url"), **req)
            # [response]事件处理节点
            return reduce(lambda res, extender: extender(res), [res, *RequestsExtender.extenders["response"]])
        # hook 原始请求方法
        requests.api.request = request_extension
```

***register*** 方法是方案的核心实现逻辑，其主要流程如下：

1. 将 *register* 方法的实际调用参数 *extenders* 添加到 *RequestsExtender.extenders* 静态属性上，*RequestsExtender.extenders* 用于存储所有已注册的扩展器，其内部结构如下:

   ```py
   {
       "request": [extender1, extender2, ...],
       "response": [extender1, extender2, ...]
   }
   ```

   其中键名为扩展器注册的事件类型，可选的事件类型列表为：
     * request: 在请求调用之前执行
     * response: 在请求调用之后执行

2. 固定关键函数 *requests.api.request* 到 *RequestsExtender.source_request_method* 静态属性上，用于后续调用。

3. 构建 *request_extension(请求扩展函数)*，增加 *RequestsExtender.extenders* 的执行逻辑，根据扩展器注册的事件类型，在 *requests.api.request* 函数调用之前或之后进行扩展器的依次调用。

4. hook *requests.api.request* 函数，将其替换成 *request_extension*。

通过调用 *RequestsExtender.register* 来实现自定义的扩展功能：

```py
import requests

RequestsExtender.register({
    "request": [extender1, extender2, extender3],
    "response": [extender4, extender5, extender6]
})

requests.get("https://www.python.org/")
```

### 4.3. 扩展器设计

**extender(扩展器)** 采用组件化的设计，每个扩展器都是一个独立组件，用于实现特定的功能扩展需求，通过组合不同的扩展器来覆盖不同的应用场景。这种组件化的设计使其具有可复用的特性。扩展器的通常定义如下：

```py
# 扩展器
def extender(obj):
    return obj
```

*extender* 只有一个形式参数 *obj*，根据其注册事件类型的不同，调用时的实际参数也不同，当注册到 *request* 事件上时，obj(req) 是 *请求参数字典(dict)*，即通过 get，post 等函数传入的参数。当注册到 *response* 事件上时，obj(res) 是 *requests.api.request* 函数调用后的 *requests.Response* 实例，即请求响应对象。

*extender* 对 *obj* 进行处理后，需要返回 *obj* 或者一个同类型的对象，以供后续扩展器处理。

*extender* 被当成 **Callable(可调用)** 对象进行处理，这意味着除了上述通常的函数定义方式外，还支持其他形式，当扩展器需要在调用过程中引用额外参数，又或是需要保存中间状态时，可以考虑以下实现：

```py
import os

class SaveResponseExtender(object):

    def __init__(self, path):
        self.path = path
        not os.path.exists(self.path) and os.makedirs(self.path)

    def __call__(self, res):
        filepath = os.path.join(self.path, f'{urlparse(res.url).hostname}.html')
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(res.text)
        return res

extender = SaveResponseExtender("./reqflow")
RequestsExtender.register({
  "response": [extender]
})
```

通过实现 *\_\_call\_\_* 方法，让实例变成可调用对象，除了上述方法，也可以利用 **闭包** 来简化实现：

```py
def save_response_extender(path):
    not os.path.exists(path) and os.makedirs(path)
    def extender(res):
        filepath = os.path.join(path, f'{urlparse(res.url).hostname}.html')
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(res.text)
        return res
    return extender

RequestsExtender.register({
    "response": [save_response_extender("./reqflow")]
})
```

### 4.4. 其他功能

除了上述核心功能外，*RequestsExtender* 还提供了一个 *domain_filter* 方法用来为扩展器指定允许处理的域名列表，当启用时其他域名的请求将被过滤，用于限制扩展器的作用范围。

```py
@staticmethod
def domain_filter(extender, allow_domain:list=None, ignore_domain:list=None):
    """域名过滤器

    为扩展器指定允许处理的域名列表，其他域名的请求将被过滤。
    """
    def domain_filter_extender(data):
        url = data["url"] if isinstance(data, dict) else data.url
        domain = urlparse(url).hostname
        if allow_domain and domain not in allow_domain:
            return data
        if ignore_domain and domain in ignore_domain:
            return data
        return extender(data)
    return domain_filter_extender

# 当前扩展器只处理 www.python.org 域名下的请求
RequestsExtender.domain_filter(extender, allow_domain=["www.python.org"])
```

-------------------------------------------------------
## 5. 测试样例

```py
import os
from requests_extender import RequestsExtender


def disp_request_extender(req):
    """显示请求"""
    print(f'[disp_request_extender]: {req}')
    return req

def save_response_extender(path):
    """保存响应数据"""
    not os.path.exists(path) and os.makedirs(path)
    def extender(res):
        filepath = os.path.join(path, f'{urlparse(res.url).hostname}.html')
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(res.text)
        print(f'[save_response_extender]: save({res.url})')
        return res
    return extender

# 注册扩展器
RequestsExtender.register({
    "request": [
        RequestsExtender.request_templates(
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"},
            proxies = {"https": "http://127.0.0.1:7890"}
        ),
        disp_request_extender
    ],
    "response": [
        RequestsExtender.domain_filter(save_response_extender("./dataflow"), allow_domain=["www.python.org"])
    ]
})


print("---------" * 6)
print(requests.get("https://www.python.org/"))
print("---------" * 6)
print(requests.get("https://www.google.com/"))

# ------------------------------------------------------
# [disp_request_extender]: {'method': 'get', 'url': 'https://www.python.org/', 'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}, 'params': None, 'proxies': {'https': 'http://127.0.0.1:7890'}}
# [save_response_extender]: save(https://www.python.org/)
# <Response [200]>
# ------------------------------------------------------
# [disp_request_extender]: {'method': 'get', 'url': 'https://www.google.com/', 'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}, 'params': None, 'proxies': {'https': 'http://127.0.0.1:7890'}}
# <Response [200]>
```

-------------------------------------------------------
## 6. 总结
上述就是基于requests库的组件化扩展方案的完整实现流程，但是需要注意的是，由于该方案替换的是 ***requests.api.request*** 函数，因此单独创建的 *requests.Session* 对象的请求调用不会被影响。

同时这种基于 hook 的实现方案由于涉及到隐式的函数替换，虽然提供了 *即插即用* 的简便特性，但如果用于复杂采集框架的构建，可能产生不可预期的影响。因此较合理的应用场景是用于一些开发工具的构建，或者在一些测试代码中减少重复逻辑，对于需要基于 requests 构建采集框架的场景，最好的方案还是通过显式的封装(比如封装一个下载器)来实现。