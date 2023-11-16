# Scrapy

-------------------------------------------------------
## Topic · 主题
> Scrapy is a fast high-level web crawling and web scraping framework, used to crawl websites and extract structured data from their pages. It can be used for a wide range of purposes, from data mining to monitoring and automated testing.

*Scrapy* 是一个快速的高层次的网络数据采集框架，用于抓取网站并从其页面中提取结构化数据，广泛应用于数据挖掘，监测和自动化测试。

本主题用于研究 *Scrapy* 框架的应用场景及相关源码实现。主要目的是学习和分析该通用数据采集框架的架构设计思想，以建立不同问题场景下的最佳实践，为后续自研框架提供理论基础。


-------------------------------------------------------
## Index · 索引
* [Scrapy-命令行模块架构分析](./Scrapy-命令行模块架构分析/Scrapy-命令行模块架构分析.md)
* [Scrapy-配置化机制分析](./Scrapy-配置化机制分析/README.md)
* [Scrapy-请求去重机制分析](./Scrapy-请求去重机制分析/Scrapy-请求去重机制分析.md)
* [Scrapy-运行状态监控组件的实现原理分析](./Scrapy-运行状态监控组件的实现原理分析/Scrapy-运行状态监控组件的实现原理分析.md)


-------------------------------------------------------
## Plan · 计划
* Scrapy 爬虫结构优化：
  * 回调式异步模式的缺陷(代码结构割裂)问题。
  * 基于协程的代码结构优化方案研究
* scrapy.Spider类实现与调用过程
* scrapy.signals 信号机制
* pipeline(数据管道)的生命周期
* middlewares(中间件)的生命周期
* AttributeError: 'Crawler' object has no attribute 'spider' 异常原因分析


-------------------------------------------------------
## Resource · 资源
* [官方网站](https://scrapy.org/)
* [Github仓库](https://github.com/scrapy/scrapy)