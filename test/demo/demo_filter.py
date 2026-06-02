"""
Demo: 从 demo_article.json 筛选文章（日期筛选 + 正文提取 + AI 主题判断）

用法:
    python demo_filter.py

说明:
    - 从 demo_article.json 读取文章列表（需先运行 demo_fakeid_and_articles.py 生成）
    - 通过 input() 输入起止日期进行日期筛选
    - 逐篇提取正文，调用 DeepSeek API 判断是否属于外事主题
    - 结果保存到 demo_filter_result.json
    - 自包含，不依赖项目根目录的业务模块
"""

import sys
import os
import requests
import random
import json
import time
from bs4 import BeautifulSoup

# --------------- 配置 ---------------
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from config import X_AUTH_KEY, DEEPSEEK_API_KEY
except ImportError:
    X_AUTH_KEY = "请在此处填写你的 X-Auth-Key"
    DEEPSEEK_API_KEY = "请在此处填写你的 DeepSeek API Key"
    print("[警告] 未能导入 config.py，请确认 API Key 已正确设置")

# 数据文件路径（与脚本同目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_ARTICLE_FILE = os.path.join(SCRIPT_DIR, "demo_article.json")
DEMO_FILTER_RESULT_FILE = os.path.join(SCRIPT_DIR, "demo_filter_result.json")


# ============================================================
#  工具函数
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


def load_demo_articles():
    """从 demo_article.json 加载文章列表"""
    if os.path.exists(DEMO_ARTICLE_FILE):
        with open(DEMO_ARTICLE_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []


def save_json(filepath, data):
    """将数据保存为 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [✓] 已保存到 {os.path.basename(filepath)}")


# ============================================================
#  Step 1: 日期筛选
# ============================================================

def get_articles_by_date(articles, start_date, end_date):
    """根据日期区间筛选文章（闭区间 [start_date, end_date]）"""
    filtered = [a for a in articles if start_date <= a['date'] <= end_date]
    print(f"从 {len(articles)} 篇文章中筛选出 {len(filtered)} 篇（{start_date} ~ {end_date}）")
    return filtered


# ============================================================
#  Step 2: 正文提取
# ============================================================

def extract_article_text(url, headers):
    """抓取微信文章页面，提取正文纯文本（前800字）"""
    try:
        response = requests.get(
            f'https://down.mptext.top/api/public/v1/download?url={url}',
            headers=headers,
            timeout=15
        )
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


# ============================================================
#  Step 3: AI 主题判断
# ============================================================

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
                "response_format": {"type": "json_object"},
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


# ============================================================
#  主入口
# ============================================================

def main():
    # 1. 加载 demo_article.json
    articles = load_demo_articles()
    if not articles:
        print("[错误] demo_article.json 不存在或为空，请先运行 demo_fakeid_and_articles.py")
        sys.exit(1)

    print()
    print("=" * 60)
    print(" " * 18 + "Demo 文章筛选")
    print("=" * 60)
    print(f"\n从 demo_article.json 加载了 {len(articles)} 篇文章\n")

    # 2. 输入日期区间
    start_date = input("请输入起始日期（格式 YYYY-MM-DD，如 2026-04-01）：").strip()
    end_date = input("请输入结束日期（格式 YYYY-MM-DD，如 2026-04-30）：").strip()

    print()
    print("=" * 60)
    print("开始日期筛选")
    print("=" * 60)
    print()

    dated_articles = get_articles_by_date(articles, start_date, end_date)

    if not dated_articles:
        print("\n日期区间内无文章，流程结束。")
        return

    # 3. 主题筛选
    current_headers = get_headers()
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

        # 提取正文
        text = extract_article_text(url, current_headers)
        if not text:
            print(f"  ⏭️ 跳过（无法提取正文）\n")
            continue

        # AI 判断主题
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

        # 请求间隔，避免被限流
        time.sleep(random.uniform(1.5, 4.0))
        print()

    # 4. 输出结果
    print("=" * 60)
    print(f"筛选完成！共 {len(foreign_affairs_articles)} 篇外事相关文章：")
    print("=" * 60)

    for article in foreign_affairs_articles:
        print(f"  [{article['date']}] {article['account']}")
        print(f"  {article['title']}")
        print()

    # 5. 保存筛选结果
    save_json(DEMO_FILTER_RESULT_FILE, foreign_affairs_articles)
    print(f"结果已保存到 {os.path.basename(DEMO_FILTER_RESULT_FILE)}（共 {len(foreign_affairs_articles)} 篇）")


if __name__ == "__main__":
    main()
