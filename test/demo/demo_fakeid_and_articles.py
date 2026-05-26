"""
Demo: 从文章链接获取公众号 fakeid，并爬取历史文章列表

用法:
    python demo_fakeid_and_articles.py <文章链接>
    python demo_fakeid_and_articles.py  (不带参数则使用脚本内硬编码的测试链接)

说明:
    - 获取 fakeid 后保存到 demo_account.json
    - 爬取文章后保存到 demo_article.json
    - 自包含，不依赖项目根目录的业务模块（仅导入 config.py 获取 API Key）
"""

import sys
import os
import requests
import random
import json
from datetime import datetime

# --------------- 配置 ---------------
# 从项目根目录的 config.py 读取 X_AUTH_KEY
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from config import X_AUTH_KEY
except ImportError:
    X_AUTH_KEY = "请在此处填写你的 X-Auth-Key"
    print("[警告] 未能导入 config.py，请确认 X_AUTH_KEY 已正确设置")

# 测试用文章链接（不传命令行参数时使用）
TEST_URL = "请在此处粘贴一个微信文章链接"

# 数据文件路径（与脚本同目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_ACCOUNT_FILE = os.path.join(SCRIPT_DIR, "demo_account.json")
DEMO_ARTICLE_FILE = os.path.join(SCRIPT_DIR, "demo_article.json")


# ============================================================
#  工具函数（内联自 utils.py / date_range.py）
# ============================================================

def get_headers():
    """获取模拟浏览器的请求头"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    ]
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'X-Auth-Key': X_AUTH_KEY
    }
    return headers


def show_date_range(nickname, articles):
    """显示某个公众号此次爬取到的文章日期区间"""
    if not articles:
        print(f"【{nickname}】此次未爬取到新文章")
        return
    dates = [article['date'] for article in articles]
    earliest = min(dates)
    latest = max(dates)
    print(f"【{nickname}】此次爬取到 {len(articles)} 篇文章，日期区间：{earliest} ~ {latest}")


def save_json(filepath, data):
    """将数据保存为 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [✓] 已保存到 {os.path.basename(filepath)}")


# ============================================================
#  Step 1: 从文章链接获取 fakeid
# ============================================================

def get_fakeid_from_url(article_url):
    """
    通过文章链接调用 API 获取公众号 fakeid 和 nickname。
    获取成功后保存到 demo_account.json。
    返回: dict {'nickname': ..., 'fakeid': ...} 或 None
    """
    print("=" * 60)
    print(" " * 15 + "Step 1: 获取公众号 fakeid")
    print("=" * 60)
    print(f"\n目标链接: {article_url}\n")

    api_url = f'https://down.mptext.top/api/public/v1/accountbyurl?url={article_url}'
    headers = get_headers()

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        data = response.json().get('list', [])

        if response.status_code == 200 and data:
            item = data[0]  # 取第一个结果
            fakeid = item.get('fakeid')
            nickname = item.get('nickname')
            account = {'nickname': nickname, 'fakeid': fakeid}

            print(f"  [✓] 公众号: {nickname}")
            print(f"  [✓] fakeid: {fakeid}")

            # 保存到 demo_account.json
            save_json(DEMO_ACCOUNT_FILE, account)

            return account
        else:
            print(f"  [✗] 获取失败，状态码: {response.status_code}")
            print(f"  [✗] 响应内容: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"  [✗] 请求异常: {e}")
        return None


# ============================================================
#  Step 2: 根据 fakeid 爬取历史文章列表
# ============================================================

def fetch_articles_by_fakeid(account):
    """
    根据公众号信息爬取历史文章列表。
    爬取完成后保存到 demo_article.json。
    参数: account - dict {'nickname': ..., 'fakeid': ...}
    返回: list of article dicts
    """
    fakeid = account['fakeid']
    nickname = account['nickname']

    print()
    print("=" * 60)
    print(" " * 15 + "Step 2: 爬取历史文章列表")
    print("=" * 60)
    print(f"\n准备爬取公众号：{nickname} (fakeid: {fakeid})\n")

    headers = get_headers()
    list_url = f'https://down.mptext.top/api/public/v1/article?fakeid={fakeid}&begin=0&size=20'

    try:
        response = requests.get(list_url, headers=headers, timeout=10)
        articles_data = response.json().get('articles', [])

        if response.status_code == 200 and articles_data:
            print(f"--- 正在提取【{nickname}】的文章 ---\n")

            article_list = []
            for item in articles_data:
                title = item.get('title')
                url = item.get('link')
                timestamp = item.get('create_time')
                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

                article = {
                    'account': nickname,
                    'title': title,
                    'url': url,
                    'date': date
                }
                article_list.append(article)
                print(f"  [+] ({date}) {title}")

            # 显示日期区间
            print()
            show_date_range(nickname, article_list)

            # 保存到 demo_article.json
            save_json(DEMO_ARTICLE_FILE, article_list)

            return article_list
        else:
            print(f"  [✗] 提取失败，状态码: {response.status_code}")
            print(f"  [✗] 响应内容: {response.text[:200]}")
            return []

    except Exception as e:
        print(f"  [✗] 请求异常: {e}")
        return []


# ============================================================
#  主入口
# ============================================================

def main():
    # 获取文章链接：优先使用命令行参数，其次使用硬编码的测试链接
    if len(sys.argv) > 1:
        article_url = sys.argv[1]
    else:
        article_url = TEST_URL
        if article_url.startswith("请在此处"):
            print("[错误] 请提供文章链接！")
            print(f"  用法: python {os.path.basename(__file__)} <文章链接>")
            print(f"  或者: 修改脚本中的 TEST_URL 变量")
            sys.exit(1)

    # Step 1: 获取 fakeid 并保存到 demo_account.json
    account = get_fakeid_from_url(article_url)
    if not account:
        print("\n[错误] 无法获取 fakeid，流程终止。")
        sys.exit(1)

    # Step 2: 爬取文章列表并保存到 demo_article.json
    articles = fetch_articles_by_fakeid(account)

    # 输出汇总
    print()
    print("=" * 60)
    print(" " * 22 + "汇总")
    print("=" * 60)
    print(f"  公众号: {account['nickname']}")
    print(f"  fakeid: {account['fakeid']}")
    print(f"  文章数: {len(articles)}")
    print(f"  账号文件: {os.path.basename(DEMO_ACCOUNT_FILE)}")
    print(f"  文章文件: {os.path.basename(DEMO_ARTICLE_FILE)}")
    print()


if __name__ == "__main__":
    main()
