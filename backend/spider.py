import re
import requests
from bs4 import BeautifulSoup
import json # For JSON Lines output
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import time # For potential delays
import os # Import os module
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry # Corrected import for Retry

# 爬取的诗歌网址 (可以保持不变或按需调整)
urls = [
    'https://so.gushiwen.org/gushi/tangshi.aspx',
    'https://so.gushiwen.org/gushi/sanbai.aspx',
    'https://so.gushiwen.org/gushi/songsan.aspx',
    'https://so.gushiwen.org/gushi/songci.aspx'
]

poem_links = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': 'https://so.gushiwen.org' # Adding a referer might be polite
}

print("Fetching poem links...")

# Function to create a session with retry logic
def requests_retry_session(
    retries=5, # Increased retries
    backoff_factor=2, # Increased backoff_factor for more significant exponential delay
    status_forcelist=(500, 502, 503, 504, 408), # Added 408 Request Timeout
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(['GET', 'POST']) # Allow retries for POST if needed in future
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# 获取所有诗歌链接
for url_category in urls:
    try:
        # Use session for retries, increase timeout
        session = requests_retry_session()
        req = session.get(url_category, headers=headers, timeout=30) # Increased timeout
        req.raise_for_status() # Check for HTTP errors
        soup = BeautifulSoup(req.text, "lxml")
        # Sons div contains links to individual poems or further sub-categories
        sons_divs = soup.find_all('div', class_="sons")
        for sons_div in sons_divs:
            links = sons_div.find_all('a')
            for link in links:
                href = link.get('href')
                # Ensure it's a direct poem link
                if href and (href.startswith('/shiwenv_') or href.startswith('https://so.gushiwen.cn/shiwenv_')):
                    if href.startswith('/'):
                        poem_links.append('https://so.gushiwen.org' + href)
                    else:
                        poem_links.append(href)
        # time.sleep(0.5) # Removed, retry backoff will handle delays
    except requests.exceptions.RequestException as e:
        print(f"Error fetching category page {url_category}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred with {url_category}: {e}")


poem_links = list(set(poem_links)) # Remove duplicates
print(f"Found {len(poem_links)} unique poem links.")

# This list will store dictionaries, each representing a poem
structured_poem_list = []

# 爬取单首诗歌内容的函数
def get_poem_details(url):
    poem_data = {} # Initialize poem_data at the beginning of the function
    try:
        # print(f"Fetching details for: {url}")
        session = requests_retry_session()
        req = session.get(url, headers=headers, timeout=30) # Increased timeout and use session
        req.raise_for_status()
        soup = BeautifulSoup(req.text, "lxml")

        # 1. 提取标题 (title)
        title_tag = soup.find('h1')
        poem_data['title'] = title_tag.get_text(strip=True) if title_tag else "未知标题"

        # 2. 提取作者 (author) 和朝代 (dynasty)
        source_tag = soup.find('p', class_='source')
        author = "未知作者"
        dynasty = "未知朝代"
        if source_tag:
            author_links = source_tag.find_all('a')
            if len(author_links) > 0:
                author = author_links[0].get_text(strip=True)
            # Try to find dynasty more robustly
            span_tag = source_tag.find('span')
            if span_tag:
                dynasty_text_in_span = span_tag.get_text(strip=True)
                match_dynasty = re.search(r'〔(.*?)〕', dynasty_text_in_span)
                if match_dynasty:
                    dynasty = match_dynasty.group(1)
                elif len(author_links) > 1 and author_links[-1].get_text(strip=True) != author:
                    # Fallback if span method fails but there are multiple links
                    dynasty_candidate_text = author_links[-1].get_text(strip=True)
                    if len(dynasty_candidate_text) < 5 and ('代' in dynasty_candidate_text or len(dynasty_candidate_text) <=2 ) : # simple check for dynasty like string
                         dynasty = dynasty_candidate_text

        poem_data['author'] = author
        poem_data['dynasty'] = dynasty.replace('代', '') # "唐代" -> "唐"

        # 3. 提取内容 (content)
        content_div = soup.find('div', class_='contson')
        content_text = ""
        if content_div:
            for span_tooltip in content_div.find_all('span', style=lambda value: value and 'display:none' in value):
                span_tooltip.decompose()

            paragraphs = content_div.find_all('p')
            if paragraphs:
                lines_from_p = []
                for p_tag in paragraphs:
                    p_text = ' '.join(p_tag.get_text(separator='\n', strip=True).split())
                    lines_from_p.append(p_text)
                content_text = '\n'.join(lines_from_p)
            else:
                content_text = content_div.get_text(separator='\n', strip=True)
                content_text = '\n'.join([line.strip() for line in content_text.splitlines() if line.strip()])

            content_text = re.sub(r'\（.*?\）', '', content_text)
            content_text = re.sub(r'\(.*?\)', '', content_text)
            content_text = re.sub(r'\[.*?\]', '', content_text)
            content_text = content_text.replace('!', '！').replace('?', '？')

        poem_data['content'] = content_text if content_text else "无内容"

        # 4. 提取类型 (type) 和标签 (tags)
        tags_div = soup.find('div', class_='tag')
        tags_list = []
        poem_type = "诗"
        
        if tags_div:
            tag_links = tags_div.find_all('a')
            for tag_link in tag_links:
                tag_text = tag_link.get_text(strip=True)
                if tag_text.endswith('词') and len(tag_text) < 5:
                    poem_type = tag_text
                elif tag_text.endswith('曲') and len(tag_text) < 5:
                     poem_type = tag_text
                elif tag_text == "古诗" or tag_text == "诗歌":
                    poem_type = "诗"
                elif tag_text not in ["赏析", "译文", "翻译", "注释", "字词", "背景", "名句", "创作背景", "作者介绍"]:
                    if len(tag_text) < 10:
                        tags_list.append(tag_text)
        
        if poem_data.get('title'): # Use .get for safety
            title_val = poem_data['title']
            if "·" in title_val or "（" in title_val or title_val.endswith("令") or title_val.endswith("慢") or title_val.endswith("子"):
                 if poem_type == "诗": poem_type = "词"
            if title_val.endswith("赋"):
                 if poem_type == "诗": poem_type = "赋"

        poem_data['type'] = poem_type
        poem_data['tags'] = ','.join(list(set(tags_list))) if tags_list else None
        poem_data['difficulty'] = 1

        structured_poem_list.append(poem_data)
        time.sleep(0.25) # Add a small delay after each successful fetch

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"An error occurred processing {url}: {e}\nExtracted data so far: {poem_data}")


print(f"\nStarting to fetch details for {len(poem_links)} poems...")
executor = ThreadPoolExecutor(max_workers=2) # Further reduced max_workers
future_tasks = [executor.submit(get_poem_details, url) for url in poem_links]
wait(future_tasks, return_when=ALL_COMPLETED)

print(f"\nFetched details for {len(structured_poem_list)} poems.")

# Define output directory and filename within the project structure
# Assuming spider.py is in backend/, so backend/data/poems_structured.jsonl
output_dir = os.path.join(os.path.dirname(__file__), 'data') # Gets a 'data' subdir relative to this script
output_filename = os.path.join(output_dir, 'poems_structured.jsonl')

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    try:
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    except OSError as e:
        print(f"Error creating directory {output_dir}: {e}")
        # Fallback to current directory if unable to create data subdir
        output_filename = 'poems_structured.jsonl' 
        print(f"Will attempt to write to current directory: {os.getcwd()}")

print(f"Writing poems to {output_filename}...")
with open(output_filename, 'w', encoding='utf-8') as f:
    for poem_data_item in structured_poem_list:
        f.write(json.dumps(poem_data_item, ensure_ascii=False) + '\n')

print(f"Successfully wrote {len(structured_poem_list)} poems to {output_filename}")
