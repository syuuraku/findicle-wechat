import requests
import utils
import storage
from bs4 import BeautifulSoup
import time
import random
import json
import os
import yaml
from config import DEEPSEEK_API_KEY

# ========== 主题配置相关 ==========

TOPICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "topics")


def list_topics():
    """列出 topics/ 目录下所有可用的主题配置文件

    Returns:
        [(文件路径, 主题名称), ...] 的列表
    """
    topics = []
    if not os.path.exists(TOPICS_DIR):
        return topics

    for filename in sorted(os.listdir(TOPICS_DIR)):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(TOPICS_DIR, filename)
            topic = load_topic(filepath)
            topics.append((filepath, topic['name'], filename))
    return topics


def load_topic(topic_file):
    """加载 YAML 主题配置文件

    Args:
        topic_file: YAML 文件路径

    Returns:
        {'name': '主题名', 'categories': ['类别1', '类别2', ...]}
    """
    with open(topic_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def select_topic():
    """交互式菜单：让用户选择一个主题配置

    Returns:
        加载后的主题字典 {'name': ..., 'categories': [...]}
    """
    topics = list_topics()

    if not topics:
        print("⚠️ topics/ 目录下没有找到任何主题配置文件（.yaml）。")
        print("请参考 README.md 创建主题配置。")
        return None

    print("请选择筛选主题：")
    print()
    for i, (filepath, name, filename) in enumerate(topics):
        print(f"  {i + 1}. {name} ({filename})")
    print()

    while True:
        choice = input(f"请输入编号（1-{len(topics)}）：").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(topics):
            selected = topics[int(choice) - 1]
            topic = load_topic(selected[0])
            print(f"\n已选择主题：{topic['name']}")
            return topic
        print(f"  ⚠️ 无效输入，请输入 1 到 {len(topics)} 之间的数字。")


# ========== 日期筛选 ==========

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


# ========== 正文提取 ==========

def extract_article_text(url):
    """直接请求微信文章页面，提取正文纯文本（前800字）"""
    try:
        headers = utils.get_wechat_headers()
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
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


# ========== AI 主题分类 ==========

def build_prompt(topic, title, text):
    """根据主题配置动态构建分类 prompt

    Args:
        topic: 主题字典 {'name': ..., 'categories': [...]}
        title: 文章标题
        text:  文章正文（前800字）

    Returns:
        构建好的 prompt 字符串
    """
    topic_name = topic['name']
    categories_text = "\n".join(f"- {c}" for c in topic['categories'])

    return f"""请判断以下文章是否属于"{topic_name}"主题。{topic_name}主题包括但不限于：
{categories_text}

文章标题：{title}

文章正文（前800字）：
{text}

请只返回以下JSON格式，不要输出其他内容：
{{"is_match": true/false, "reason": "简要原因"}}"""


def classify_article(topic, title, text):
    """调用 DeepSeek API 判断文章是否匹配指定主题

    Args:
        topic: 主题字典 {'name': ..., 'categories': [...]}
        title: 文章标题
        text:  文章正文（前800字）

    Returns:
        {'is_match': True/False, 'reason': '...'} 或 None（失败时）
    """
    prompt = build_prompt(topic, title, text)

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


# ========== 主流程 ==========

def main():
    """主流程：主题选择 → 日期筛选 → 正文提取 → AI 主题分类 → 输出结果"""

    # ========== 主题选择 ==========
    print()
    print("=" * 60)
    print("选择筛选主题")
    print("=" * 60)
    print()

    topic = select_topic()
    if not topic:
        return

    topic_name = topic['name']

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
    matched_articles = []

    print()
    print("=" * 60)
    print(f"开始主题筛选（{topic_name}）")
    print("=" * 60)

    print(f"\n共 {len(dated_articles)} 篇文章待筛选\n")

    for i, article in enumerate(dated_articles):
        title = article['title']
        url = article['url']
        account = article['account']
        date = article['date']

        print(f"[{i+1}/{len(dated_articles)}] 正在处理: {title}")

        # 第一步：抓取文章正文
        text = extract_article_text(url)
        if not text:
            print(f"  ⏭️ 跳过（无法提取正文）\n")
            continue

        # 第二步：AI 判断主题
        result = classify_article(topic, title, text)

        if result and result.get('is_match'):
            matched_articles.append({
                'title': title,
                'account': account,
                'date': date,
                'url': url
            })
            print(f"  ✅ {topic_name}相关 - {result.get('reason', '')}")
        elif result:
            print(f"  ❌ 非{topic_name} - {result.get('reason', '')}")
        else:
            print(f"  ⏭️ 跳过（AI 判断失败）")

        # 请求间隔，模拟人类阅读行为，避免被限流
        time.sleep(random.uniform(1.5, 4.0))
        print()

    # ========== 输出结果 ==========
    print("=" * 60)
    print(f"筛选完成！共 {len(matched_articles)} 篇{topic_name}相关文章：")
    print("=" * 60)

    for article in matched_articles:
        print(f"  [{article['date']}] {article['account']}")
        print(f"  {article['title']}")
        # print(f"  {article['url']}")
        print()

    # 保存筛选结果到本地临时文件（已被 .gitignore 忽略）
    storage.save_filter_result(matched_articles)
    print(f"结果已保存到 data/filter_result.json（共 {len(matched_articles)} 篇）")


if __name__ == "__main__":
    main()
