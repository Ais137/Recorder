# Articles-Structure-Specification-v1.0

***topic*** 目录用于存储 **以问题研究为核心的相关文章**，并按照 *topic(主题)* 进行分类，以树状结构进行存储，是项目的核心组成部分。

--------------------------------------------------
## Topic文档 - 目录结构规范
*topic* 目录中的子目录结构需要遵循以下规范。

1. 每个主题/子主题的根目录需要包含 *README.md* 文件，用于后期在建立管理系统的时候，通过检查 *README.md* 文件来识别主题目录。

2. 每个主题中采用文件夹对文档进行分割，文件夹名称应表达要探讨的核心问题，通常与核心文档同名。

3. *src* 目录用于存储文档中使用到的源代码。

目录结构样例如下：
```
topic
 ├─ topicA
 |   ├─ doc1
 |   |   ├─ doc1.md
 |   |   └─ src/
 |   ├─ doc2
 |   |   └─ doc2.md
 |   └─ README.md
 ├─ topicB
 |   ├─ ...
 |   └─ README.md
 ├─ topicC
 |   ├─ ...
 |   └─ README.md
 |
 ...
```

--------------------------------------------------
## Topic文档 - 元数据结构规范
*topic* 文档中的 *元数据* 记录文档的相关创建信息和特征，用于管理系统识别和索引的建立。通常位于文档中 *概述* 段落的 *### Meta* 标题下，其结构定义如下：

```json
{
    "node": "文档的唯一标识码(全大写的UUID)",
    "name": "文档名",
    "author": "作者(Ais)",
    "date": "文档完成日期(yyyy-mm-dd)",
    "tag": ["文档标签"] 
}
```

实际样例如下：

```json
{
    "node": "D0B58787-93D2-DBD0-E731-3817F18AED2A",
    "name": "python中的反射机制及其应用场景",
    "author": "Ais",
    "date": "2023-09-13",
    "tag": ["python", "语法研究", "高级特性", "反射机制", "内省机制", "自省", "动态构建"]
}
```

--------------------------------------------------
## Meta
* date : 2023-09-15
* author : Ais
* version : v1.0