"""
日期区间展示模块

爬取完每个公众号的文章后，显示此次爬取到的文章日期区间。
"""


def show_date_range(nickname, articles):
    """
    显示某个公众号此次爬取到的文章日期区间。

    参数:
        nickname: 公众号名称
        articles: 此次爬取到的文章列表，每篇文章为 dict，包含 'date' 字段（格式 'YYYY-MM-DD'）
    """
    if not articles:
        print(f"【{nickname}】此次未爬取到新文章")
        return

    dates = [article['date'] for article in articles]
    earliest = min(dates)
    latest = max(dates)

    print(f"【{nickname}】此次爬取到 {len(articles)} 篇文章，日期区间：{earliest} ~ {latest}")
