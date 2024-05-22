# Name: article_topic_intergrator
# Date: 2024-05-14
# Author: Ais
# Desc: 文档主题数据集成


import os
import json


class ArticleTopicIntergrator(object):
    """文档主题数据集成
    
    加载文档元数据并从中提取主题数据，集成后输出到指定文件路径。
    如果文档主题数据文件已经存在，并不会直接覆盖，而是采用更新的方式来写入动态统计数据。
    
    Confs:
        * article_meta_filepath: 文档元数据文件路径。
        * articles_topic_export_filepath: 文章主题数据导出路径。

    Dependencies:
        * articles.article_meta_integrator.ArticlesMetaIntegrator

    Output:
        文档主题数据的输出格式如下：
        {
            "topic": {
                "articles_count": "int|该主题下的文档数量",
                "articles": [
                    "str|articles|文档id",
                    ...
                ],
                ...
            },
            ...
        }
    """

    def __init__(self, confs=None):
        self.confs = {
            "article_meta_filepath": "",
            "articles_topic_export_filepath": "",
        }
        confs and isinstance(confs, dict) and self.confs.update(confs)

    def process(self) -> bool:
        self.integration()
        return True

    def integration(self) -> dict:
        """集成文章主题数据"""
        # 加载文档元数据
        with open(self.confs["article_meta_filepath"], 'r', encoding='utf-8') as f:
            article_meta_sources = json.loads(f.read())
        # 加载文档主题数据
        if os.path.exists(self.confs["articles_topic_export_filepath"]):
            with open(self.confs["articles_topic_export_filepath"], 'r', encoding='utf-8') as f:
                articles_topic_sources = json.loads(f.read())
        else:
            articles_topic_sources = {}
        # 按照主题对文章进行分类
        article_topic_classify = {}
        for article_meta in article_meta_sources:
            for topic in article_meta["topic"]:
                if topic not in article_topic_classify:
                    article_topic_classify[topic] = []
                article_topic_classify[topic].append(article_meta)
        # 构建文档主题统计
        articles_topic_data = {}
        for topic in sorted(list(article_topic_classify.keys())):
            articles_topic_data[topic] = {}
            articles_topic_data[topic].update(articles_topic_sources.get(topic, {}))
            articles = [article["node"] for article in article_topic_classify[topic]]
            articles_topic_data[topic]["articles_count"] = len(articles)
            articles_topic_data[topic]["articles"] = articles
        # 导出数据
        with open(self.confs["articles_topic_export_filepath"], 'w', encoding='utf-8') as f:
            f.write(json.dumps(articles_topic_data, ensure_ascii=False, indent=4))



if __name__ ==  "__main__":
    
    ArticleTopicIntergrator(
        confs = {
            "article_meta_filepath": "../meta/articles-meta.json",
            "articles_topic_export_filepath": "../meta/articles-topic.json",
        }
    ).integration()
    
