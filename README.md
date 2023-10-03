# Project_Bilibili_Download
爬取和分析bilibili网站的实时热门视频信息，并提供视频查询、视频下载功能、评论获取、弹幕关键词热度图、评论情感倾向图展示等功能;

项目为后端部分
## 视频爬取、查询与下载
基于报文拆解和视频音频合成实现，默认为该视频的最高分辨率；

支持管理员对指定非法视频进行特殊处理，通过包污染将视频引导向指定的内容;

查询基于AC自动机实现
## 评论爬取
爬取实时热门100条评论
## 热评情感分析
基于snowNLP实现
![BV1MV41147aJ](https://github.com/CynthiaLou/Project_Bilibili_Download/assets/61345723/43b8fbbf-c524-4074-939b-dc4445d3dc57)

## 弹幕热度云图
基于jieba分词和wordcloud实现
![cloud#BV1iy4y1u7d3](https://github.com/CynthiaLou/Project_Bilibili_Download/assets/61345723/ff707375-4ed8-413a-bfe9-d6906de90cc4)

## 支持log
![图像2023-10-3 17 57](https://github.com/CynthiaLou/Project_Bilibili_Download/assets/61345723/25ed7c94-12f9-494a-b5cb-bc482d5eb939)
## 数据库：mySQL




