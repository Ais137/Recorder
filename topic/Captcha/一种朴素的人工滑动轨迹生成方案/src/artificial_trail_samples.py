# Name: 人工轨迹样本库
# Date: 2022-09-16
# Author: Ais
# Desc: None
# Update: (2023-09-15): 代码优化


import os
import json
import random


class ArtificialTrailSamples(object):
    """人工轨迹样本库

    一种朴素的人工滑动轨迹生成方案，用于解决在目标网站进行轨迹模式检测场景下的绕过问题，
    基于 **人工滑动轨迹样本库** 与 **插值算法** 来构建任意长度的模拟人工滑动轨迹。

    Methods:
        * build_trail_samples(static): 构建轨迹样本库
        * trail_interpolator(static): 轨迹插值算法
        * load: 加载轨迹样本库
        * build: 构建目标轨迹
    """

    @staticmethod
    def build_trail_samples(source_trail_samples_filepath:str, trail_samples_export_path:str="./trail_samples.json", sort_by:str="x_offset") -> int:
        """构建轨迹样本库

        通过 **人工轨迹样本捕获器** 捕获的原始轨迹数据构建轨迹样本库。

        Args:
            * source_trail_samples_filepath(str): 原始轨迹数据文件路径 
            原始轨迹数据格式定义如下: 
            [
                [["x轴偏移量", "y轴偏移量", "滑动时间"], ...],
                ...
            ]
            * trail_samples_export_path(str): 轨迹样本库导出路径，默认为 *./trail_samples.json*，
            样本库轨迹格式参考 class(Trail) 属性。
            * sort_by(str): 样本库轨迹排序方式，默认按照 x_offset(x轴总偏移量) 升序，其他排序方式参考 class(Trail) 属性。

        Returns:
            (int): 导出轨迹样本库，并返回轨迹样本数量。 

        Examples:
            >>> ArtificialTrailSamples.build_trail_samples(
            ...    # 原始轨迹数据文件路径
            ...    source_trail_samples_filepath = "./source_trail_samples.json",
            ...    # 轨迹样本库导出路径
            ...    trail_samples_export_path = "./trail_samples.json",
            ...    # 排序方式
            ...    sort_by = "x_offset"
            ... )
        """
        # 导入原始轨迹数据
        source_trail_samples = []
        with open(source_trail_samples_filepath, "r", encoding="utf-8") as f:
            source_trail_samples = json.loads(f.read())
        # 构建轨迹样本库
        trail_samples = sorted(
            # 根据原始轨迹生成轨迹样本
            [Trail(offset_sequence=ats).toDict() for ats in source_trail_samples],
            # 将轨迹按照 sort_by 键升序排序 
            key = lambda trail: trail[sort_by]
        )
        # 导出轨迹样本库
        with open(trail_samples_export_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(trail_samples, ensure_ascii=False))
        return len(trail_samples)
    
    @staticmethod
    def trail_interpolator(diff_sequence: list, target: int, w:int=0) -> list:
        """轨迹插值算法

        通过插值算法将轨迹的总偏移量移动到目标值

        Args:
            * diff_sequence(list): 轨迹坐标间隔序列 
            * target(int): 目标总偏移量
            * w(int): 轨迹分量索引

        Returns:
            (list) 插值后的轨迹坐标间隔序列

        Algorithm:
            设 diff_sequence 为某个轨迹的 *轨迹坐标间隔序列*，n 为轨迹点数量，target 为目标总偏移量。
                diff_sequence = [d1, d2, d3, ..., dx]
            则有目标总偏移量的差值 diff = target - sum(diff_sequence), (sum(diff_sequence)为当前轨迹的总偏移量)
            分解增量令 diff = dn*n + di
            其中 
                整体插值增量 dn = int(d/n)
                间隔插值增量 di = d%n
            通过以下方式对轨迹坐标序列进行插值：
            * 整体插值: 当 diff>=n 时有 dn>0：
                    [d1, d2, d3, d4, ..., dx]
                +   [dn, dn, dn, dn, ..., dn]
                ->  [d1+dn, d2+dn, d3+dn, ..., dx+dn]
            * 间隔插值: 当 diff<n 或 di>0 时：
                    [d1, d2, d3, d4, ..., dx]
                +   [1,  0,  1,  0, ...,  di]
                ->  [d1+1, d2+0, d3+1, ..., dx+di]
                其中插值间距为 round(n/di)
            由上述可知，增量偏移序列的轨迹点增量为
                diff_sequence[i] = diff_sequence[i] + dn + di
        """
        # 轨迹点数量
        n = len(diff_sequence)
        # 计算偏移量的差值
        diff = target - sum([t[w] for t in diff_sequence])
        # 分解增量
        dn, di = int(diff/n), (abs(diff)%n)
        # (diff >= n): 整体插值 -> [dn, dn, dn, ...0]
        if dn:
            for i in range(n):
                diff_sequence[i][w] += dn
        # (diff < n):  间隔插值 -> [1, ..., 1, ..., 1, ...]
        if di:
            for i in list(range(0, n, round(n/di)))[:di]:
                diff_sequence[i][w] += (1 if diff>0 else -1)
        return diff_sequence
    
    def __init__(self, trail_search_range=50, trail_interpolator=None):
        """初始化

        Args:
            * trail_search_range(int): 轨迹搜索范围，使用 *build* 方法时，从样本轨迹库中搜索轨迹时的范围。
            例如目标轨迹(x轴总偏移量)为 t，trail_search_range为(50)，则轨迹搜索范围为 (t-50, 5+50)。
            * trail_interpolator(Callable): 轨迹插值器，默认为 ArtificialTrailSamples.trail_interpolator
            轨迹插值器的形式定义如下:
                def interpolator(diff_sequence: list, target: int, w:int=0) -> list
            参数定义参考 ArtificialTrailSamples.trail_interpolator 的文档字符串。
        """
        # 轨迹样本库
        self.trail_samples = []
        # 轨迹搜索范围
        self.trail_search_range = trail_search_range
        # 插值器(插值算法实现)
        self.trail_interpolator = trail_interpolator or ArtificialTrailSamples.trail_interpolator
    
    def load(self, trail_samples_filepath=None):
        """加载轨迹样本库
        
        从指定文件路径中加载轨迹样本库

        Args:
            * trail_samples_filepath(str): 轨迹样本库文件路径，默认值为 *./trail_samples.json*

        Returns:
            self
        """
        trail_samples_filepath = trail_samples_filepath or os.path.join(os.path.dirname(__file__), "trail_samples.json")
        with open(trail_samples_filepath, "r", encoding="utf-8") as f:
            self.trail_samples = [
                Trail(
                    offset_sequence = trail["offset_sequence"], 
                    diff_sequence = trail["diff_sequence"],
                    interpolator = self.trail_interpolator
                ) 
                for trail in json.loads(f.read())
            ]
        return self
    
    def build(self, x_offset, t_offset=None):
        """构建目标轨迹

        指定 x_offset(x轴总偏移量) 和 t_offset(总滑动时间)，基于轨迹样本库中的人工轨迹样本，
        通过插值算法生成目标轨迹。

        Args:
            * x_offset(int): 目标轨迹x轴总偏移量
            * t_offset(int): 目标轨迹总滑动时间

        Returns:
            (Trail) 目标轨迹

        Examples:
            >>> trail = ArtificialTrailSamples().load().build(x_offset=325, t_offset=3000)
        """
        # 基于 trail_search_range 参数从指定范围内随机获取一个样本轨迹
        trail = random.choice([
            trail for trail in self.trail_samples 
            if (x_offset-self.trail_search_range <= trail.x_offset <= x_offset+self.trail_search_range)
        ]).copy()
        # 对轨迹样本进行插值
        return trail.interpolation(x_offset, "x").interpolation(t_offset, "t")



