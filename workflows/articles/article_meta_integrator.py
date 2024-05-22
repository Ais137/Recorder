# Name: article_meta_integrator
# Date: 2024-05-13
# Author: Ais
# Desc: 文档元数据集成器


import os
import json


class ArticlesMetaIntegrator(object):
    """文档元数据集成器
    
    扫描 articles_dirpath 下的文档元数据，集成后输出到指定文件路径。

    Confs:
        * articles_dirpath: 文档目录路径，从该目录下扫描并集成文档元数据。
        * articles_meta_export_filepath: 文档元数据导出路径。
        * article_meta_filename: 文档元数据文件名(参考 Articles-Structure-Specification 规范)。
        * sort_by: 排序条件，根据文档元数据中的指定键进行排序，默认排序为 "-date"，"-" 用于指定是否降序。

    Output:
        在指定文件路径输出集成的文档元数据，格式定义如下：
        [
            {
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
        ]
    """

    def __init__(self, confs=None):
        self.confs = {
            "articles_dirpath": "",
            "articles_meta_export_filepath": "",
            "article_meta_filename": "article-meta.json",
            "sort_by": "-date",
        }
        confs and isinstance(confs, dict) and self.confs.update(confs)

    def process(self) -> bool:
        self.integration()
        return True

    def integration(self) -> dict:
        """集成文档元数据"""
        article_meta_list = []
        # 扫描 articles 目录下的元数据文件
        for article_dir in os.listdir(self.confs["articles_dirpath"]):
            article_meta_filepath = os.path.join(self.confs["articles_dirpath"], article_dir, self.confs["article_meta_filename"])
            if not os.path.exists(article_meta_filepath):
                continue
            with open(article_meta_filepath, 'r', encoding='utf-8') as f:
                article_meta = json.loads(f.read())
                article_meta["filepath"] = f'{article_dir}/{article_dir}.md'
                article_meta_list.append(article_meta)
        # 对集成的元数据进行排序
        sort_key, sort_reverse = (self.confs["sort_by"][1:], True) if self.confs["sort_by"].startswith("-") else (self.confs["sort_by"], False)
        article_meta_list = sorted(article_meta_list, key=lambda data:data[sort_key], reverse=sort_reverse)
        # 导出集成的文档元数据
        if self.confs["articles_meta_export_filepath"]:
            with open(self.confs["articles_meta_export_filepath"], 'w', encoding='utf-8') as f:
                f.write(json.dumps(article_meta_list, ensure_ascii=False, indent=4))
        return article_meta_list

    
    
if __name__ ==  "__main__":
    
    import sys
    sys.path.append("..")
    from utils import get_project_root_path
    project_root_path = get_project_root_path()

    ArticlesMetaIntegrator(
        confs = {
            "articles_dirpath": os.path.join(project_root_path, "articles"),
            "articles_meta_export_filepath": os.path.join(project_root_path, "workflows/meta/articles-meta.json"),
        }
    ).integration()