# Name: JsonPathExtractor
# Date: 2023-08-16
# Author: Ais
# Desc: 一种基于路径表达式的json数据提取器


import re


class JsonPathExtractor(object):
    """一种基于路径表达式的json数据提取器

    通过 jpath(路径表达式) 从json数据对象中提取指定数据字段，
    主要用于数据嵌套程度过深和批量提取的场景。

    Attributes:
        * JSONPATH_SEP(static): 路径分隔符
        * data(dict|list): 原始json数据
        * index(dict): 路径索引表

    Methods:
        * extract(static): 通过 jpath(路径表达式) 提取指定路径的单个值
        * get: 通过 jpath(路径表达式) 提取指定路径的单个值
        * find: 通过 jpath(路径表达式) 提取指定路径模式(支持正则表达式)的值
        * map: 通过指定 jpath_map(路径表达式映射表) 来提取多个指定路径的值
    """

    # 路径分隔符
    JSONPATH_SEP = "/"

    @staticmethod
    def extract(data, jpath, default=None):
        """提取值(静态方法)

        通过 jpath(路径表达式) 提取指定路径的单个值，用于目标数据嵌套程度过深的场景。

        Args:
            * jpath(str): 路径表达式
            * default(any): 默认值

        Returns:
            (any) 指定路径的值或者默认值

        Examples:
            >>> JsonPathExtractor.extract(test_data, "/data/type")
            'A'
            >>> JsonPathExtractor.extract(test_data, "/data/type/name")
            >>> JsonPathExtractor.extract(test_data, "/data/type/name", default="test")
            'test'
        """
        jpath = jpath.split(JsonPathExtractor.JSONPATH_SEP)[1:]
        val = data
        while jpath:
            try:
                key = int(jpath.pop(0)) if isinstance(val, (list, tuple)) else jpath.pop(0) 
                val = val[key]
            except: 
                return default
        return val

    def __init__(self, data):
        # 原始数据
        self.data = data
        # 路径索引表
        self.index = self._build_jsonpath_index(val=data)

    def _build_jsonpath_index(self, path="", key=None, val=None, index=None):
        """构建路径索引表

        通过递归遍历 json 数据对象，构建 **路径索引表**。
        路径索引表的键由根节点到目标节点的路径构成。

        Args:
            * path(str): 路径前缀
            * key(str): 数据键名
            * val(dict|list|tuple): 数据值
            * index(dict): 索引表

        Returns:
            (dict): 路径索引表
        """
        index = {} if index is None else index
        jpath = (path + JsonPathExtractor.JSONPATH_SEP + str(key)) if key is not None else "" 
        index[jpath] = val
        if isinstance(val, dict):
            [self._build_jsonpath_index(jpath, k, v, index) for k, v in val.items()]
        elif isinstance(val, (list, tuple)):
            [self._build_jsonpath_index(jpath, i, val[i], index) for i in range(len(val))]
        else:
            pass
        return index

    def __getitem__(self, jpath):
        return self.index[jpath]

    def get(self, jpath, default=None):
        """获取值

        通过 jpath(路径表达式) 提取指定路径的单个值，用于目标数据嵌套程度过深的场景。

        Args:
            * jpath(str): 路径表达式
            * default(any): 默认值

        Returns:
            (any) 指定路径的值或者默认值

        Examples:
            >>> extractor.get("/data/type")
            'A'
            >>> extractor["/data/type"]
            'A'
            >>> extractor.get("/data/type/name", default="test")
            'test'
            >>> extractor.get("/data/list/1")
            {'id': '#A2', 'name': 'A-2', 'source': {'url': 'http://www.test.com/data/A2', 'logo': './A2.png'}}
        """
        return self.index.get(jpath, default)
    
    def find(self, jpath, default=None):
        """查找值

        通过 jpath(路径表达式) 提取指定路径模式(支持正则表达式)的值，用于批量提取数据的场景。

        Args:
            * jpath(str): 路径表达式(支持正则表达式)
            * default(any): 当该参数未指定时，默认返回空数组
        
        Returns:
            (list) 目标数据

        Examples:
            >>> extractor.find("/data/list/\d+/id")
            ['#A1', '#A2', '#A3']
            >>> extractor.find("/data/list/\d+/source/url")
            ['http://www.test.com/data/A1', 'http://www.test.com/data/A2', 'http://www.test.com/data/A3']
            >>> extractor.find("/data/list/\d+/source/name")
            []
        """
        return [val for path, val in self.index.items() if re.match(jpath, path)] or default or []
    
    def map(self, jpath_map):
        """映射值

        通过指定 jpath_map(路径表达式映射表) 来提取多个指定路径的值。

        Args:
            * jpath_map(dict): 路径表达式映射表, 其模式定义如下
                {
                    "key": {"op":"", "jpath":"", "default":""}
                }
                * op: 提取方式，可选的有 ["get", "find"]
                * jpath: 路径表达式
                * default: 默认值

        Returns:
            (dict) 目标数据

        Examples:
            >>> jpath_map = {
            ...    "pn": {"op": "get", "jpath": "/page/info/page_num"},
            ...    "isEnd": {"op": "get", "jpath": "/page/info/end?", "default": False},
            ...    "urls": {"op": "find", "jpath": "/data/list/\d+/source/url"}
            ... }
            >>> extractor.map(jpath_map)
            {'pn': 1, 'isEnd': False, 'urls': ['http://www.test.com/data/A1', 'http://www.test.com/data/A2', 'http://www.test.com/data/A3']}
        """
        return {
            field: getattr(self, jpath["op"].lower())(jpath["jpath"], default=jpath.get("default"))
            for field, jpath in jpath_map.items()
        }


if __name__ ==  "__main__":
    
    # 测试数据
    test_data = {
        "status": 0,
        "page": {
            "info": {
                "page_num": 1,
                "page_size": 10,
                "total_page": 1000,
            },
            "isEnd": False,
        },
        "data": {
            "type": "A",
            "count": 3,
            "list": [
                {
                    "id": "#A1",
                    "name": "A-1",
                    "source": {
                        "url": "http://www.test.com/data/A1",
                        "logo": "./A1.png"
                    }
                },
                {
                    "id": "#A2",
                    "name": "A-2",
                    "source": {
                        "url": "http://www.test.com/data/A2",
                        "logo": "./A2.png"
                    }
                },
                {
                    "id": "#A3",
                    "name": "A-3",
                    "source": {
                        "url": "http://www.test.com/data/A3",
                        "logo": "./A3.png"
                    }
                },
            ]
        },
        "error": ""
    }

    # 构建提取器
    extractor = JsonPathExtractor(test_data)
    
    import doctest
    doctest.testmod()

    