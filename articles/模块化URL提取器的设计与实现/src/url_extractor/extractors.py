# Name: URL提取模块
# Date: 2023-10-12
# Author: Ais
# Desc: None


import re
import json
import lxml.etree
from .utils import JsonPathExtractor


def xpath_extractor(expression:str, text:str, params:dict=None) -> list:
    """xpath-URL提取器
    
    通过 xpath 表达式从文本中提取URL列表。

    Args:
        * expression(str): 目标URL的xpath表达式
        * text(str): html文本数据

    Returns:
        (list) 提取出的URL列表
    """
    if isinstance(text, str):
        data = text
    elif isinstance(text, (list, tuple)):
        data = "".join(text)
    else:
        raise ValueError(f'Unsupported text({type(text)})')
    html = lxml.etree.HTML(data)
    return html.xpath(expression)


def jpath_extractor(expression:str, text:str, params:dict=None) -> list:
    """jpath-URL提取器

    通过 jpath(路径表达式) 从json数据中提取URL列表。

    Args:
        * expression(str): 路径表达式，详见 .utils.JsonPathExtractor 中的定义。
        * text(str): json格式的文本数据

    Returns:
        (list) 提取出的URL列表
    """
    if isinstance(text, str):
        data = json.loads(text)
    elif isinstance(text, (list, tuple)):
        data = [json.loads(d) if isinstance(d, str) else d for d in text]
    elif isinstance(text, dict):
        data = text
    else:
        raise ValueError(f'Unsupported text({type(text)})')
    return JsonPathExtractor(data).find(expression, default=[])


def regex_extractor(expression:str, text:str, params:dict=None) -> list:
    """regex-URL提取器

    通过 re(正则表达式) 模块中 re.findall 方法从文本数据中提取URL列表。

    Args:
        * expression(str): 目标URL的正则表达式
        * text(str): html文本数据
        * params(dict): 扩展参数
            * toStr(bool): 将结果转换成字符串

    Returns:
        (list) 提取出的URL列表
    """
    params = params or {}
    if isinstance(text, str):
        data = text
    elif isinstance(text, (dict, list, tuple)):
        data = json.dumps(text)
    else:
        raise ValueError(f'Unsupported text({type(text)})')
    urls = re.findall(expression, data)
    return "".join(urls) if params.get("toStr") else urls

