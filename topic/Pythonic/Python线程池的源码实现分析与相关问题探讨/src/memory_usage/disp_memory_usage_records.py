# Name: disp_memory_usage_records
# Date: 2024-04-22
# Author: Ais
# Desc: 绘制线程池内存占用统计图


import pandas as pd
import matplotlib.pyplot as plt 


# 加载数据
records = pd.read_json("./memory_usage_records.json")
# 计算相对内存使用量
memory_usage_baseline = records["memory_usage"][0] / 1024 / 1024
records["memory_usage"] = records["memory_usage"].map(lambda x: (x/1024/1024)-memory_usage_baseline)

print(records.head())

fig, ax1 = plt.subplots()

# 绘制内存使用曲线
p1 = ax1.plot(
    records["step"].to_numpy(), 
    records["memory_usage"].to_numpy(), 
    color="deepskyblue", 
    label=f"memory_usage - baseline({round(memory_usage_baseline, 2)})"
)
ax1.set_title("ThreadPoolExecutor memory usage statistics", fontsize=20)
ax1.set_ylabel("memory_usage(MB)", color="deepskyblue", fontsize=15)
ax1.legend(loc=2, fontsize=15)

# 绘制队列数量曲线
ax2 = ax1.twinx()
p2 = ax2.plot(
    records["step"].to_numpy(), 
    records["queue_size"].to_numpy(), 
    linewidth = 1.0,
    color="lightgreen", 
    label="queue_size",
)
ax2.set_ylabel("queue_size(int)", color="lightgreen", fontsize=15)
ax2.legend(loc=4, fontsize=15)

plt.show()