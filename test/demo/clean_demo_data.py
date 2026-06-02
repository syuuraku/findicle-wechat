"""
清空 demo 测试数据

用法:
    python clean_demo_data.py

说明:
    删除 demo_account.json、demo_article.json 和 demo_filter_result.json（如果存在）
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILES_TO_CLEAN = [
    os.path.join(SCRIPT_DIR, "demo_account.json"),
    os.path.join(SCRIPT_DIR, "demo_article.json"),
    os.path.join(SCRIPT_DIR, "demo_filter_result.json"),
]


def clean():
    print("=" * 40)
    print(" " * 10 + "清理 demo 数据")
    print("=" * 40)
    print()

    cleaned = 0
    for filepath in FILES_TO_CLEAN:
        filename = os.path.basename(filepath)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"  [✓] 已删除 {filename}")
            cleaned += 1
        else:
            print(f"  [–] {filename} 不存在，跳过")

    print()
    print(f"清理完成，共删除 {cleaned} 个文件。")


if __name__ == "__main__":
    clean()
