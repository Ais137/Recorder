# Python导入系统研究-从文件IO动态构建模块

import types

# 从源码构建模块对象
def import_module_from_source(module_name, source):
    module = types.ModuleType(module_name)
    exec(source, module.__dict__)
    return module

# 从文件IO加载源码
with open("./test_module.py", "rb") as f:
    test_module = import_module_from_source("test_module", f.read())

# 测试
test_module.test("aaa")
print(test_module)

"""
基于上述原型代码研究 **从源码动态构建模块** 的方案，通过网络IO来传输源码并动态构建模块，
以此为基础研究模块的 **热更新** 方案。 
"""