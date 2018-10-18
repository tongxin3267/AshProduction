# AshProduction
一些灰产相关的项目，大家可以关注下，可日常可收费。1

### 1.简书
    1. 刷阅读量（已实现）
    2. 简书批量注册账号（未实现）
### 2.招聘
### 3.知乎
    1. 根据发现的文章全站抓取（已实现）
    2. 自动登录（未实现）
### 4.Csdn
    1. 刷点击量（已实现）
### 5.今日头条


# Run This Project (运行项目)
(1) download it (下载项目)
```
git clone git@github.com:lateautunm/AshProduction.git
``` 
(2) install enviroment (安装环境)
```
pip install -u pipenv && pipenv install --dev
```
(3) startup project (启动一个项目)
```
pipenv run python jianshu/add_pageview.py --userid=e9fdf09df277

pipenv run python csdn/add_pageview.py --userid=maliao1123

pipenv run python csdn/add_pageview.py --help

Usage: add_pageview.py [OPTIONS]

Options:
  --userid TEXT  your jianshu homepageId
  --help         Show this message and exit.
```
(4) look result (看看结果))
```
see https://www.jianshu.com/u/e9fdf09df277
```
(5) have fun （快乐欣赏)
