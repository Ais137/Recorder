# Articles-Structure-Specification-v2.0

文档结构规范

## 虚拟化目录与索引的动态构建

在 *v1.0* 规范中，每一篇 *Article(文档)* 都是存储在指定 *Topic(主题)* 目录下的，同时需要将 *Article* 的索引添加到 *Topic* 根目录的 *README.md* 中，这种方式导致了 *Article* 与 *Topic* 目录的硬绑定。

```
topic
 ├─ topicA
 |   ├─ article1
 |   |   ├─ article1.md
 |   |   └─ src/
 |   ├─ article2
 |   |   └─ article2.md
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

当需要对 *Article* 所属的 *Topic* 进行变更时，首先要将 *Article* 转移到新的 *Topic* 目录下，然后需要手动修改新旧两个 *Topic.README.md* 中的索引，甚至包括根目录 *README* 中展示的文档索引。这种方式无疑是繁琐的。

因此为了解决这个问题，考虑采用 **虚拟化目录** 方案，即通过将 topic(主题信息) 写入 *Article* 的 **元数据** 中来指定其所属的主题，然后通过扫描 *Articles* 目录下的所有文档的元数据来动态构建索引目录。

## Article - 目录结构规范

*Article* 以 **扁平化** 的结构存储于 *articles* 目录。

```
articles
 ├─ articleA
 |   ├─ articleA.md
 |   └─ article-meta.json
 ├─ articleB
 |   ├─ articleB.md
 |   └─ article-meta.json
 |
 ...
```

每一篇 *Article* 中必须包含两个主要文件：

  * article.md : 与目录同名的文档主文件。
  * article-meta.json : 元数据文件。

*Article* 内部可以使用目录来划分资源：
  
  * /src : 存放相关的研究和测试源码。
  * /img : 存放图像资源。

对于上述方案，当 *Article* 所属的 *Topic* 变更时，只需要修改元数据即可，然后通过自动化构建工具动态构建索引。同时这种扁平化结构对后续的一些自动化构建方案的实现来说也更加方便。

## Article - 元数据结构规范

**元数据** 用于记录 *Article* 的相关创建信息和分类特征等，在 *v1.0* 版本中是写入到 文档(article.md) 中的，但是这种方式并不合理，在后续进行文档自动化管理时，需要加载文档数据并识别其中的元数据片段。因此考虑将其从文档中分离，单独使用一个文件来存储元数据。

***article-meta.json*** 用于存储 *Article* 的 **元数据**，与 *article.md* 存放在同级目录，可以通过该文件来将一个目录标记为一个 *Article*。

***article-meta.json*** 的必要字段如下：

| 字段 | 描述 | 格式 |
| ---- | ---- | ---- |
| node | 用于标记 Article 的唯一id(使用UUID生成) | str | 
| name | 与 article.md 同名 | str |
| author | 作者名(Ais) | str |
| date | 创建日期 | str(yyyy-mm-dd) | 
| topic | 文档主题 | list[str] | 
| tag | 文档标签 | list[str] |  

***article-meta.json*** 的样例如下：

```json
{
    "node": "A54660CD-99B5-2C55-4338-1CC8BE707203",
    "name": "Python线程池的源码实现分析与相关问题探讨",
    "author": "Ais",
    "date": "2024-04-18",
    "topic": ["Pythonic"],
    "tag": ["python", "concurrent", "Thread", "ThreadPoolExecutor", "语法研究", "高级特性", "并发编程"] 
}
```

## Article - 动态索引构建

***/articles/README.md*** 用于存放文档的完整索引目录，通过扫描 */articles* 目录下的文档元数据进行动态构建。

## Meta
* date : 2024-05-11
* author: Ais