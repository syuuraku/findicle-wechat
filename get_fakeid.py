import requests
import utils

# 存放最终的公众号信息列表
account_list = []

# 传入文章url
article_url = [
    "https://mp.weixin.qq.com/s/MnEBLlFtfLtgziRAf5hzUA",
    "https://mp.weixin.qq.com/s/BAmZloPZSeSzqB7nsAJyWg"
]


def fetch_fakeids():
    """根据文章URL获取公众号fakeid，结果存入 account_list"""
    # 如果需要手动更新 key，可以在这里传入，或者直接修改 config.py
    current_headers = utils.get_headers()

    piece_url = [f'https://down.mptext.top/api/public/v1/accountbyurl?url={url}' for url in article_url]

    for piece in piece_url:
        piece_response = requests.get(piece, headers=current_headers, timeout=10)
        piece_data = piece_response.json().get('list', [])

        if piece_response.status_code == 200 and piece_data:
            for item in piece_data:
                account_list.append({"nickname": item.get('nickname'), "fakeid": item.get('fakeid')})
                print(f"添加成功：{item.get('nickname')}")
        else:
            print(f"提取{piece}失败，状态码：{piece_response.status_code}")

    print(f"\n共添加{len(account_list)}个公众号")
    print()
    return account_list


if __name__ == "__main__":
    fetch_fakeids()

