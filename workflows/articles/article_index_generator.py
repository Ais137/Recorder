# Name: article_index_generator
# Date: 2024-05-13
# Author: Ais
# Desc: 文档索引生成器


import os
import json
from jinja2 import FileSystemLoader, Environment


class ArticleIndexGenerator(object):
    """文档索引生成器
    
    通过 文档元数据 和 文档主题数据 来渲染并生成文档索引。

    Confs:
        * article_meta_filepath: 文档元数据文件路径。
        * article_topic_filepath: 文档主题数据文件路径。
        * templates_dirpath: 模板目录路径。
        * articles_index_template: 文档索引模板名。
        * articles_dirpath: 文档目录相对路径，用于构建文档的索引链接。
        * articles_index_export_filepath: 文档索引文件导出路径。
        * top_topics: 置顶该列表中的主题。

    Dependencies:
        * articles.article_meta_integrator.ArticlesMetaIntegrator
        * articles.article_topic_intergrator.ArticleTopicIntergrator

    Templates:
        * articles-index.md.j2

    Output:
        根据模板渲染的文档索引文件。
    """

    def __init__(self, confs=None):
        self.confs = {
            "article_meta_filepath": "",
            "article_topic_filepath": "",
            "templates_dirpath": "",
            "articles_index_template": "",
            "articles_dirpath": "",
            "articles_index_export_filepath": "",
            "top_topics": [],
        }
        confs and isinstance(confs, dict) and self.confs.update(confs)

    def process(self) -> bool:
        return self.generate_articles_index()

    def generate_articles_index(self) -> bool:
        """生成文档索引"""
        # 加载文档元数据
        with open(self.confs["article_meta_filepath"], 'r', encoding='utf-8') as f:
            article_meta_sources = json.loads(f.read())
        for article_meta in article_meta_sources:
            article_meta["filepath"] = f'{self.confs["articles_dirpath"]}/{article_meta["filepath"]}'
        article_meta_sources = {article_meta["node"]: article_meta for article_meta in article_meta_sources}
        # 加载文档主题数据
        with open(self.confs["article_topic_filepath"], 'r', encoding='utf-8') as f:
            article_topic_sources = json.loads(f.read())
        # 构建渲染数据
        article_topic = {}
        for topic in self.confs["top_topics"] + sorted(article_topic_sources.keys()):
            if (not topic in article_topic_sources) or (topic in article_topic):
                continue
            article_topic[topic] = article_topic_sources[topic]
            article_topic[topic]["articles"] = sorted([
                article_meta_sources[node]
                for node in article_topic[topic]["articles"]
            ], key=lambda data:data["date"], reverse=True)
        # 渲染文档索引文件
        env = Environment(
            loader = FileSystemLoader(self.confs["templates_dirpath"]),
        )
        template = env.get_template(self.confs["articles_index_template"])
        with open(self.confs["articles_index_export_filepath"], 'w', encoding='utf-8') as f:
            f.write(template.render(article_meta_data=article_topic))
        return True


if __name__ ==  "__main__":

    import os, sys
    sys.path.append("..")
    from utils import get_project_root_path
    
    ArticleIndexGenerator(
        confs = {
            "article_meta_filepath": "../meta/articles-meta.json",
            "article_topic_filepath": "../meta/articles-topic.json",
            "templates_dirpath": "../templates",
            "articles_index_template": "articles-index.md.j2",
            "articles_dirpath": "./articles",
            "articles_index_export_filepath": os.path.join(get_project_root_path(), "articles/articles-index.md"),
            "top_topics": ["Pythonic", "Solution", "Scrapy"],
        }
    ).generate_articles_index()


