import requests
import utils
import json
import os
from datetime import datetime
import get_fakeid

# 持久化文件路径
ARTICLES_FILE = "articles.json"


def load_articles():
    """从本地 JSON 文件加载已有文章列表"""
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_articles(articles):
    """将文章列表保存到本地 JSON 文件"""
    with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def fetch_articles():

    """获取所有公众号的文章列表，与历史数据合并后存入 all_articles 并持久化"""

    # 1. 加载历史数据
    all_articles = load_articles()
    old_count = len(all_articles)
    print()
    print(f"从本地加载了 {old_count} 篇历史文章")
    print()

    # 2. 从历史数据构建去重集合
    seen_urls = {article['url'] for article in all_articles}

    # 3. 获取请求头和公众号列表
    current_headers = utils.get_headers()
    account_list = get_fakeid.fetch_fakeids()
    
    if not account_list:
        print("未获取到任何公众号信息，请检查 urls.txt 或 accounts.json")
        return all_articles

    print("=" * 60)
    print(" " * 20 + "开始获取文章列表")
    print("=" * 60)
    print()

    # 4. 爬取各公众号的文章
    new_count = 0
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
            for item in list_data:
                title = item.get('title')
                url = item.get('link')
                timestamp = item.get('create_time')
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

                if url in seen_urls:
                    print(f"  [跳过重复] {title}")
                    continue

                seen_urls.add(url)
                all_articles.append({
                    'account': current_nickname,
                    'title': title,
                    'url': url,
                    'date': date
                })
                new_count += 1
                print(f"  [+] ({date}) {title} ")

        else:
            print(f"提取【{current_nickname}】失败，状态码: {list_response.status_code}")

    # 5. 按日期排序
    all_articles.sort(key=lambda x: (x['account'], x['date']))

    # 6. 持久化保存
    save_articles(all_articles)

    print(f"\n本次新增 {new_count} 篇，总计 {len(all_articles)} 篇文章（已去重、已排序、已保存）")
    print()
    return all_articles



if __name__ == "__main__":
    fetch_articles()
