import re
import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 数据库相关导入
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DbSession # 使用别名以防冲突
# 假设 Poetry 模型和 Base 在 app.models 和 app.core.database
# 如果 spider.py 从项目根目录执行 (python backend/spider.py)
from app.models import Poetry 
from app.core.database import Base as AppBase # 如果需要创建表 (通常不需要，主应用会做)
from app.core.config import settings

# 新的目标网站
BASE_URL = 'https://gushici.china.com'
START_URL = f'{BASE_URL}/shici/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/5.37.36 '
                  '(KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Referer': BASE_URL
}

print("Initializing spider for gushici.china.com...")

def requests_retry_session(
    retries=5,
    backoff_factor=2,
    status_forcelist=(500, 502, 503, 504, 408),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(['GET', 'POST'])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# 用于临时存储从一页爬取到的诗歌字典列表
page_poems_data = []


def save_poem_to_db(db: DbSession, poem_data: dict):
    """将单首诗歌数据保存到数据库，并检查重复。"""
    try:
        existing_poem = db.query(Poetry).filter_by(title=poem_data['title'], author=poem_data['author']).first()
        if existing_poem:
            print(f"  Poem '{poem_data['title']}' by {poem_data['author']} already exists in DB. Skipping.")
            return False
        
        new_poem = Poetry(
            title=poem_data['title'],
            author=poem_data['author'],
            dynasty=poem_data['dynasty'],
            content=poem_data['content'],
            type=poem_data.get('type', '诗'),
            tags=poem_data.get('tags'), # 目前为 None
            difficulty=poem_data.get('difficulty', 1) # 默认
        )
        db.add(new_poem)
        # db.commit() # 单独提交可能效率低，改为批量提交
        print(f"  Added to DB session: {poem_data.get('title')}")
        return True
    except Exception as e:
        print(f"Error saving poem '{poem_data.get('title')}' to DB session: {e}")
        # db.rollback() # 如果是单独提交，则需要回滚
        return False

# 主爬取逻辑
def crawl_poems(page_url: str, db: DbSession): # 接收db会话
    global page_poems_data # 使用全局列表来收集当前页面的数据，稍后批量处理
    page_poems_data = [] # 清空上一页的数据

    print(f"Fetching poems from: {page_url}")
    try:
        session = requests_retry_session()
        req = session.get(page_url, headers=headers, timeout=30)
        req.raise_for_status()
        soup = BeautifulSoup(req.text, "lxml")
        
        poem_titles_h3 = soup.find_all('h3')
        if not poem_titles_h3:
            print("Could not find any poem title (h3 tags) on the page.")
            return 0

        print(f"Found {len(poem_titles_h3)} potential poem entries (h3 tags) on the page.")
        
        parsed_count = 0
        for h3_tag in poem_titles_h3:
            poem_item_data = {}
            
            # 1. 标题
            title_a_tag = h3_tag.find('a')
            title_text = title_a_tag.get_text(strip=True) if title_a_tag else h3_tag.get_text(strip=True)
            if not title_text:
                # print("  Skipping h3 tag with no title text.")
                continue
            poem_item_data['title'] = title_text

            # 2. 作者与朝代
            author_dynasty_text_node_content = ""
            current_node = h3_tag.next_sibling
            processed_author_node = None 
            print(f"\n--- Processing H3: {title_text[:30]}...") # DEBUG

            while current_node:
                if hasattr(current_node, 'name') and current_node.name: 
                    current_tag_name = current_node.name
                    current_tag_classes = current_node.get('class', []) if hasattr(current_node, 'attrs') else []
                    
                    if current_tag_name == 'h3' and current_node != h3_tag: 
                        break

                    # Check for author info within specific tags
                    if (current_tag_name == 'p' and 'item_txt' in current_tag_classes) or \
                       (current_tag_name == 'div' and any(cls in current_tag_classes for cls in ['item_info', 'side_focus_name'])):
                        candidate_text = current_node.get_text(strip=True)
                        print(f"    Text from '{current_tag_name}.{'.'.join(current_tag_classes) if current_tag_classes else ''}': '{candidate_text}'") # DEBUG
                        if '·' in candidate_text: 
                            author_dynasty_text_node_content = candidate_text
                            processed_author_node = current_node 
                            print(f"    Found Author/Dynasty Candidate in Tag '{current_tag_name}.{'.'.join(current_tag_classes)}': '{author_dynasty_text_node_content}'") # DEBUG
                            break
                    elif current_tag_name == 'span': # Handle <span>-作者·朝代</span>
                        candidate_text = current_node.get_text(strip=True)
                        print(f"    Text from 'span': '{candidate_text}'") # DEBUG
                        if candidate_text.startswith('-'):
                            candidate_text = candidate_text[1:].strip()
                        if '·' in candidate_text:
                            author_dynasty_text_node_content = candidate_text
                            processed_author_node = current_node
                            print(f"    Found Author/Dynasty Candidate in Tag 'span': '{author_dynasty_text_node_content}'") # DEBUG
                            break
                elif isinstance(current_node, str): 
                    stripped_text = current_node.strip()
                    if stripped_text:
                        if '·' in stripped_text and not author_dynasty_text_node_content: # Only use text node if no tagged version found yet
                            author_dynasty_text_node_content = stripped_text
                            processed_author_node = current_node # Though this is a text node, we mark its position
                            print(f"    Found Author/Dynasty Candidate in Text Node: '{author_dynasty_text_node_content}'") # DEBUG
                            break
                
                if hasattr(current_node, 'name') and current_node.name == 'div' and \
                    any(c in current_node.get('class', []) for c in ['content', 'contson', 'item_content', 'item_info', 'side_focus_txt']): # Added item_info, side_focus_txt
                    # If we hit a content div while still looking for author, it means author was likely missed or structured differently
                    # print("    Hit a potential content div while searching for author, stopping author search.") # DEBUG
                    break

                current_node = current_node.next_sibling
            
            author = "未知作者"
            dynasty = "未知朝代"
            if author_dynasty_text_node_content:
                if '·' in author_dynasty_text_node_content:
                    parts = author_dynasty_text_node_content.split('·', 1)
                    author = parts[0].strip()
                    dynasty = parts[1].strip().replace('[','').replace(']','') # Clean brackets from dynasty
                else: 
                    author = author_dynasty_text_node_content.strip().replace('[','').replace(']','') # Handle cases where only author or dynasty might be there and clean
            
            poem_item_data['author'] = author
            poem_item_data['dynasty'] = dynasty
            print(f"    Parsed Author: '{author}', Dynasty: '{dynasty}'") # DEBUG

            # 3. 内容
            content_text = ""
            content_div_found = None
            # Start searching for content AFTER the h3 tag OR after the processed_author_node if one was found
            start_search_for_content_node = processed_author_node if processed_author_node else h3_tag
            print(f"    Starting content search after node: {type(start_search_for_content_node)}, tag: {getattr(start_search_for_content_node, 'name', 'N/A')}, text hint: '{start_search_for_content_node.get_text(strip=True)[:30]}...'") # DEBUG
            
            current_sibling_for_content = start_search_for_content_node.next_sibling
            while current_sibling_for_content:
                print(f"    Content search - current sibling: type={type(current_sibling_for_content)}, name='{getattr(current_sibling_for_content, 'name', 'N/A')}', classes={getattr(current_sibling_for_content, 'attrs', {}).get('class', 'N/A')}, text(short)='{str(current_sibling_for_content)[:50].strip() if isinstance(current_sibling_for_content, str) else (getattr(current_sibling_for_content, 'get_text', lambda strip: '')(strip=True)[:30] + '...' if hasattr(current_sibling_for_content, 'name') else '') }'") # DEBUG
                if hasattr(current_sibling_for_content, 'name') and current_sibling_for_content.name == 'div':
                    # Check for 'item_info', 'side_focus_txt', or fallback 'content'/'contson'
                    current_classes = current_sibling_for_content.get('class', [])
                    if any(cls in current_classes for cls in ['item_info', 'side_focus_txt', 'content', 'contson']):
                        content_div_found = current_sibling_for_content
                        print(f"      Found POTENTIAL content div with classes: {current_classes}!") # DEBUG
                        break
                if hasattr(current_sibling_for_content, 'name') and current_sibling_for_content.name == 'h3': # Stop if we hit the next poem's title
                    print("      Hit next H3, stopping content search for current poem.") # DEBUG
                    break
                current_sibling_for_content = current_sibling_for_content.next_sibling

            if content_div_found:
                for br_tag in content_div_found.find_all("br"):
                    br_tag.replace_with("\\n")
                raw_content = content_div_found.get_text(separator=' ', strip=True)
                content_text = raw_content.replace("\\n", "\n").strip()
                content_text = re.sub(r'\\（.*?\\）', '', content_text)
                content_text = re.sub(r'\\(.*?\\)', '', content_text)
                content_text = re.sub(r'\\[.*?\\]', '', content_text)
                content_text = content_text.replace('!', '！').replace('?', '？')
            print(f"    Parsed Content (first 50 chars after cleaning): '{content_text[:50]}...'") # DEBUG
            
            poem_item_data['content'] = content_text if content_text else "无内容"
            
            poem_item_data['type'] = "诗"
            poem_item_data['tags'] = None
            poem_item_data['difficulty'] = 1

            # 更详细的判断和打印
            title_ok = poem_item_data.get('title') != "未知标题" and bool(poem_item_data.get('title'))
            # 作者信息可以为"未知作者"，但不能是空字符串，如果网站上就没有作者，那也接受
            author_ok = bool(poem_item_data.get('author')) # 允许"未知作者"但不能为空
            content_ok = poem_item_data.get('content') != "无内容" and bool(poem_item_data.get('content'))

            # print(f"    Checks: Title OK? {title_ok}, Author OK? {author_ok} ('{poem_item_data.get('author')}'), Content OK? {content_ok}") # DEBUG

            if title_ok and author_ok and content_ok:
                if save_poem_to_db(db, poem_item_data):
                    parsed_count += 1
                    print(f"  Successfully parsed & added to DB session: {poem_item_data.get('title')} by {poem_item_data.get('author')}") # 更明确的成功信息
            else:
                print(f"  Skipped entry: Title='{poem_item_data.get('title')}', Author='{poem_item_data.get('author')}', Content isempty= {not content_ok}")
                if not title_ok: print("    Reason: Title missing or invalid.")
                if not author_ok: print("    Reason: Author missing.") # "未知作者" 是可接受的，但完全没有提取到author (empty string)不行
                if not content_ok: print("    Reason: Content missing or invalid.")
            
        
        print(f"Finished parsing page. Successfully parsed and attempted to add {parsed_count} poems to DB session.")
        return parsed_count

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_url}: {e}")
        return 0
    except Exception as e:
        print(f"An unexpected error occurred with {page_url}: {e}")
        import traceback
        traceback.print_exc()
        return 0

