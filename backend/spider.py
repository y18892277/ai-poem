import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

# 爬取的诗歌网址
urls = [
    'https://so.gushiwen.org/gushi/tangshi.aspx',
    'https://so.gushiwen.org/gushi/sanbai.aspx',
    'https://so.gushiwen.org/gushi/songsan.aspx',
    'https://so.gushiwen.org/gushi/songci.aspx'
]

poem_links = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}

# 获取所有诗歌链接
for url in urls:
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.text, "lxml")
    content = soup.find('div', class_="sons")
    if content:
        links = content.find_all('a')
        for link in links:
            href = link.get('href')
            if href and href.startswith('/shiwenv'):
                poem_links.append('https://so.gushiwen.org' + href)

poem_list = []

# 爬取单首诗歌内容的函数
def get_poem(url):
    try:
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "lxml")
        poem_div = soup.find('div', class_='contson')
        if poem_div:
            poem = poem_div.get_text(separator='', strip=True)
            # 清理文本
            poem = poem.replace(' ', '')
            # 去除一些无用的字符或注释（根据实际页面调整）
            poem = re.sub(r'\[.*?\]', '', poem)
            poem = poem.replace('!', '！').replace('?', '？')
            poem_list.append(poem)
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# 多线程爬取
executor = ThreadPoolExecutor(max_workers=10)
future_tasks = [executor.submit(get_poem, url) for url in poem_links]
wait(future_tasks, return_when=ALL_COMPLETED)

# 去重并排序
poems = list(set(poem_list))
poems.sort(key=len)

# 写入文件
with open('F://poem.txt', 'w', encoding='utf-8') as f:
    for poem in poems:
        # 去除多余符号
        clean_poem = poem.replace('《', '').replace('》', '') \
                         .replace('：', '').replace('“', '').replace('”', '')
        f.write(clean_poem + '\n\n')
        print(clean_poem)
