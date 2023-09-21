# Name: RequestsExtender
# Date: 2023-09-21
# Author: Ais
# Desc: 基于requests库的组件化扩展方案


import requests
from functools import reduce
from urllib.parse import urlparse


class RequestsExtender(object):
    """requests扩展器

    基于 requests 库的组件化功能扩展方案

    Attributes:
        * HOOK_EVENTS(list): 可注册事件列表
        * extenders(dict): 已注册扩展器
        * source_request_method(Callable): 原始请求方法(requests.api.request) 
    
    Methods:
        * register(static): 注册扩展器
        * domain_filter(static): 域名过滤器
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

        注册扩展器到指定事件，基于 hook 增强原始请求方法(requests.api.request)，主要流程如下:
            1. 将 extenders 注册到 RequestsExtender.extenders 属性上。
            2. 固定 requests.api.request 方法到 RequestsExtender.source_request_method 属性上，
            用于后续调用。
            3. 构建 request_extension(请求扩展函数)，增加 extenders 的执行逻辑。
            4. hook requests.api.request 方法，替换成 request_extension。
        
        Args:
            extenders(dict): 扩展器是一个字典，格式定义如下：
            {
                "request": [extender1, extender2, ...],
                "response": [extender1, extender2, ...]
            }
            extenders 的键名为子扩展器的注册事件类型，可选事件详见 HOOK_EVENTS 属性，
            其中:
                * request  : 在请求调用之前执行，扩展器的定义为 def extender(req)，req(dict) 为请求的参数字典。
                * response : 在请求调用之后执行，扩展器的定义为 def extender(res)，res(requests.Response) 为请求响应对象。

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

    @staticmethod
    def domain_filter(extender, allow_domain:list=None, ignore_domain:list=None):
        """域名过滤器

        为扩展器指定允许处理的域名列表，其他域名的请求将被过滤。

        Args:
            * extender(Callable): 扩展器
            * allow_domain(list): 允许处理的域名列表
            * ignore_domain(list): 忽略的域名列表

        Returns:
            (Callable) domain_filter_extender 

        Examples:
            >>> RequestsExtender.domain_filter(extender, allow_domain=["www.python.org"])
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
    
    @staticmethod
    def request_templates(**templates):
        """请求参数模板

        提供一个请求参数模板，该扩展器 将请求模板参数合并到实际的请求参数中

        Args:
            templates: request请求参数

        Returns:
            (Callable) request_templates_extender 

        Examples:
            >>> RequestsExtender.request_templates(
            ...    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"},
            ...    proxies = {"https": "http://127.0.0.1:7890"},
            ...    verify = False
            ... )
        """
        def request_templates_extender(req):
            for key, val in templates.items():
                if isinstance(val, dict):
                    req.setdefault(key, {}).update(val)
                else:
                    req[key] = val
            return req
        return request_templates_extender
    
    
if __name__ ==  "__main__":

    import os

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