# --- 主程序执行 ---
if __name__ == "__main__":
    # 设置数据库连接
    engine = create_engine(settings.get_database_url)
    # AppBase.metadata.create_all(bind=engine) # 确保表已创建, 通常在主应用启动时执行一次即可
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db: DbSession = SessionLocal()
    
    total_poems_added_to_session = 0
    max_pages_to_crawl = 200
    start_page = 1 # 可以从指定页码开始，默认为1
    consecutive_empty_pages_limit = 15 # 连续多少个空页面后停止
    empty_page_streak = 0 # 当前连续空页面的计数
    
    try:
        for page_num in range(start_page, start_page + max_pages_to_crawl):
            # 使用新的URL分页格式: https://gushici.china.com/shici/0_0_0_PAGE.html
            current_url = f"{BASE_URL}/shici/0_0_0_{page_num}.html"
            
            print(f"\n--- Processing Page {page_num} ({current_url}) ---")
            
            parsed_on_page = crawl_poems(current_url, db) # Pass db session
            total_poems_added_to_session += parsed_on_page
            
            if parsed_on_page == 0:
                empty_page_streak += 1
                print(f"No new poems found or added from page {page_num}. Consecutive empty pages: {empty_page_streak}")
                if empty_page_streak >= consecutive_empty_pages_limit:
                    print(f"Reached {consecutive_empty_pages_limit} consecutive empty pages. Stopping pagination.")
                    break # 达到连续空页面上限，停止
            else:
                empty_page_streak = 0 # 重置连续空页面计数
            
            # Delay only if we are continuing to the next page and it's not the last one in the current batch
            if page_num < (start_page + max_pages_to_crawl - 1) and empty_page_streak < consecutive_empty_pages_limit:
                print(f"Waiting for 2 seconds before fetching next page...")
                time.sleep(2) # 尊重服务器, 避免请求过于频繁

        if total_poems_added_to_session > 0:
            db.commit() # 提交所有事务
            print(f"\nSuccessfully committed {total_poems_added_to_session} new poems to the database from {max_pages_to_crawl} pages (or fewer if pagination ended early).")
        else:
            print(f"\nNo new poems were added to the database session to commit after attempting to crawl {max_pages_to_crawl} pages.")

    except Exception as e:
        print(f"An error occurred during the crawl or DB commit process: {e}")
        db.rollback() # 回滚所有未提交的更改
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("Database session closed.")

    # 移除旧的 JSON Lines 文件写入逻辑
    # print(f"\nFetched details for {len(all_poems_data)} poems from the first page.")
    # output_dir = os.path.join(os.path.dirname(__file__), 'data')
    # output_filename = os.path.join(output_dir, 'poems_china_com.jsonl')
    # ... (文件写入代码)
