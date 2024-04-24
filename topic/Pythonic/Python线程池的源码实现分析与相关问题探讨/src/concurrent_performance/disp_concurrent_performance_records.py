# Name: disp_concurrent_performance_records
# Date: 2024-04-24
# Author: Ais
# Desc: 绘制线程池并发性能统计图


import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib.ticker as ticker

# 加载数据
records = pd.read_json("./concurrent_performance_records_1.json")
# records = pd.read_json("./concurrent_performance_records_2.json")
# records = pd.read_json("./concurrent_performance_records_3.json")

print(records.head())

ax = plt.axes()
ax.set_title("ThreadPoolExecutor concurrent performance statistics", fontsize=20)

ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

ax.set_ylabel("task_num(int)", color="deepskyblue", fontsize=15)
ax.set_ylim((0, 30))

plt.plot(
    records["step"].to_numpy(),
    records["task_diff"].to_numpy(),
    label="task_num",
    color="deepskyblue",
)

plt.plot(
    records["step"].to_numpy(),
    records["queue_size"].to_numpy(),
    label="queue_size",
    color="red",
)

plt.hlines(20.3, 0, 30, linestyles="--", colors="blue")

plt.legend(fontsize=15)

plt.show()