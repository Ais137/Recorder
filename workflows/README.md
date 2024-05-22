# Workflows · 文档自动化工作流

**文档自动化工作流** 是 **Recorder** 的子项目，主要用于进行文档相关资源的自动化生成和管理。

--------------------------------------------------
## 目录结构

* *articles* : articles 目录下文档相关自动化工作流。
* *meta* : 元数据目录，工作流依赖的元数据。
* *readme* : 项目 README 文档的渲染与自动化构建工作流。
* *templates* : 渲染模板目录，工作流依赖的渲染模板。
* *utils* : 通用组件。

--------------------------------------------------
## 开发流程

1. 明确需求和自动化工作流程，根据具体场景对目标工作流进行拆分，拆解出子步骤。

2. 在对应模块目录下开发子模块，模块目录与工作流操作的数据目录对应，比如文档索引的自动构建工作流对应于 *articles* 目录。每一个子模块对应一个子步骤，子模块功能应该保证单一原则。

3. 在模块目录的 *\_\_main\_\_.py* 文件中添加工作流对应的子命令，通过调用子模块来实现完整的工作流逻辑。 

--------------------------------------------------
## 开发规范

### 工作流子模块开发规范

工作流子模块的格式定义如下：

```py
class WorkflowModule(object):
    """工作流子模块
    
    工作流子模块功能描述信息

    # 运行配置
    Confs:
        * article_meta_filepath: 文档元数据文件路径。
        * article_topic_filepath: 文档主题数据文件路径。
        ...
    
    # 依赖项
    Dependencies:
        * articles.article_meta_integrator.ArticlesMetaIntegrator
        * articles.article_topic_intergrator.ArticleTopicIntergrator
        ...

    # 渲染模板
    Templates:
        * articles-index.md.j2
        ...

    # 导出资源
    Output:
        ...
    """

    def __init__(self, confs=None):
        self.confs = {
            "article_meta_filepath": "",
            "article_topic_filepath": "",
            ...
        }
        confs and isinstance(confs, dict) and self.confs.update(confs)

    def process(self) -> bool:
        return True
```

--------------------------------------------------
## 工作流列表

* Articles文档索引自动构建工作流
```sh
python -m workflows.articles index
```

* README文档自动渲染与构建工作流
```sh
python -m workflows.readme build
```