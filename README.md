# 微信公众号文章采集与筛选

批量采集微信公众号文章，通过日期筛选 + AI 主题分类，自动筛选出自定义主题的文章。

## 使用流程

### 准备工作

1. 复制 `config.example.py` 为 `config.py`，填入你的 API Key（详见下方「配置」部分）
2. 在项目根目录下创建 `data` 文件夹，并新建 `data/urls.txt`，将待采集的公众号文章链接粘贴进去（每行一个）

### 第一步：获取公众号信息

```bash
python fetch_fakeid.py
```

从 `data/urls.txt` 中读取链接，解析出公众号的 `fakeid`，与本地已有库去重后保存到 `data/accounts.json`。

### 第二步：爬取文章列表

```bash
python fetch_article.py
```

遍历 `data/accounts.json` 中的所有公众号，爬取最新文章列表，与历史数据合并去重后保存到 `data/articles.json`。运行时会要求输入目标年月，用于最终汇总各公众号的日期覆盖情况。

### 第三步：按主题筛选文章

```bash
python filter_articles.py
```

运行后依次完成：
1. 从 `topics/` 目录选择筛选主题
2. 输入起止日期，从 `data/articles.json` 中筛选文章
3. 逐篇提取正文（前 800 字）
4. 调用 DeepSeek API 判断是否匹配所选主题
5. 结果保存到 `data/filter_result.json`

#### 自定义主题

在 `topics/` 目录下新建 YAML 文件即可添加自定义主题：

```yaml
name: "科研成果"
categories:
  - "发表高水平论文"
  - "获得科研奖项"
  - "申请或授权专利"
```

## 配置

1. 复制 `config.example.py` 为 `config.py`
2. 填入你的 API Key：

```python
X_AUTH_KEY = "你的 X-Auth-Key"
DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
```

## 项目结构

```
article_in_wechat/
├── config.example.py   # 配置模板
├── storage.py          # 统一的数据文件路径与读写
├── utils.py            # 请求头生成
├── fetch_fakeid.py     # 步骤1: 获取公众号 fakeid
├── fetch_article.py    # 步骤2: 爬取文章列表
├── date_range.py       # 日期区间展示工具
├── filter_articles.py  # 步骤3: 日期筛选 + AI 主题分类
└── topics/             # 主题配置目录
    └── foreign_affairs.yaml  # 示例：外事主题
```

运行后会自动在 `data/` 目录下生成以下数据文件（不纳入版本控制）：

| 文件 | 说明 |
|------|------|
| `data/urls.txt` | 待解析的公众号文章链接 |
| `data/accounts.json` | 公众号信息库 |
| `data/articles.json` | 文章库 |
| `data/filter_result.json` | 筛选结果 |

## 依赖

- Python 3.8+
- `requests`
- `beautifulsoup4`
- `pyyaml`

## 致谢

本项目的公众号信息获取、文章列表爬取及正文下载等 API 调用均基于 [wechat-article-exporter](https://github.com/wechat-article/wechat-article-exporter) 项目提供的接口，感谢原作者的开源贡献。
