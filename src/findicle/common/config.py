"""
项目配置

从项目根目录的 .env 文件加载敏感配置（API 密钥等）。
使用前请复制 .env.example 为 .env 并填入你自己的参数。
"""

import os
from dotenv import load_dotenv

# 项目根目录（src/findicle/common/config.py 向上四层）
PROJECT_ROOT = os.path.dirname(       # article_in_wechat/
    os.path.dirname(                   # src/
        os.path.dirname(               # findicle/
            os.path.dirname(           # common/
                os.path.abspath(__file__)  # config.py
            )
        )
    )
)

# 从项目根目录加载 .env
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# 第三方 API
X_AUTH_KEY = os.getenv("X_AUTH_KEY", "")

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# Notion
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
