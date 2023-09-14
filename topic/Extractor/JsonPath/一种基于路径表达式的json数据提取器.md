# JsonPath · 一种基于路径表达式的 json 数据提取器

-------------------------------------------------------
## 1. 概述
一种基于路径表达式的 *json* 数据提取器设计与实现，用于解决复杂 *json* 数据下的提取问题。

完整源码位于 [jsonpath](./src/jsonpath.py)。

### Index

- [JsonPath · 一种基于路径表达式的 json 数据提取器](#jsonpath--一种基于路径表达式的-json-数据提取器)
  - [1. 概述](#1-概述)
    - [Index](#index)
    - [Meta](#meta)
  - [2. 问题场景](#2-问题场景)
  - [3. 特性设计](#3-特性设计)
  - [4. 架构设计](#4-架构设计)
    - [设计思想](#设计思想)
    - [路径表达式设计](#路径表达式设计)
  - [5. 核心代码](#5-核心代码)
  - [6. 使用样例](#6-使用样例)
    - [6.1. 构建 *JsonPathExtractor* 实例](#61-构建-jsonpathextractor-实例)
    - [6.2. 通过 *路径表达式* 提取指定路径的值](#62-通过-路径表达式-提取指定路径的值)
    - [6.3. 通过 *路径表达式* 提取指定路径模式的值](#63-通过-路径表达式-提取指定路径模式的值)
    - [6.4. 通过指定 *路径表达式映射表* 来提取多个指定路径的值](#64-通过指定-路径表达式映射表-来提取多个指定路径的值)


### Meta
```json
{
    "node": "AE2E20C1-A3FE-FDCE-F93C-3EFE9D9F5226",
    "name": "JsonPath · 一种基于路径表达式的 json 数据提取器",
    "author": "Ais",
    "date": "2023-09-14",
    "tag": ["JsonPath", "数据提取", "python", "路径表达式"]
}
```

-------------------------------------------------------
## 2. 问题场景
在 python 中提取 json 格式的数据对象时，通常采用链式调用的方式来提取指定值，
```py
val = data["key1"]["key2"]["key3"][...]["keyN"]
```
同时为了保证在提取时不触发 *KeyError* 异常，可以通过 *get* 的链式调用在键缺失时返回默认值。
```py
val = data.get("key1", {}).get("key2", {})...get("keyN", "default")
val = (data.get("key1", {}) or {}).get(...)
```  
上述方法在目标数据结构简单时是有效的，但是在面对 **复杂** 的提取场景时，比如：
* 目标数据嵌套层数过深，导致链式调用代码过长。
* 目标数据中混合了 *list* 类型的值，导致无法通过 *get* 进行完整的链式调用，需要针对 *list* 进行特殊处理。
* 需要对指定数据进行批量提取的场景。

为了解决上述场景的提取问题，通过设计 **一种基于路径表达式的 json 数据提取器** 来实现。

-------------------------------------------------------
## 3. 特性设计
*JsonPathExtractor* 提取器具有以下特性：
1. 通过路径表达式提取指定值，并在值不存在时返回默认值
```py
>>> extractor.get("/key1/key2/key3/.../keyN", default="test")
```
2. 目标数据包含混合结构(dict & list)的提取场景，比如包含数组作为中间结构。
```py
>>> extractor.get("/key1/index[1]/key2/.../keyN")
```
3. 对指定模式的路径进行批量提取，比如具有 “平行结构” 的值。
```py
>>> data = [
    {
        "name": "A1",
        "url": "https://www.test.com/A1"
    },
    {
        "name": "B2",
        "url": "https://www.test.com/B2"
    },
    ...
]
>>> extractor.find("/url") 
["https://www.test.com/A1", "https://www.test.com/B2"]
```

-------------------------------------------------------
## 4. 架构设计

### 设计思想  
*JsonPathExtractor* 的核心设计在于构建一个 **路径** 到 **数据值** 的索引映射表。通过对 *json* 数据结构的观察不难发现，实际上可以将其看作是一种树状结构。对于其中的某个数据节点，从根节点到该节点的 **路径**，可以作为该节点在整个树中的 **唯一索引**，而该节点的 **子树** 则是其数据值，通过这个视角，就可以通过遍历 json 数据，建立一个 **路径** 到 **数据值** 的唯一索引表。

### 路径表达式设计
***路径表达式(jpath)*** 是由 **路径分割符** 构成的字符串。  
example: "/data/page/info/page_num"

-------------------------------------------------------
## 5. 核心代码
```py
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
```

-------------------------------------------------------
## 6. 使用样例

* 测试数据
```py
data = {
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
```

### 6.1. 构建 *JsonPathExtractor* 实例
```py
extractor = JsonPathExtractor(data)
```

### 6.2. 通过 *路径表达式* 提取指定路径的值
用于目标数据嵌套程度过深的场景。
```py
>>> extractor.get("/data/type")
'A'
>>> extractor["/data/type"]
'A'
>>> extractor.get("/data/type/name", default="test")
'test'
>>> extractor.get("/data/list/1")
{'id': '#A2', 'name': 'A-2', 'source': {'url': 'http://www.test.com/data/A2', 'logo': './A2.png'}}
```

除了使用 *get* 方法进行提取外，还可以通过一个静态方法 *JsonPathExtractor.extract* 在不用构建实例的情况下进行快速提取: 
```py
>>> JsonPathExtractor.extract(test_data, "/data/type")
'A'
>>> JsonPathExtractor.extract(test_data, "/data/type/name")
>>> JsonPathExtractor.extract(test_data, "/data/type/name", default="test")
'test'
```

### 6.3. 通过 *路径表达式* 提取指定路径模式的值
用于批量提取数据的场景，支持正则表达式。
```py
>>> extractor.find("/data/list/\d+/id")
['#A1', '#A2', '#A3']
>>> extractor.find("/data/list/\d+/source/url")
['http://www.test.com/data/A1', 'http://www.test.com/data/A2', 'http://www.test.com/data/A3']
>>> extractor.find("/data/list/\d+/source/name")
[]
```

### 6.4. 通过指定 *路径表达式映射表* 来提取多个指定路径的值
```py
>>> jpath_map = {
    "pn": {"op": "get", "jpath": "/page/info/page_num"},
    "isEnd": {"op": "get", "jpath": "/page/info/end?", "default": False},
    "urls": {"op": "find", "jpath": "/data/list/\d+/source/url"}
}
>>> extractor.map(jpath_map)
{
    'pn': 1, 
    'isEnd': False, 
    'urls': ['http://www.test.com/data/A1', 'http://www.test.com/data/A2', 'http://www.test.com/data/A3']
}
```



