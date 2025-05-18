# 笔趣阁爬取 Freereading
******
## 1. 项目背景
笔趣阁网站上的小说，普遍存在广告，且需要在线阅读，和一般的txt形式的阅读习惯不符，故撰写freereading代码，自动以多线程爬取笔趣阁，合并为txt形式小说


## 2. 使用方法

进入笔趣阁网站，例如https://www.c24f.cc/

打开想要下载小说的某一章，例如：https://www.c24f.cc//read/170567/23.html

这里面170567就是bookid，替换mian/get.py中的id运行即可

```
url_lis, bookname = get_list("170567")
```

**请保持网络畅通**
