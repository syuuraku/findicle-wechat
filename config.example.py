# 配置文件模板，使用时请复制为 config.py 并填写你自己的参数
X_AUTH_KEY = "YOUR_X_AUTH_KEY_HERE"

# DeepSeek API 配置
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY_HERE"

# Notion API 配置
# NOTION_TOKEN：Notion internal integration 的 token（建 integration 后获取，
#   并在目标数据库 ··· → Connections 里把该 integration 分享进去，否则 API 无权限写入）
# NOTION_DATABASE_ID：目标数据库 id（数据库 URL 里 ? 前那段 32 位十六进制）
NOTION_TOKEN = "YOUR_NOTION_TOKEN_HERE"
NOTION_DATABASE_ID = "YOUR_NOTION_DATABASE_ID_HERE"
