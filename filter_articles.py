import requests
import utils
import storage
from bs4 import BeautifulSoup
import time
import random
import json
from config import DEEPSEEK_API_KEY


def get_articles_by_date(start_date, end_date):
    """根据日期区间从本地文件提取文章（不触发爬取）

    Args:
        start_date: 起始日期字符串，如 "2025-04-01"
        end_date:   结束日期字符串，如 "2025-04-30"

    Returns:
        符合日期区间的文章列表（闭区间 [start_date, end_date]）
    """
    articles = storage.load_articles()
    filtered = [a for a in articles if start_date <= a['date'] <= end_date]
    print(f"从本地 {len(articles)} 篇文章中筛选出 {len(filtered)} 篇（{start_date} ~ {end_date}）")
    return filtered


def extract_article_text(url, headers):
    """抓取微信文章页面，提取正文纯文本（前800字）"""
    try:
        response = requests.get(f'https://down.mptext.top/api/public/v1/download?url={url}', headers=headers, timeout=15)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"  ⚠️ 抓取失败，状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find(id='js_content')

        if not content_div:
            print("  ⚠️ 未找到正文区域（id='js_content'）")
            return None

        plain_text = content_div.get_text(separator='\n', strip=True)
        return plain_text[:800]

    except Exception as e:
        print(f"  ⚠️ 抓取异常 [{url}]: {e}")
        return None


def judge_foreign_affairs(title, text):
    """调用 DeepSeek API 判断文章是否属于外事主题，返回 JSON 结果"""
    prompt = f"""请判断以下文章是否属于"外事"主题。外事主题包括但不限于：
- 国外学校/机构来访或出访
- 与国外学者的学术合作与交流
- 在国际顶尖期刊或会议上发表论文
- 港澳台地区的学术交流与合作
- 国际学术会议参会或举办
- 国际项目合作、联合培养

文章标题：{title}

文章正文（前800字）：
{text}

请只返回以下JSON格式，不要输出其他内容：
{{"is_foreign_affairs": true/false, "reason": "简要原因"}}"""

    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个文章主题分类助手，只返回JSON格式的判断结果。"},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}, # <--- 开启 JSON 模式
                "temperature": 0.3
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"  ⚠️ DeepSeek API 错误，状态码: {response.status_code}")
            return None

        result_text = response.json()['choices'][0]['message']['content'].strip()
        result = json.loads(result_text)
        return result

    except Exception as e:
        print(f"  ⚠️ AI 判断异常: {e}")
        return None


def main():
    """主流程：日期筛选 → 正文提取 → AI 主题分类 → 输出结果"""

    # ========== 日期筛选 ==========
    print()
    print("=" * 60)
    print("开始日期筛选")
    print("=" * 60)
    print()

    start_date = input("请输入起始日期（格式 YYYY-MM-DD，如 2026-04-01）：").strip()
    end_date = input("请输入结束日期（格式 YYYY-MM-DD，如 2026-04-30）：").strip()

    dated_articles = get_articles_by_date(start_date, end_date)

    if not dated_articles:
        print("\n日期区间内无文章，流程结束。")
        return

    # ========== 主题筛选 ==========
    current_headers = utils.get_headers()
    foreign_affairs_articles = []

    print()
    print("=" * 60)
    print("开始主题筛选")
    print("=" * 60)

    print(f"\n共 {len(dated_articles)} 篇文章待筛选\n")

    for i, article in enumerate(dated_articles):
        title = article['title']
        url = article['url']
        account = article['account']
        date = article['date']

        print(f"[{i+1}/{len(dated_articles)}] 正在处理: {title}")

        # 第一步：抓取文章正文
        text = extract_article_text(url, current_headers)
        if not text:
            print(f"  ⏭️ 跳过（无法提取正文）\n")
            continue

        # 第二步：AI 判断主题
        result = judge_foreign_affairs(title, text)

        if result and result.get('is_foreign_affairs'):
            foreign_affairs_articles.append({
                'title': title,
                'account': account,
                'date': date,
                'url': url
            })
            print(f"  ✅ 外事相关 - {result.get('reason', '')}")
        elif result:
            print(f"  ❌ 非外事 - {result.get('reason', '')}")
        else:
            print(f"  ⏭️ 跳过（AI 判断失败）")

        # 请求间隔，模拟人类阅读行为，避免被限流
        time.sleep(random.uniform(1.5, 4.0))
        print()

    # ========== 输出结果 ==========
    print("=" * 60)
    print(f"筛选完成！共 {len(foreign_affairs_articles)} 篇外事相关文章：")
    print("=" * 60)

    for article in foreign_affairs_articles:
        print(f"  [{article['date']}] {article['account']}")
        print(f"  {article['title']}")
        # print(f"  {article['url']}")
        print()

    # 保存筛选结果到本地临时文件（已被 .gitignore 忽略）
    storage.save_filter_result(foreign_affairs_articles)
    print(f"结果已保存到 data/filter_result.json（共 {len(foreign_affairs_articles)} 篇）")


if __name__ == "__main__":
    main()
