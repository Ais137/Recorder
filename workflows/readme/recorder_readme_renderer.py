# Name: recorder_readme_renderer
# Date: 2024-05-17
# Author: Ais
# Desc: 项目 README 文档渲染器


import os
import json
from jinja2 import FileSystemLoader, Environment


class RecorderReadmeRenderer(object):
    """项目 README 文档渲染器

    渲染并生成项目的 README 文档。  
    
    Confs:
        * article_meta_filepath: 文档元数据文件路径。
        * articles_dirpath: 文档目录相对路径，用于构建文档的索引链接。
        * top_articles_nodes_filepath: 精选文档id列表文件路径。
        * latest_articles_num: 最新文档展示数量(默认为10)。
        * templates_dirpath: 模板目录路径。
        * readme_template: README模板名。
        * readme_export_filepath: README文档导出路径(默认为项目根目录)。

    Dependencies:
        * articles.article_meta_integrator.ArticlesMetaIntegrator

    Templates:
        * recorder-readme.j2

    Output:
        根据模板渲染的 README 文档。
    """

    def __init__(self, confs=None):
        self.confs = {
            "article_meta_filepath": "",
            "articles_dirpath": "",
            "top_articles_nodes_filepath": "",
            "latest_articles_num": 10,
            "templates_dirpath": "",
            "readme_template": "",
            "readme_export_filepath": "",
        }
        confs and isinstance(confs, dict) and self.confs.update(confs)

    def process(self) -> bool:
        return self.render()

    def render(self):
        """渲染README文档"""
        article_meta_sources = self.load_article_meta_sources(
            article_meta_filepath = self.confs["article_meta_filepath"],
            articles_dirpath = self.confs["articles_dirpath"],
        )
        top_articles = self.generate_top_articles_list(
            article_meta_sources = article_meta_sources,
            top_articles_nodes_filepath = self.confs["top_articles_nodes_filepath"],
        )
        latest_articles = self.generate_latest_articles_list(
            article_meta_sources = article_meta_sources,
            articles_num = self.confs["latest_articles_num"],
        )
        env = Environment(
            loader = FileSystemLoader(self.confs["templates_dirpath"]),
        )
        template = env.get_template(self.confs["readme_template"])
        readme = template.render(
            top_articles = top_articles,
            latest_articles = latest_articles,
        )
        with open(self.confs["readme_export_filepath"], 'w', encoding='utf-8') as f:
            f.write(readme)
        return True

    def load_article_meta_sources(self, article_meta_filepath:str, articles_dirpath:str) -> dict:
        """加载文档元数据

        加载文档元数据，并将其从 list 转换成以 文档id(article_meta["node"]) 为 key 的 dict。
        
        Args:
            * article_meta_filepath : 文档元数据文件路径。
            * articles_dirpath : 文档目录相对路径，用于构建文档的索引链接。

        Returns:
            加载并转换后的文档元数据，格式定义如下：
            {
                "node": {
                    "node": "str|文档唯一id",
                    "name": "str|文档名",
                    "author": "str|作者",
                    "date": "str|发布日期",
                    "topic": "list|主题",
                    "tag": "list|标签",
                    "filepath": "str|文件路径，相对于 articles_dirpath 路径"
                    ...
                },
                ...
            }
        """
        with open(article_meta_filepath, 'r', encoding='utf-8') as f:
            article_meta_sources = json.loads(f.read())
        for article_meta in article_meta_sources:
            article_meta["filepath"] = f'{articles_dirpath}/{article_meta["filepath"]}'
        return {article_meta["node"]:article_meta for article_meta in article_meta_sources}
    
    def generate_top_articles_list(self, article_meta_sources:dict, top_articles_nodes_filepath:str):
        """构建精选文档列表
        
        根据指定的文档id列表(top_articles_nodes_filepath)，生成精选文档元数据列表。

        Args:
            * article_meta_sources : 文档元数据。
            * top_articles_nodes_filepath : 精选文档id列表文件路径，格式定义如下：
            [
                "article_node": "str|文档id(node字段)",
                ...
            ]

        Returns:
            精选文档元数据列表，格式定义如下：
            [
                {
                    "node": "",
                    "name": "",
                    ...
                },
                ...
            ]
        """
        with open(top_articles_nodes_filepath, 'r', encoding='utf-8') as f:
            top_articles_nodes = json.loads(f.read())
        return [
            article_meta_sources[article_node] 
            for article_node in top_articles_nodes 
            if article_node in article_meta_sources
        ]
    
    def generate_latest_articles_list(self, article_meta_sources:dict, articles_num:int=10):
        """构建最新文档列表
        
        将文档按照 创建时间(date) 字段排序后，返回其中最新的文档元数据列表。

        Args:
            * article_meta_sources : 文档元数据。
            * articles_num : 最新文档展示数量

        Returns:
            最新文档元数据列表，格式定义如下：
            [
                {
                    "node": "",
                    "name": "",
                    ...
                },
                ...
            ]
        """
        return sorted(list(article_meta_sources.values()), key=lambda data:data["date"], reverse=True)[:articles_num]
    


if __name__ ==  "__main__":
    
    import os, sys
    sys.path.append("..")
    from utils import get_project_root_path
    
    RecorderReadmeRenderer(
        confs = {
            "article_meta_filepath": "../meta/articles-meta.json",
            "articles_dirpath": "./articles",
            "top_articles_nodes_filepath": "../meta/top-articles-nodes.json",
            "latest_articles_num": 10,
            "templates_dirpath": "../templates",
            "readme_template": "recorder-readme.j2",
            "readme_export_filepath": os.path.join(get_project_root_path(), "README.md"),
        }
    ).render()
