"""
Notion 同步模块

将 filter_articles.py 的筛选结果写入 Notion 数据库「院系外事收集」。
直接调用 Notion 官方 REST API（裸 requests，与项目里 DeepSeek 调用风格一致），
不依赖 notion-client SDK。

使用前提（见 config.example.py）：
  1. 在 Notion 建一个 internal integration，拿到 token；
  2. 在目标数据库 ··· → Connections 里把该 integration 分享进去；
  3. 在 .env 填写 NOTION_TOKEN 与 NOTION_DATABASE_ID。

字段映射（院系外事收集）：
  标题(title) ← title，作者(text) ← account，日期(date) ← date，
  网址(url) ← url，理由(text) ← reason
  「类型」「合辑」暂留空，由人工在 Notion 标注。
"""

import time
import requests
from findicle.common.config import NOTION_TOKEN, NOTION_DATABASE_ID

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"


def _build_properties(article):
    """把一篇文章映射成 Notion 数据库的 properties 字典"""
    properties = {
        "标题": {"title": [{"text": {"content": article.get("title", "")}}]},
        "作者": {"rich_text": [{"text": {"content": article.get("account", "")}}]},
    }
    # 日期：我们的 date 是 "YYYY-MM-DD"，本身就是合法 ISO-8601 date
    date = article.get("date")
    if date:
        properties["日期"] = {"date": {"start": date}}
    url = article.get("url")
    if url:
        properties["网址"] = {"url": url}
    reason = article.get("reason")
    if reason:
        properties["理由"] = {"rich_text": [{"text": {"content": reason}}]}
    return properties


def _create_page(article, max_retries=3):
    """在 Notion 数据库创建一篇文章对应的 page

    对 429 / 5xx / 网络异常做指数退避重试（1s→2s→4s）；
    4xx（除 429）等永久错误直接返回 False，不重试。

    Returns:
        True 创建成功；False 失败
    """
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": _build_properties(article),
    }
    title = article.get("title", "")

    for attempt in range(max_retries):
        # 仅当后面还有重试机会时才退避等待
        def backoff(note):
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"  ⚠️ {note}，{wait}s 后重试（{attempt + 1}/{max_retries}）：{title}")
                time.sleep(wait)

        try:
            resp = requests.post(NOTION_API_URL, headers=headers, json=payload, timeout=30)

            # 限速 / 服务端错误：可恢复，退避后重试
            if resp.status_code == 429 or resp.status_code >= 500:
                backoff(f"Notion 暂时不可用（{resp.status_code}）")
                continue

            # 其余非 200（400/401/403/404 等）：配置或数据问题，重试无意义
            if resp.status_code != 200:
                print(f"  ⚠️ Notion API 错误 {resp.status_code}（不重试）：{title}")
                print(f"     {resp.text[:300]}")
                return False

            return True

        except (requests.Timeout, requests.ConnectionError) as e:
            backoff(f"网络异常（{e}）")
            continue

    print(f"  ⚠️ 重试 {max_retries} 次仍失败：{title}")
    return False


def push_to_notion(articles, topic_name=""):
    """将筛选结果逐篇写入 Notion 数据库

    Args:
        articles: 文章列表，每项含 title/account/date/url
        topic_name: 主题名，仅用于日志展示

    Returns:
        (成功数, 失败数)
    """
    # 配置校验：缺 token / database id 直接提示，不硬闯
    if not NOTION_TOKEN or NOTION_TOKEN.startswith("YOUR_"):
        print("⚠️ 未配置 NOTION_TOKEN（见 .env / .env.example），跳过 Notion 写入。")
        return (0, len(articles))
    if not NOTION_DATABASE_ID or NOTION_DATABASE_ID.startswith("YOUR_"):
        print("⚠️ 未配置 NOTION_DATABASE_ID（见 .env / .env.example），跳过 Notion 写入。")
        return (0, len(articles))

    total = len(articles)
    print(f"\n开始写入 Notion（共 {total} 篇）...\n")

    success, failed = 0, 0
    for i, article in enumerate(articles):
        title = article.get("title", "")
        print(f"[{i + 1}/{total}] 写入：{title}")
        if _create_page(article):
            success += 1
        else:
            failed += 1
        # Notion 官方限速约 3 请求/秒，逐篇稍作间隔更稳；最后一篇无需再等
        if i < total - 1:
            time.sleep(0.4)

    print()
    print(f"📤 Notion 写入完成：成功 {success} 篇，失败 {failed} 篇。")
    if failed:
        print("   失败的文章未写入，可检查上方错误后重跑。")
    return (success, failed)
