# Name: 通用组件
# Date: 2024-05-11
# Author: Ais
# Desc: None


import os


def get_project_root_path(flags:list=None) -> str:
    """获取项目根路径
    
    从当前目录向上遍历，并根据 flags 特征判定是否是项目根目录

    Args:
        * flags: 项目根目录下的特征文件/文件夹名，默认根据 ["articles", "workflows", ".gitignore"] 来识别。
    
    Returns:
        项目根目录的绝对路径

    Raises:
        Exception: 向上遍历到根目录时未找到项目根目录。
    """
    flags = flags or ["articles", "workflows", ".gitignore"]
    project_root_path = os.path.abspath(__file__)
    while project_root_path != os.path.dirname(project_root_path):
        if all([os.path.exists(os.path.join(project_root_path, flag)) for flag in flags]):
            return project_root_path
        project_root_path = os.path.dirname(project_root_path)
    raise Exception("Can't found project root path")

