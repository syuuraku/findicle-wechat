"""
主题配置加载与选择

管理 topics/ 目录下的 YAML 主题配置文件。
"""

import os
import yaml
from findicle.common.config import PROJECT_ROOT

TOPICS_DIR = os.path.join(PROJECT_ROOT, "topics")


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