class Trail(object):
    """轨迹容器

    用于存储轨迹坐标数据

    Attributes:
        * offset_sequence(list): 轨迹坐标偏移序列
        * diff_sequence(list): 轨迹坐标间隔序列
        * interpolator(Callable): 轨迹插值器
        
    Methods:
        * interpolation: 轨迹插值
        * display: 显示轨迹结构
        * slider: 模拟滑动
    """

    @staticmethod
    def build_diff_sequence(offset_sequence:list) -> list:
        """构建间隔序列

        基于 *偏移序列* 构建 *间隔序列*，[1, 2, 4, ...] -> [1, 2, ...]

        Args:
            * offset_sequence(list): 偏移序列
        
        Returns:
            (list): 间隔序列

        Examples:
            >>> offset_sequence = [[0, 0], [1, 1], [2, 2], [4, 1], [3, 2], [6, 1]]
            >>> Trail.build_diff_sequence(offset_sequence)
            [[1, 1], [1, 1], [2, -1], [-1, 1], [3, -1]]
        """
        dim = len(offset_sequence[0])
        return [
            [offset_sequence[i+1][k]-offset_sequence[i][k] for k in range(dim)] 
            for i in range(len(offset_sequence)-1)
        ]
    
    @staticmethod
    def build_offset_sequence(diff_sequence:list, start:list=None) -> list:
        """构建偏移序列

        基于 *间隔序列* 构建 *偏移序列*，[1, 1, 2, ...] -> [1, 2, 4, ...]，
        该方法与 *build_diff_sequence* 互为逆操作。

        Args:
            * diff_sequence(list): 间隔序列
            * start(list): 起始值

        Returns:
            (list): 偏移序列
        
        Examples:
            >>> diff_sequence = [[1, 1], [1, 1], [2, -1], [-1, 1], [3, -1]]
            >>> Trail.build_offset_sequence(diff_sequence)
            [[0, 0], [1, 1], [2, 2], [4, 1], [3, 2], [6, 1]]
        """
        dim = len(diff_sequence[0])
        offset_sequence = [start or ([0] * dim)]
        [
            offset_sequence.append([offset_sequence[i][n]+diff_sequence[i][n] for n in range(dim)]) 
            for i in range(len(diff_sequence))
        ]
        return offset_sequence
    
    def __init__(self, offset_sequence:list=None, diff_sequence:list=None, interpolator=None, start=None):
        # 轨迹坐标偏移序列
        self.offset_sequence = offset_sequence or Trail.build_offset_sequence(diff_sequence, start or [0, 0, 0])
        # 轨迹坐标间隔序列
        self.diff_sequence = diff_sequence or Trail.build_diff_sequence(offset_sequence)
        # 轨迹插值器
        self.interpolator = interpolator
        # 偏移量分量索引表(用于插值时确定轨迹分量)
        self.offset_type_index = {"x": 0, "y": 1, "t": 2}

    def __len__(self):
        return len(self.offset_sequence)
    
    def __getitem__(self, key):
        return self.offset_sequence[key]
    
    def __iter__(self):
        return iter(self.offset_sequence)
    
    @property
    def x_offset(self):
        """轨迹坐标x轴总偏移量"""
        return self.offset_sequence[-1][0] - self.offset_sequence[0][0]
    
    @property
    def y_offset(self):
        """轨迹坐标y轴总偏移量"""
        return self.offset_sequence[-1][1] - self.offset_sequence[0][1]
    
    @property
    def t_offset(self):
        """轨迹总滑动时间"""
        return self.offset_sequence[-1][2] - self.offset_sequence[0][2]
    
    @property
    def dx(self):
        """轨迹坐标间隔序列(diff_sequence)x分量"""
        return [d[0] for d in self.diff_sequence]
    
    @property
    def dy(self):
        """轨迹坐标间隔序列(diff_sequence)y分量"""
        return [d[1] for d in self.diff_sequence]
    
    @property
    def dt(self):
        """轨迹坐标间隔序列(diff_sequence)时间分量"""
        return [d[2] for d in self.diff_sequence]
    
    @property
    def start(self):
        """起始轨迹坐标"""
        return self.offset_sequence[0][:]

    def toDict(self):
        """转换成字典"""
        return {
            # x轴总偏移量
            "x_offset": self.x_offset,
            # y轴总偏移量
            "y_offset": self.y_offset,
            # 总时间间隔
            "t_offset": self.t_offset,
            # 轨迹点数量
            "tn": len(self),
            # 起始状态
            "start": self.start,
            # 偏移序列
            "offset_sequence": self.offset_sequence,
            # 间隔序列
            "diff_sequence": self.diff_sequence
        }

    def copy(self):
        """复制对象"""
        return Trail(
            offset_sequence=[t[:] for t in self.offset_sequence], 
            diff_sequence=[t[:] for t in self.diff_sequence],
            interpolator = self.interpolator    
        )

    def interpolation(self, target, offset_type="x"):
        """轨迹插值

        对轨迹的指定分量进行插值

        Args:
            * target(int): 目标值
            * offset_type(str): 轨迹分量(["x", "y", "t"])

        Returns:
            self
        """
        if not target:
            return self
        if not callable(self.interpolator):
            raise ValueError(f'interpolator({self.interpolator}) is not Callable')
        if offset_type not in self.offset_type_index:
            raise ValueError(f'unknown offset_type({offset_type})')
        # 插值操作
        self.diff_sequence = self.interpolator(self.diff_sequence, target, self.offset_type_index[offset_type])
        # 更新轨迹数据
        self.offset_sequence = Trail.build_offset_sequence(self.diff_sequence, self.start)
        return self

    def display(self):
        """显示轨迹结构"""
        import matplotlib.pyplot as plt
        print("-----------" * 5)
        print(f"TRAIL_SAMPLES(tn={len(self)}): ")
        print(f"[x_offset]: ---> {self.x_offset}")
        print(f"[y_offset]: ---> {self.y_offset}")
        print(f"[t_offset]: ---> {self.t_offset}")
        print(f"[start]: ------> {self.start}")
        print(f"[end]: --------> {self.offset_sequence[-1]}")
        # 绘制图像
        n = list(range(len(self)))
        fig, ax = plt.subplots(2, 2, figsize=(12, 8))
        # 绘制x分量
        ax[0][0].plot(n, [p[0] for p in self.offset_sequence])
        ax[0][0].set_ylabel("x")
        ax[0][0].set_xlabel("n")
        # 绘制y分量
        ax[0][1].plot(n, [p[1] for p in self.offset_sequence])
        ax[0][1].set_ylabel("y")
        ax[0][1].set_xlabel("n")
        # 绘制dx分量
        ax[1][0].plot(n[:-1], self.dx)
        ax[1][0].set_ylabel("dx")
        ax[1][0].set_xlabel("n")
        # 绘制dy分量
        ax[1][1].plot(n[:-1], self.dy)
        ax[1][1].set_ylabel("dy")
        ax[1][1].set_xlabel("n")
        plt.show()
        return self

    def slider(self, driver, slider_xpath, delay=None, release=True):
        """模拟滑动
        
        通过selenium进行轨迹的滑动模拟，用于滑动缺口验证码的轨迹模式识别绕过

        Args:
            * driver(WebDriver): 浏览器驱动(webdriver.Chrome())
            * slider_xpath(str): 目标滑块元素的xpath表达式
            * delay(int): 总体滑动延时，当启用该参数时，轨迹的dt序列将被短路
            * release(bool): 滑动结束后是否释放滑块

        Returns:
            self
        """
        import time
        from selenium.webdriver.common.by import By
        from selenium.webdriver import ActionChains
        # 获取滑块元素
        slider_element = driver.find_element(By.XPATH, slider_xpath)
        # 点击滑块并保持
        ActionChains(driver).click_and_hold(slider_element).perform()
        # 计算平均延迟时间(将短路轨迹中的dt序列)
        _dt = (delay/len(self.diff_sequence)/1000) if delay else 0
        # 根据轨迹参数(d_offset)进行滑动
        for dx, dy, dt in self.diff_sequence:
            # duration = 250 会导致滑动延迟
            ActionChains(driver, duration=0).move_by_offset(xoffset=dx, yoffset=dy).perform()
            # 滑动延时
            time.sleep(_dt or (dt/1000 if dt>=0 else 0.001))
        # 释放滑块
        release and ActionChains(driver).release().perform()
        return self


# Test
if __name__ ==  "__main__":

    # # 构建轨迹样本库
    # ArtificialTrailSamples.build_trail_samples(
    #     # 原始轨迹数据文件路径
    #     source_trail_samples_filepath = "./source_trail_samples.json",
    #     # 轨迹样本库导出路径
    #     trail_samples_export_path = "./trail_samples.json",
    #     # 排序方式
    #     sort_by = "x_offset"
    # )

    trail = ArtificialTrailSamples().load().build(x_offset=325, t_offset=3000).display()