import random
from config import X_AUTH_KEY


# 微信内置浏览器 User-Agent 列表（用于直接请求微信文章页面）
WECHAT_USER_AGENTS = [
    # Android - Samsung Galaxy S23 Ultra, 微信 8.0.48
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36 MMWEBID/2455 MicroMessenger/8.0.48.2580(0x28003036) Process/toolsmp WeChat/arm64 WeChatLib/OKLNE/2024.03.25 Language/zh_CN ABI/arm64",
    # Android - Google Pixel 7, 微信 8.0.47
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36 MMWEBID/3188 MicroMessenger/8.0.47.2560(0x28002F34) Process/toolsmp WeChat/arm64 WeChatLib/OKLNE/2024.02.18 Language/zh_CN ABI/arm64",
    # Android - HUAWEI P60 Pro, 微信 8.0.49
    "Mozilla/5.0 (Linux; Android 14; HUAWEI P60 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36 MMWEBID/1876 MicroMessenger/8.0.49.2600(0x28003138) Process/toolsmp WeChat/arm64 WeChatLib/OKLNE/2024.05.10 Language/zh_CN ABI/arm64",
    # Android - Xiaomi Redmi Note 12 Pro, 微信 8.0.46
    "Mozilla/5.0 (Linux; Android 13; 22101316C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.80 Mobile Safari/537.36 MMWEBID/4021 MicroMessenger/8.0.46.2540(0x28002E2C) Process/toolsmp WeChat/arm64 WeChatLib/OKLNE/2024.01.15 Language/zh_CN ABI/arm64",
    # Android - OPPO Find X6 Pro, 微信 8.0.50
    "Mozilla/5.0 (Linux; Android 14; PGEM10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.53 Mobile Safari/537.36 MMWEBID/5532 MicroMessenger/8.0.50.2620(0x2800323C) Process/toolsmp WeChat/arm64 WeChatLib/OKLNE/2024.06.20 Language/zh_CN ABI/arm64",
    # iOS - iPhone 15 Pro Max, 微信 8.0.48
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302e) NetType/WIFI Language/zh_CN",
    # iOS - iPhone 14 Pro, 微信 8.0.49
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x18003130) NetType/4G Language/zh_CN",
    # iOS - iPhone 13, 微信 8.0.47
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002F2C) NetType/WIFI Language/zh_CN",
    # iOS - iPhone 15, 微信 8.0.50
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.50(0x1800323A) NetType/WIFI Language/zh_CN",
]


def get_wechat_headers():
    """获取模拟微信内置浏览器的请求头（用于直接请求微信文章页面）

    与 get_headers() 的区别：
    - 仅使用微信内置浏览器 UA
    - 带 Referer 头（微信域名）
    - 不包含 X-Auth-Key（那是给第三方 API 用的）
    """
    return {
        'User-Agent': random.choice(WECHAT_USER_AGENTS),
        'Referer': 'https://mp.weixin.qq.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }


def get_headers(auth_key=None):
    """
    获取模拟浏览器的请求头
    :param auth_key: 可选，手动传入最新的 X-Auth-Key。如果不传，则默认使用 config.py 中的配置。
    """
    # 如果调用时没传 auth_key，就用 config 里的
    current_key = auth_key if auth_key is not None else X_AUTH_KEY
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        # 模拟微信内置浏览器 (Android)
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36 MMWEBID/2455 MicroMessenger/8.0.48.2580(0x28003036) Process/toolsmp WeChat/arm64 WeChatLib/OKLNE/2024.03.25 Language/zh_CN ABI/arm64",
        # 模拟微信内置浏览器 (iOS)
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302e) NetType/WIFI Language/zh_CN"
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'X-Auth-Key': current_key
    }
    return headers
