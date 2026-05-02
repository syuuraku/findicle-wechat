import requests
import utils
import json
import os

URLS_FILE = "urls.txt"
ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    """从本地 JSON 文件加载已有公众号列表"""
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_accounts(accounts):
    """将公众号列表保存到本地 JSON 文件"""
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)

def fetch_fakeids():
    print("=" * 60)
    print(" " * 20 + "开始检查公众号库")
    print("=" * 60)
    print()
    """读取本地URL获取公众号fakeid，更新到 accounts.json，并返回完整公众号列表"""
    # 1. 加载本地已有库
    account_list = load_accounts()
    existing_fakeids = {acc['fakeid'] for acc in account_list}
    print(f"从本地加载了 {len(account_list)} 个公众号信息")
    print() 
    
    # 2. 读取 urls.txt
    urls = []
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    
    if not urls:
        print("未在 urls.txt 中发现有效的待解析链接。")
        return account_list

    # 3. 爬取新链接的公众号信息
    current_headers = utils.get_headers()
    new_count = 0
    
    piece_url = [f'https://down.mptext.top/api/public/v1/accountbyurl?url={url}' for url in urls]

    for piece in piece_url:
        try:
            piece_response = requests.get(piece, headers=current_headers, timeout=10)
            piece_data = piece_response.json().get('list', [])

            if piece_response.status_code == 200 and piece_data:
                for item in piece_data:
                    fakeid = item.get('fakeid')
                    nickname = item.get('nickname')
                    if fakeid in existing_fakeids:
                        print(f"  [跳过重复] {nickname}（已在库中）")
                    else:
                        account_list.append({"nickname": nickname, "fakeid": fakeid})
                        existing_fakeids.add(fakeid)
                        new_count += 1
                        print(f"  [+] 新增公众号: {nickname}")
            else:
                print(f"提取 {piece} 失败，状态码：{piece_response.status_code}")
        except Exception as e:
            print(f"请求 {piece} 时发生错误: {e}")

    # 4. 如果有新增则保存
    if new_count > 0:
        save_accounts(account_list)
        print(f"\n本次新增 {new_count} 个公众号，库中总计 {len(account_list)} 个公众号已保存。")
    else:
        print("\n本次没有新增公众号。")
        
    print()
    return account_list

if __name__ == "__main__":
    fetch_fakeids()

