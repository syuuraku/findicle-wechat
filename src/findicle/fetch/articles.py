import requests
from findicle.common import utils, storage
from findicle.filter.choose_date import show_date_range, show_summary
from datetime import datetime


def fetch_articles():

    """获取所有公众号的文章列表，与历史数据合并后存入 all_articles 并持久化"""

    # 1. 加载历史数据
    all_articles = storage.load_articles()
    old_count = len(all_articles)
    print()
    print(f"从本地加载了 {old_count} 篇历史文章")
    print()

    # 2. 从历史数据构建去重集合
    seen_urls = {article['url'] for article in all_articles}

    # 3. 获取请求头和公众号列表
    current_headers = utils.get_headers()
    account_list = storage.load_accounts()
    
    if not account_list:
        print("未获取到任何公众号信息，请检查 data/urls.txt 或 data/accounts.json")
        return all_articles

    # 4. 输入目标月份（用于最终汇总分组）
    target_year_month = input("请输入目标年月（格式 YYYY-MM，如 2026-05）：").strip()

    print()
    print("=" * 60)
    print(" " * 20 + "开始获取文章列表")
    print("=" * 60)
    print()

    # 5. 爬取各公众号的文章
    new_count = 0
    all_account_ranges = []  # 收集所有公众号的日期信息
    for account in account_list:
        current_fakeid = account['fakeid']
        current_nickname = account['nickname']
        
        print()
        print(f"准备爬取公众号：{current_nickname}")

        list_url = f'https://down.mptext.top/api/public/v1/article?fakeid={current_fakeid}&begin=0&size=20'

        list_response = requests.get(list_url, headers=current_headers, timeout=10)
        list_data = list_response.json().get('articles', [])

        if list_response.status_code == 200 and list_data:
            print(f"--- 正在提取【{current_nickname}】的文章 ---")
            account_new_articles = []  # 记录该公众号本次新增的文章
            for item in list_data:
                title = item.get('title')
                url = item.get('link')
                timestamp = item.get('create_time')
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

                if url in seen_urls:
                    print(f"  [跳过重复] {title}")
                    continue

                seen_urls.add(url)
                new_article = {
                    'account': current_nickname,
                    'title': title,
                    'url': url,
                    'date': date
                }
                all_articles.append(new_article)
                account_new_articles.append(new_article)
                new_count += 1
                print(f"  [+] ({date}) {title} ")

            # 显示该公众号此次爬取的日期区间
            show_date_range(current_nickname, account_new_articles)

            # 收集该公众号的日期区间信息用于最终汇总
            if account_new_articles:
                dates = [a['date'] for a in account_new_articles]
                all_account_ranges.append({
                    'nickname': current_nickname,
                    'earliest': min(dates),
                    'latest': max(dates),
                    'count': len(account_new_articles),
                })

        else:
            print(f"提取【{current_nickname}】失败，状态码: {list_response.status_code}")

    # 6. 按日期排序
    all_articles.sort(key=lambda x: (x['account'], x['date']))

    # 7. 持久化保存
    storage.save_articles(all_articles)

    # 8. 显示全部公众号日期汇总
    show_summary(all_account_ranges, target_year_month)

    print(f"\n本次新增 {new_count} 篇，总计 {len(all_articles)} 篇文章（已去重、已排序、已保存）")
    print()
    return all_articles



if __name__ == "__main__":
    fetch_articles()
