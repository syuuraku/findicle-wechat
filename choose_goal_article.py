import requests

# 这是一个模拟微信内置浏览器的UA字符串示例
WECHAT_USER_AGENT = "Mozilla/5.0 (Linux; Android 10; Redmi K30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36 MicroMessenger/8.0.16.2040(0x28000056)"

article_url = "https://down.mptext.top/api/public/v1/account?keyword=中山大学"

headers = {
    "User-Agent": WECHAT_USER_AGENT,
    "X-Auth-Key": "09fd22be77464314931166f2becdea7a"
}


response = requests.get(article_url, headers=headers)

print(f"status code:{response.status_code}")
print(response.json())
