import requests
from bs4 import BeautifulSoup
import utils

current_headers = utils.get_headers()

url = "https://mp.weixin.qq.com/s/MnEBLlFtfLtgziRAf5hzUA"

response = requests.get(url, headers=current_headers, timeout=15)
response.encoding = 'utf-8'

print(f"状态码: {response.status_code}")
print(f"HTML 总长度: {len(response.text)} 字符\n")

# 保存原始 HTML 供查看
with open("raw_article.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("✅ 原始 HTML 已保存到 raw_article.html\n")

# 解析正文区域（微信文章正文通常在 id="js_content" 的 div 里）
soup = BeautifulSoup(response.text, 'html.parser')
content_div = soup.find(id='js_content')

if content_div:
    # 方式1：直接 get_text
    plain_text = content_div.get_text(separator='\n', strip=True)
    
    print("=" * 60)
    print("【get_text() 提取的纯文本 - 前 1500 字】")
    print("=" * 60)
    print(plain_text[:1500])
    print(f"\n... (纯文本总长度: {len(plain_text)} 字符)")
    
    # 保存纯文本
    with open("plain_text.txt", "w", encoding="utf-8") as f:
        f.write(plain_text)
    print("✅ 纯文本已保存到 plain_text.txt\n")
    
    # 方式2：看看正文区域有哪些标签类型（分析噪音来源）
    print("=" * 60)
    print("【正文区域的 HTML 标签统计】")
    print("=" * 60)
    tag_count = {}
    for tag in content_div.find_all(True):
        name = tag.name
        tag_count[name] = tag_count.get(name, 0) + 1
    for tag_name, count in sorted(tag_count.items(), key=lambda x: -x[1]):
        print(f"  <{tag_name}>: {count} 个")
    
    # 方式3：看看有哪些外部链接（秀米等）
    print(f"\n{'=' * 60}")
    print("【正文中的外部链接】")
    print("=" * 60)
    links = content_div.find_all('a', href=True)
    for link in links[:20]:
        href = link.get('href', '')
        text = link.get_text(strip=True)[:50]
        print(f"  文本: {text or '(空)'}")
        print(f"  链接: {href[:100]}")
        print()
else:
    print("⚠️ 未找到 id='js_content' 的正文区域")
    print("可能原因：微信文章需要在微信客户端内打开，或页面结构已变化")
    print("\n页面 title:", soup.title.string if soup.title else "无")
    # 打印前2000字符的HTML看看实际返回了什么
    print("\n--- 页面 HTML 前 2000 字符 ---")
    print(response.text[:2000])
