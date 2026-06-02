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


def show_summary(all_account_ranges, target_year_month):
    """
    爬取结束后汇总显示所有公众号的日期区间，按是否从目标月份第一天开始分组。

    参数:
        all_account_ranges: list of dict，每个元素包含:
            - nickname: 公众号名称
            - earliest: 最早文章日期字符串 'YYYY-MM-DD'
            - latest: 最晚文章日期字符串 'YYYY-MM-DD'
            - count: 文章数量
        target_year_month: 目标年月字符串，格式 'YYYY-MM'
    """
    if not all_account_ranges:
        print("\n本次未爬取到任何新文章，无日期汇总。")
        return

    first_day_str = f"{target_year_month}-01"

    from_first_day = []
    not_from_first_day = []

    for info in all_account_ranges:
        if info['earliest'] <= first_day_str:
            from_first_day.append(info)
        else:
            not_from_first_day.append(info)

    print()
    print("=" * 60)
    print(f"      全部公众号爬取日期汇总（目标月份：{target_year_month}）")
    print("=" * 60)

    if from_first_day:
        print(f"\n  ✅ 从 {target_year_month} 第一天开始爬取（{len(from_first_day)} 个）：")
        for info in from_first_day:
            print(f"    【{info['nickname']}】{info['count']} 篇，{info['earliest']} ~ {info['latest']}")

    if not_from_first_day:
        print(f"\n  ⚠️ 未从 {target_year_month} 第一天开始爬取（{len(not_from_first_day)} 个）：")
        for info in not_from_first_day:
            print(f"    【{info['nickname']}】{info['count']} 篇，{info['earliest']} ~ {info['latest']}")

    print()
