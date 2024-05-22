# Name: 文档自动化工作流
# Date: 2024-05-14
# Author: Ais
# Desc: None


import argparse


# 构建命令行解析器
parser = argparse.ArgumentParser(prog='PROG', description="Articles-文档自动化工作流")
subparser = parser.add_subparsers(help="commands")


# ------------------------------------------------------ #
# 构建文档索引
build_articles_index = subparser.add_parser(name="index", help="构建文档索引")

def build_articles_index_handler(args):

    import os
    try:
        from workflows.utils import get_project_root_path
    except: 
        from utils import get_project_root_path
    
    project_root_path = get_project_root_path()

    print(f'[Articles](index): start build articles-index')
    # 集成文档元数据
    from .article_meta_integrator import ArticlesMetaIntegrator
    articles_dirpath = os.path.join(project_root_path, "articles")
    articles_meta_filepath = os.path.join(project_root_path, "workflows/meta/articles-meta.json")
    ArticlesMetaIntegrator(
        confs = {
            "articles_dirpath": articles_dirpath,
            "articles_meta_export_filepath": articles_meta_filepath,
        }
    ).process()
    print(f'[Articles](index|step-1): integration articles-meta success -> ({articles_meta_filepath})')
    # 集成文档主题数据
    from .article_topic_intergrator import ArticleTopicIntergrator
    articles_topic_filepath = os.path.join(project_root_path, "workflows/meta/articles-topic.json")
    ArticleTopicIntergrator(
        confs = {
            "article_meta_filepath": articles_meta_filepath,
            "articles_topic_export_filepath": articles_topic_filepath,
        }
    ).process()
    print(f'[Articles](index|step-2): integration articles-topic success -> ({articles_topic_filepath})')
    # 构建文档索引
    from .article_index_generator import ArticleIndexGenerator
    articles_index_filepath = os.path.join(get_project_root_path(), "articles/README.md")
    ArticleIndexGenerator(
        confs = {
            "article_meta_filepath": articles_meta_filepath,
            "article_topic_filepath": articles_topic_filepath,
            "templates_dirpath": os.path.join(project_root_path, "workflows/templates"),
            "articles_index_template": "articles-index.md.j2",
            "articles_dirpath": ".",
            "articles_index_export_filepath": articles_index_filepath,
            "top_topics": ["Pythonic", "Solution", "Scrapy"],
        }
    ).process()
    print(f'[Articles](index|step-3): build articles-index success -> ({articles_index_filepath})')
    print(f'[Articles](index): build articles-index completed')

build_articles_index.set_defaults(func=build_articles_index_handler)


# ------------------------------------------------------ #
# 解析参数
args = parser.parse_args()
args.func(args)