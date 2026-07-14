"""
AI 主题分类

使用 DeepSeek API 判断文章是否匹配指定主题。
"""

import time
import json
import requests
from findicle.common.config import DEEPSEEK_API_KEY

# DeepSeek 分类并发数（微信抓取仍单线程串行防封，仅 AI 判断并行）
CLASSIFY_WORKERS = 4


def build_prompt(topic, title, text):
    """根据主题配置动态构建分类 prompt

    Args:
        topic: 主题字典 {'name': ..., 'categories': [...], 'exclusions': [...], 'guidelines': [...]}
        title: 文章标题
        text:  文章正文（前800字）

    Returns:
        构建好的 prompt 字符串
    """
    topic_name = topic['name']
    categories_text = "\n".join(f"- {c}" for c in topic['categories'])

    principle = topic.get('principle', '')
    principle_line = f"\n{principle}\n" if principle else ""

    prompt = f"""请判断以下文章是否属于"{topic_name}"主题。
{principle_line}
符合"{topic_name}"的类别：
{categories_text}"""

    if 'exclusions' in topic:
        exclusions_text = "\n".join(f"- {e}" for e in topic['exclusions'])
        prompt += f"""

以下情况不属于"{topic_name}"（即使表面上涉及国际元素，也应判断为不符合）：
{exclusions_text}"""

    prompt += f"""

文章标题：{title}

文章正文（前800字）：
{text}

请只返回以下JSON格式，不要输出其他内容：
{{"is_match": true/false, "reason": "简要原因"}}"""

    return prompt


def classify_article(topic, title, text, max_retries=3):
    """调用 DeepSeek API 判断文章是否匹配指定主题

    对 429 / 5xx / 超时等瞬时错误做指数退避重试（最多 max_retries 次，
    1s→2s→4s）；4xx（除 429）、JSON 解析失败等永久错误直接返回 None。

    Args:
        topic: 主题字典 {'name': ..., 'categories': [...]}
        title: 文章标题
        text:  文章正文（前800字）
        max_retries: 瞬时错误的最大重试次数

    Returns:
        {'is_match': True/False, 'reason': '...'}；
        None 表示硬失败（重试用尽或永久错误），上层据此记入待复核
    """
    prompt = build_prompt(topic, title, text)

    for attempt in range(max_retries):
        # 仅当后面还有重试机会时才退避等待，最后一次失败不再空等
        def backoff(note):
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"  ⚠️ {note}，{wait}s 后重试（{attempt + 1}/{max_retries}）：{title}")
                time.sleep(wait)

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

            # 限速 / 服务端错误：可恢复，退避后重试
            if response.status_code == 429 or response.status_code >= 500:
                backoff(f"DeepSeek 暂时不可用（{response.status_code}）")
                continue

            # 其余非 200（如 400/401/402）：永久错误，重试无意义
            if response.status_code != 200:
                print(f"  ⚠️ DeepSeek API 错误，状态码: {response.status_code}（不重试）：{title}")
                return None

            result_text = response.json()['choices'][0]['message']['content'].strip()
            return json.loads(result_text)

        except (requests.Timeout, requests.ConnectionError) as e:
            # 网络抖动 / 超时：可恢复，退避后重试
            backoff(f"网络异常（{e}）")
            continue

        except Exception as e:
            # JSON 解析失败等：内容有问题，重试通常无用，直接判失败
            print(f"  ⚠️ AI 判断异常: {e}（不重试）：{title}")
            return None

    # 重试用尽仍未拿到结果，判为硬失败
    print(f"  ⚠️ 重试 {max_retries} 次仍失败：{title}")
    return None
