# Name: 文档自动化工作流
# Date: 2024-05-20
# Author: Ais
# Desc: 自动构建README文档


import argparse


# 构建命令行解析器
parser = argparse.ArgumentParser(prog='PROG', description="自动构建 README 文档")
subparser = parser.add_subparsers(help="commands")


# ------------------------------------------------------ #
# 自动构建 README 文档
build_readme_doc = subparser.add_parser(name="build", help="自动构建 README 文档")
build_readme_doc.add_argument("-n", "--latest_articles_num", type=int, default=10, help="最新文章展示数量")

def build_readme_doc_handler(args):
    
    import os
    try:
        from workflows.utils import get_project_root_path
    except: 
        from utils import get_project_root_path
    from .recorder_readme_renderer import RecorderReadmeRenderer
    
    project_root_path = get_project_root_path()
    workflows_root_path = os.path.join(project_root_path, "workflows")

    RecorderReadmeRenderer(
        confs = {
            "article_meta_filepath": os.path.join(workflows_root_path, "meta/articles-meta.json"),
            "articles_dirpath": "./articles",
            "top_articles_nodes_filepath": os.path.join(workflows_root_path, "meta/top-articles-nodes.json"),
            "latest_articles_num": args.latest_articles_num,
            "templates_dirpath": os.path.join(workflows_root_path, "templates"),
            "readme_template": "recorder-readme.j2",
            "readme_export_filepath": os.path.join(project_root_path, "README.md"),
        }
    ).process()

    print(f'[README](build): build readme-doc completed')

build_readme_doc.set_defaults(func=build_readme_doc_handler)


# ------------------------------------------------------ #
# 解析参数
args = parser.parse_args()
args.func(args)