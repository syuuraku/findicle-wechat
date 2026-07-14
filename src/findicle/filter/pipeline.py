"""
筛选主流程

主题选择 → 日期筛选 → 正文提取 → AI 主题分类 → 输出结果
"""

import os
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor

from findicle.common import storage
from findicle.filter.topics import select_topic
from findicle.filter.extractor import extract_article_text
from findicle.filter.classifier import classify_article, CLASSIFY_WORKERS


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

    # 保存待筛选文章列表到 data/filter/，文件名为日期区间
    os.makedirs(storage.FILTER_DIR, exist_ok=True)
    dated_file = os.path.join(storage.FILTER_DIR, f"{start_date}_{end_date}.json")
    with open(dated_file, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f"待筛选文章已保存到 {dated_file}")

    return filtered


# ========== 结果去向（筛选完成后由用户选择） ==========

def select_output_destination():
    """交互式菜单：让用户选择筛选结果的去向

    Returns:
        'notion'：传入 Notion；'local'：存入本地 JSON + Excel
    """
    print()
    print("请选择筛选结果的去向：")
    print()
    print("  1. 传入 Notion")
    print("  2. 存入本地（data/filter_result.json 和 data/filter_result.xlsx）")
    print()

    while True:
        choice = input("请输入编号（1-2）：").strip()
        if choice == '1':
            return 'notion'
        if choice == '2':
            return 'local'
        print("  ⚠️ 无效输入，请输入 1 或 2。")


def save_to_local(articles, topic_name):
    """将筛选结果存入本地 data/filter_result.json 和 data/filter_result.xlsx"""
    storage.save_filter_result(articles)
    print(f"结果已保存到 data/filter_result.json（共 {len(articles)} 篇）")

    from findicle.output.excel import export_to_excel
    export_to_excel(articles, topic_name)


def export_to_notion(articles, topic_name):
    """将筛选结果写入 Notion 数据库「院系外事收集」（见 notion_sync 模块）"""
    from findicle.output.notion import push_to_notion
    push_to_notion(articles, topic_name)


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

    dated_file = os.path.join(storage.FILTER_DIR, f"{start_date}_{end_date}.json")
    if os.path.exists(dated_file):
        with open(dated_file, 'r', encoding='utf-8') as f:
            dated_articles = json.load(f)
        print(f"已找到缓存文件 {dated_file}，直接加载 {len(dated_articles)} 篇文章")
    else:
        dated_articles = get_articles_by_date(start_date, end_date)

    if not dated_articles:
        print("\n日期区间内无文章，流程结束。")
        return

    # ========== 主题筛选 ==========
    matched_articles = []
    undetermined = []  # API 硬失败（重试用尽）的文章，单独导出供复核，绝不静默丢弃

    print()
    print("=" * 60)
    print(f"开始主题筛选（{topic_name}）")
    print("=" * 60)

    total = len(dated_articles)
    print(f"\n共 {total} 篇文章待筛选\n")

    # 抓取（单线程串行 + 间隔，防封）与 AI 分类（线程池并行）流水线：
    # 主线程逐篇抓正文，抓到一篇就把分类任务丢进线程池后台并行跑，
    # 这样 AI 判断耗时被抓取间隔覆盖掉，总耗时基本只剩「抓取 + 间隔」一条线。
    classify_jobs = []  # [(article, future), ...] 按文章顺序保存

    with ThreadPoolExecutor(max_workers=CLASSIFY_WORKERS) as executor:
        for i, article in enumerate(dated_articles):
            title = article['title']
            url = article['url']

            print(f"[{i+1}/{total}] 抓取正文: {title}")

            # 第一步：抓取文章正文（串行，限流只针对微信）
            text = extract_article_text(url)
            if not text:
                print(f"  ⏭️ 跳过（无法提取正文）")
            else:
                # 第二步：提交 AI 分类任务到线程池并行执行（不阻塞抓取）
                future = executor.submit(classify_article, topic, title, text)
                classify_jobs.append((article, future))

            # 抓取间隔：只绑定微信抓取，DeepSeek 调用后不睡；最后一篇无需再等
            if i < total - 1:
                time.sleep(random.uniform(1.0, 2.0))

        # 抓取全部完成，按文章顺序收集 AI 分类结果（多数已在后台跑完）
        print(f"\n抓取完成，等待 AI 分类结果...\n")
        for article, future in classify_jobs:
            title = article['title']
            result = future.result()

            if result and result.get('is_match'):
                matched_articles.append({
                    'title': title,
                    'account': article['account'],
                    'date': article['date'],
                    'url': article['url'],
                    'reason': result.get('reason', '')
                })
                print(f"  ✅ {title}\n     {topic_name}相关 - {result.get('reason', '')}")
            elif result:
                print(f"  ❌ {title}\n     非{topic_name} - {result.get('reason', '')}")
            else:
                # AI 没能判断（API 硬失败）≠ 不匹配：记入待复核，不丢弃
                undetermined.append({
                    'title': title,
                    'account': article['account'],
                    'date': article['date'],
                    'url': article['url'],
                    'reason': 'API 请求失败（重试用尽），未判断'
                })
                print(f"  ⚠️ {title}\n     未判断（API 请求失败）→ 已记入待复核")

    # ========== 输出结果 ==========
    print("=" * 60)
    print(f"筛选完成！共 {len(matched_articles)} 篇{topic_name}相关文章：")
    print("=" * 60)

    for article in matched_articles:
        print(f"  [{article['date']}] {article['account']}")
        print(f"  {article['title']}")
        # print(f"  {article['url']}")
        print()

    # 由用户决定结果去向：传入 Notion，或存入本地 JSON + Excel
    destination = select_output_destination()
    if destination == 'notion':
        export_to_notion(matched_articles, topic_name)
    else:
        save_to_local(matched_articles, topic_name)

    # 未判断（API 硬失败）文章：无论结果去向如何，始终单独导出到本地，
    # 供复核 / 重跑，避免需要的文章被静默丢弃
    if undetermined:
        from findicle.output.excel import export_to_excel
        undetermined_file = os.path.join(
            storage.FILTER_DIR, f"{start_date}_{end_date}_undetermined.xlsx"
        )
        export_to_excel(
            undetermined, f"{topic_name}-未判断", output_file=undetermined_file
        )
        print()
        print(f"⚠️ 有 {len(undetermined)} 篇因 API 请求失败未能判断，已存到：")
        print(f"   {undetermined_file}")
        print("   这些文章可能包含你需要的内容，建议复核，或稍后重跑这一批补救。")


if __name__ == "__main__":
    main()
