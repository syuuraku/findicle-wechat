"""
统一的数据文件读写模块

集中管理所有数据文件的路径与读写操作，避免路径硬编码和函数重复定义。
"""

import json
import os

# ========== 数据文件路径常量 ==========
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
ARTICLES_FILE = os.path.join(DATA_DIR, "articles.json")
URLS_FILE = os.path.join(DATA_DIR, "urls.txt")
FILTER_RESULT_FILE = os.path.join(DATA_DIR, "filter_result.json")


def _ensure_data_dir():
    """确保 data 目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)

# ========== URLs ==========

def load_urls():
    """从 urls.txt 加载待解析链接列表"""
    urls = []
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    return urls


# ========== 公众号 (accounts) ==========

def load_accounts():
    """从本地 JSON 文件加载已有公众号列表"""
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_accounts(accounts):
    """将公众号列表保存到本地 JSON 文件"""
    _ensure_data_dir()
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)


# ========== 文章 (articles) ==========

def load_articles():
    """从本地 JSON 文件加载已有文章列表"""
    if os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    return []


def save_articles(articles):
    """将文章列表保存到本地 JSON 文件"""
    _ensure_data_dir()
    with open(ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)





# ========== 筛选结果 ==========

def save_filter_result(articles):
    """保存筛选结果到本地临时文件"""
    _ensure_data_dir()
    with open(FILTER_RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
