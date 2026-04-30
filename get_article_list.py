import requests
from datetime import datetime
import utils
import get_fakeid 

# 如果需要手动更新 key，可以在这里传入，或者直接修改 config.py
current_headers = utils.get_headers()

# 从get_fakeid.py中获取公众号列表
account_list = get_fakeid.account_list

# 获取公众号【全部】文章列表
all_articles = []

for account in account_list:
    current_fakeid = account['fakeid']
    current_nickname = account['nickname']
    print(f"准备爬取公众号：{current_nickname}")

    list_url = f'https://down.mptext.top/api/public/v1/article?fakeid={current_fakeid}&begin=0&size=20'

    list_response = requests.get(list_url, headers=current_headers, timeout=10)
    list_data = list_response.json().get('articles', [])

    if list_response.status_code == 200 and list_data:
        print(f"--- 正在提取【{current_nickname}】的文章 ---")
        for item in list_data:
            title = item.get('title')
            url = item.get('link')
            timestamp = item.get('create_time')
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

            all_articles.append({
                'account': current_nickname,
                'title': title,
                'url': url,
                'date': date
            })
            print(f"  [+] {title} ({date})")

    else:
        print(f"提取【{current_nickname}】失败，状态码: {list_response.status_code}")

print(f"\n共提取到 {len(all_articles)} 篇文章")
print()
