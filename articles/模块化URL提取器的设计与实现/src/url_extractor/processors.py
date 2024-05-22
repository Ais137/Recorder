# Name: URL处理模块
# Date: 2023-10-12
# Author: Ais
# Desc: None


import re
from urllib.parse import urljoin, urlparse


def UrlDupeFilter():
    """URL去重器
    
    对重复URL进行过滤，使用 set 数据结构进行去重处理。

    Examples:
        >>> url_dupefilter = UrlDupeFilter()
        >>> url_dupefilter(["https://www.test.com/page/1", "https://www.test.com/page/2"]
        ['https://www.test.com/page/2', 'https://www.test.com/page/1']
        >>> url_dupefilter(["https://www.test.com/page/2", "https://www.test.com/page/3"]
        ['https://www.test.com/page/3']
    """
    url_dupefilter_set = set()
    def url_dupefilter(urls:list) -> list:
        urls = set(urls) - url_dupefilter_set
        url_dupefilter_set.update(urls)
        return list(urls)
    return url_dupefilter


def UrlDomainFilter(allow_domain:set=None, ignore_domain:set=None):
    """URL域名过滤器

    通过指定的域名集合对URL列表进行过滤。
    
    Args:
        * allow_domain: 允许的域名列表
        * ignore_domain: 忽略的域名列表
        当 allow_domain 和 ignore_domain 同时启用时，只有 allow_domain 参数会生效。

    Examples:
        >>> url_domain_filter = UrlDomainFilter(allow_domain={"www.test.com"})
        >>> url_domain_filter(["https://www.test.com/", "https://www.data.com/"])
        ['https://www.test.com/']
        >>> url_domain_filter = UrlDomainFilter(ignore_domain={"www.data.com"})
        >>> url_domain_filter(["https://www.test.com/", "https://www.data.com/"])
        ['https://www.test.com/']
    """
    def url_domain_filter(urls:list) -> list:
        if allow_domain:
            return [url for url in urls if urlparse(url).netloc in allow_domain]
        if ignore_domain:
            return [url for url in urls if urlparse(url).netloc not in ignore_domain]
        return urls
    return url_domain_filter


def UrlRegexFilter(pattern:str):
    """URL正则过滤器

    通过正则表达式对URL列表进行过滤。

    Args:
        * pattern: 可以通过的URL正则模式

    Examples:
        >>> url_regex_filter = UrlRegexFilter(r'https\://www\.test\.com/article/\d+\.html')
        >>> url_regex_filter(["https://www.test.com/article/1234.html", "https://www.test.com/article/4567.html", "https://www.test.com/page/1"])
        ['https://www.test.com/article/1234.html', 'https://www.test.com/article/4567.html']
    """
    regex = re.compile(pattern)
    def url_regex_filter(urls:list) -> list:
        return [url for url in urls if regex.match(url)]
    return url_regex_filter


def UrlAssembler(url_prefix:str="", url_templates:str=""):
    """URL装配器

    通过指定参数来组合，用于构建完整URL。

    Args:
        * url_prefix: 通过指定URL前缀来拼接完整URL。
        * url_templates: 通过指定模板字符串来构建完整URL。

    Examples:
        >>> url_assembler = UrlAssembler(url_prefix="https://www.test.com")
        >>> url_assembler(["/article/1234.html", "/article/4567.html"])
        ['https://www.test.com/article/1234.html', 'https://www.test.com/article/4567.html']
        >>> url_assembler = UrlAssembler(url_templates="https://www.test.com/article/{}.html")
        >>> url_assembler(["1234", "4567"])
        ['https://www.test.com/article/1234.html', 'https://www.test.com/article/4567.html']
    """
    def url_assembler(urls:list) -> list:
        if url_prefix:
            return [urljoin(url_prefix, url) for url in urls]
        if url_templates:
            return [url_templates.format(url) for url in urls]
        return urls
    return url_assembler
    
