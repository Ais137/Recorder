# Name: URL提取器
# Date: 2023-10-12
# Author: Ais
# Desc: 模块化URL提取器


from .extractors import xpath_extractor, jpath_extractor, regex_extractor


class UrlExtractor(object):
    """URL提取器
    
    根据 URL提取表达式 从文本中提取出URL列表，采用模块化的设计，通过组合不同的子模块来进行提取器的自定义和功能扩展。

    Attributes:
        * url_extract_exps(list): URL提取表达式，通过该表达式来指定待提取的URL模式。
        * url_extractors(dict): URL提取模块容器是一个映射字典，键为提取模块id，值为提取模块的引用，通过 url_extract_exps(URL提取表达式) 进行调用。
        * url_processors(list): URL处理模块容器是一个列表结构，其中每个子模块是一个可调用对象，用于处理提取后的URL，例如过滤，拼接等操作。

    Methods:
        * extract: 提取URL(调用入口)

    Examples:
        >>> urls = UrlExtractor(
        ...     url_extract_exps=(
        ...         ("xpath", "//ul[@id='article']/li/a/@href"),
        ...     )
        ... ).extract(text)
    """

    def __init__(self, url_extractors:dict=None, url_extract_exps:list=None, url_processors:list=None):
        # URL提取模块容器
        self.url_extractors = url_extractors or {
            "xpath": xpath_extractor,
            "jpath": jpath_extractor,
            "regex": regex_extractor
        }
        # URL提取表达式
        self.url_extract_exps = url_extract_exps or []
        # URL处理模块容器
        self.url_processors = url_processors or []

    def extract(self, text:str, url_extract_exps:list=None) -> list:
        """提取URL(调用入口)
        
        根据 URL提取表达式 从文本中提取出URL列表。

        Args:
            * text: 目标文本
            * url_extract_exps: URL提取表达式，当该参数为空时，使用类初始化时传入的 url_extract_exps 参数。

        Returns:
            提取出的URL列表

        Raises:
            * ValueError: text 或者 url_extract_exps(self.url_extract_exps) 为空时抛出异常。
        """
        url_extract_exps = url_extract_exps or self.url_extract_exps
        if not text or not url_extract_exps:
            raise ValueError("text or url_extract_exps must be not None")
        urls = self.extract_urls(url_extract_exps, text)
        return self.process_urls(urls) if urls else []        

    def extract_urls(self, url_extract_exps:list, text:str) -> list:
        """提取URL(内部实现)

        根据 URL提取表达式 从 self.url_extractors 查找指定提取模块来提取URL。
        """
        urls = []
        for url_extract_exp in url_extract_exps:
            if len(url_extract_exp) == 3:
                extractor_id, extract_exp, extend_params = url_extract_exp
            else:
                extractor_id, extract_exp, extend_params = *url_extract_exp, {}
            # 调用指定的提取模块解析执行提取表达式
            urls = self.url_extractors[extractor_id](extract_exp, urls or text, extend_params)
            if not urls:
                break
        return urls
    
    def process_urls(self, urls:list) -> list:
        """处理URLs
        
        通过 self.url_processors(URL处理模块) 依次处理提取出的URL列表。
        """
        for processor in self.url_processors:
            urls = processor(urls)
            if not urls:
                break
        return urls
    
