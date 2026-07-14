"""
微信文章正文提取

直接请求微信文章页面，用 BeautifulSoup 提取正文纯文本。
"""

import requests
from bs4 import BeautifulSoup
from findicle.common.utils import get_wechat_headers


def extract_article_text(url):
    """直接请求微信文章页面，提取正文纯文本（前800字）"""
    try:
        headers = get_wechat_headers()
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
