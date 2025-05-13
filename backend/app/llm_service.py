import os
from zhipuai import ZhipuAI
from .core.config import settings
import logging
import re
from sqlalchemy.orm import Session # 导入 Session
from .models import Poetry # 导入 Poetry 模型
# from .core.database import get_db # 暂时不需要在这里获取db，由调用方传入
from typing import Optional

print("!!!!!!!!!!!! LLM_SERVICE.PY WAS LOADED BY PYTHON !!!!!!!!!!!!")

logger = logging.getLogger(__name__)

# 全局客户端实例
llm_client: Optional[ZhipuAI] = None # 明确类型
MAX_RETRIES = 3 # 定义最大重试次数

def get_llm_client() -> Optional[ZhipuAI]: # 返回 Optional[ZhipuAI]
    """获取或初始化智谱AI客户端 (同步)"""
    # print("!!!!!!!!!!!! GET_LLM_CLIENT FUNCTION ENTERED !!!!!!!!!!!!") # 可以移除这个详细打印
    global llm_client
    if llm_client is None:
        api_key = settings.LLM_API_KEY
        if not api_key:
            logger.warning("LLM_API_KEY not found. LLM features will be disabled.")
            return None
        try:
            llm_client = ZhipuAI(api_key=api_key)
            logger.info("ZhipuAI client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ZhipuAI client: {e}", exc_info=True)
            llm_client = None # 确保失败时client为None
            return None
    return llm_client

def _clean_line(line: str) -> str:
    """
    清理诗句，尝试移除常见干扰信息（如括号内容、常见前缀），然后提取汉字。
    过短的清理后结果视为空。
    """
    if not line:
        return ""

    # 1. 尝试移除括号及其内容（包括中文和英文圆括号、方括号、花括号）
    line = re.sub(r"[（\\(\\[].*?[）\\)\\]]", "", line) 
    line = re.sub(r"\\{.*?\\}", "", line)

    # 2. 移除一些常见的前缀和后缀短语
    common_prefixes = [
        "好的，请看：", "好的，这句是：", "请看：", "这句是：", 
        "我接的是：", "我的是：", "答案是：", "当然，这是下一句：",
        "没问题，请看下句：", "我来了：", "这是我的回答：", "诗句是："
    ]
    common_suffixes = [
        "你看如何？", "怎么样？", "希望你喜欢。", "请指正。"
    ]
    for prefix in common_prefixes:
        if re.match(f"^{re.escape(prefix)}", line, re.IGNORECASE):
            line = line[len(prefix):].lstrip()
    for suffix in common_suffixes:
        if line.lower().endswith(suffix.lower()):
            line = line[:-len(suffix)].rstrip()
    
    # 3. 移除中英文引号
    line = line.replace('"', '').replace("'", "").replace("`", "")
    line = line.replace('"', '').replace('"', '').replace('"', '').replace('"', '')

    # 4. 提取所有汉字
    cleaned = "".join(re.findall(r'[一-鿿]+', line))
    
    # 5. 长度校验
    if len(cleaned) <= 1 and cleaned not in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']:
        return ""
    return cleaned.strip()

def is_line_in_db(line: str, db: Session) -> bool:
    """检查清理后的诗句是否存在于数据库中。会尝试更宽松的匹配以适应数据库中可能存在的标点。"""
    logger.debug(f"[is_line_in_db] Received line for DB check: '{line}'")
    if not line or not db:
        logger.debug("[is_line_in_db] Empty line or no db session, returning False.")
        return False

    # 传入的 line 应该是已经被 _clean_line 清理过的，不含标点和多余空格
    # 例如: "海内存知己天涯若比邻"
    cleaned_line_for_query = line

    if not cleaned_line_for_query:
        logger.debug(f"[is_line_in_db] Cleaned line for query is empty. Original line: '{line}'. Returning False.")
        return False

    # 构建宽松的 LIKE 查询模式，例如: '%海%内%存%知%己%天%涯%若%比%邻%'
    # 这种模式可以匹配数据库中如 "海内存知己，天涯若比邻。" 这样的内容
    like_pattern = "%" + "%".join(list(cleaned_line_for_query)) + "%"
    logger.debug(f"[is_line_in_db] Constructed LIKE pattern: '{like_pattern}'")

    try:
        # 使用构造的模式进行查询
        exists = db.query(Poetry.id).filter(Poetry.content.like(like_pattern)).limit(1).scalar() is not None
        logger.debug(f"[is_line_in_db] Query result for pattern '{like_pattern}' (original line: '{line}') in DB: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Database check failed for line '{line}' with pattern '{like_pattern}': {e}", exc_info=True)
        return False

# 同步版本的 get_ai_starting_line
def get_ai_starting_line(db: Session) -> Optional[str]:
    print("!!!!!!!!!!!! get_ai_starting_line (SYNC FULL LOGIC) CALLED !!!!!!!!!!!!")
    client = get_llm_client()
    if not client:
        logger.error("LLM client not available for starting line.")
        return "抱歉，AI服务暂时不可用。"

    prompt = "请你作为一位精通中国古诗词的诗词大师，提供一个5到7个字的诗词短句作为诗词接龙的开头。这个短语本身必须是某首真实存在的古诗词的一部分，且较为常见、脍炙人口。请直接返回这个诗句本身，不要包含任何其他解释、标题或作者信息。"
    system_content = "你是一个精通中国古诗词的大师，你需要严格按照要求提供真实的诗词短句。"

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES + 1} to get and validate starting line (sync).")
        try:
            response = client.chat.completions.create(
                model="glm-4", 
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            if response.choices and response.choices[0].message.content:
                ai_line_raw = response.choices[0].message.content.strip()
                ai_line_cleaned = _clean_line(ai_line_raw)
                logger.info(f"LLM raw response: '{ai_line_raw}', Cleaned: '{ai_line_cleaned}'")

                if not ai_line_cleaned:
                    logger.warning("LLM returned empty or too short line after cleaning.")
                    if attempt < MAX_RETRIES: continue
                    else: return "抱歉，AI大模型未能生成有效的诗句内容。"

                if is_line_in_db(ai_line_cleaned, db):
                    logger.info(f"Line '{ai_line_cleaned}' FOUND in DB. Returning this line.")
                    return ai_line_cleaned # 返回清理后的诗句
                else:
                    logger.warning(f"Line '{ai_line_cleaned}' NOT found in DB.")
                    if attempt < MAX_RETRIES: 
                        # prompt += f"\n(提示：你上次返回的 '{ai_line_raw}' 清理后为 '{ai_line_cleaned}'，它不在我们的诗词库中，请换一句。)" # 可选：给AI反馈
                        continue
                    else: 
                        logger.error(f"Line '{ai_line_cleaned}' not in DB after all retries.")
                        # 对于初始诗句，如果最终找不到，返回None或错误提示，让main.py处理
                        return None # 让 main.py 决定如何处理（例如返回503）
            else:
                logger.warning("LLM did not return valid content (choices empty or message content missing).")
                if attempt < MAX_RETRIES: continue
                else: return "抱歉，AI大模型未能生成诗句。"

        except Exception as e:
            logger.error(f"Exception during LLM call or processing (Attempt {attempt + 1}): {e}", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，AI大模型服务暂时出现问题。"
    
    logger.error("Exhausted all attempts to get a valid starting line (sync). Returning None.")
    return None # 明确返回None，如果所有尝试都失败了

# 同步版本的 get_ai_response_to_line
def get_ai_response_to_line(user_line: str, db: Session) -> Optional[str]:
    print(f"!!!!!!!!!!!! get_ai_response_to_line (SYNC FULL LOGIC) CALLED with user_line: '{user_line}' !!!!!!!!!!!!")
    client = get_llm_client()
    if not client:
        logger.error("LLM client not available for response line.")
        return None

    cleaned_user_line = _clean_line(user_line)
    if not cleaned_user_line:
        logger.warning(f"User line '{user_line}' is empty after cleaning. Cannot get AI response.")
        return "您的输入无效，AI无法接龙。"
    
    last_char = cleaned_user_line[-1]
    
    # 使用行继续符 \ 来明确地将多行字符串拼接为一个整体赋值给 base_prompt
    base_prompt = \
        f"你的任务是进行诗词接龙。上一句的诗句是 '{cleaned_user_line}'，它的最后一个字是 '{last_char}'。\\n" \
        f"请你接一个以 '{last_char}' 开头的、大约5到7个字的纯粹的诗句。\\n" \
        "这个诗句必须是某一句较为常见或有据可查的真实古诗词的片段。\\n" \
        "请沉思片刻，发挥你的文学积累，相信你能找到合适的诗句！\\n\\n" \
        "重要规则：你的回答必须【仅仅包含诗句本身】，【绝对不能】包含任何其他文字，比如诗名、作者、标点符号、括号、解释、序号或者任何形式的聊天内容！\\n\\n" \
        "以下是【正确格式】的例子：\\n" \
        "例1：如果上一句尾字是\"天\"你就直接回答：\"天涯共此时\"\\n" \
        "例2：如果上一句尾字是\"山\"你就直接回答：\"山色空蒙雨亦奇\"\\n\\n" \
        f"现在，请接上一句尾字为'{last_char}'的诗句："
    
    current_prompt = base_prompt 
    
    system_content = "你是一位才华横溢、富有毅力和创造力的中国古诗词接龙大师。你的核心目标是运用你的智慧，让诗词接龙游戏尽可能地持续下去，同时严格遵守接龙规则（约5-7字，真实诗词片段，首字正确，输出内容【绝对纯净，只有诗句文字】）。"

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES + 1} for AI response to '{cleaned_user_line}' (sync). Current prompt: {current_prompt}")
        try:
            response = client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": current_prompt}
                ],
                max_tokens=50, # 减少 max_tokens，因为我们期望的是短诗句，且防止它说废话
                temperature=0.75, # 略微降低温度，使其更稳定地遵循格式
                stop=["\n", "（", "(", "【", "答：", "解："] # 增加 stop 序列，尝试提前终止不必要的后缀
            )
            if response.choices and response.choices[0].message.content:
                ai_line_raw = response.choices[0].message.content.strip()
                
                if "我接不上" in ai_line_raw or "接不上" in ai_line_raw or "无法接龙" in ai_line_raw:
                    logger.info(f"LLM explicitly stated it cannot chain from '{cleaned_user_line}'. Response: '{ai_line_raw}'")
                    if attempt == 0 and attempt < MAX_RETRIES:
                        logger.info("LLM said '我接不上' on first attempt, encouraging a retry.")
                        current_prompt = base_prompt + "\\n（再努力一下，大师！这对你来说肯定不难。请再试一次，只返回纯诗句。）"
                        continue 
                    return None

                ai_line_cleaned = _clean_line(ai_line_raw) 
                logger.info(f"LLM raw response: '{ai_line_raw}', Cleaned by NEW _clean_line: '{ai_line_cleaned}'")

                if not ai_line_cleaned:
                    logger.warning("LLM returned empty or too short line after cleaning for AI response.")
                    if attempt < MAX_RETRIES:
                        current_prompt = base_prompt + "\\n（返回的诗句清理后内容太少。请确保返回的是约5-7个汉字的纯诗句部分。）"
                        continue
                    else: 
                        return "抱歉，AI大模型未能生成有效的诗句来接龙。"
                
                if not (4 <= len(ai_line_cleaned) <= 8):
                    logger.warning(f"AI response '{ai_line_cleaned}' length {len(ai_line_cleaned)} is not between 4 and 8 chars.")
                    if attempt < MAX_RETRIES:
                        current_prompt = base_prompt + f"\\n（诗句长度 '{len(ai_line_cleaned)}' 不太符合期望的5-7字。请重新生成一个【纯粹的】5到7个汉字的诗句片段。）"
                        continue

                if ai_line_cleaned[0].lower() != last_char.lower():
                    logger.warning(f"AI response '{ai_line_cleaned}' (first char: {ai_line_cleaned[0]}) does not start with expected char '{last_char}'.")
                    if attempt < MAX_RETRIES:
                        current_prompt = base_prompt + f"\\n（首字 '{ai_line_cleaned[0]}' 不对哦！必须是以 '{last_char}' 开头的纯诗句。再想想看。）"
                        continue
                    else: 
                        return f"抱歉，AI暂时未能找到以 '{last_char}' 开头的诗句。"

                if is_line_in_db(ai_line_cleaned, db):
                    logger.info(f"AI response line '{ai_line_cleaned}' FOUND in DB. Returning.")
                    return ai_line_cleaned
                else:
                    logger.warning(f"AI response line '{ai_line_cleaned}' NOT found in DB.")
                    if attempt < MAX_RETRIES:
                        current_prompt = base_prompt + f"\\n（这句 '{ai_line_cleaned}' 很有趣，但在我的常见诗词库中未能确认。能否换一个以 '{last_char}' 开头的、更广为人知或明确有出处的5-7字纯诗句呢？）"
                        continue
                    else: 
                        logger.error(f"AI response line '{ai_line_cleaned}' not in DB after all retries.")
                        return None
            else:
                logger.warning("LLM did not return valid content for AI response (choices empty or message content missing).")
                if attempt < MAX_RETRIES:
                    current_prompt = base_prompt + f"\\n（返回内容似乎是空的。请给出一个以'{last_char}'开头的5-7字纯诗句。）" # 使用f-string并用单引号包裹变量
                    continue
                else: 
                    return "抱歉，AI大模型未能生成诗句来接龙。"

        except Exception as e:
            logger.error(f"Exception during LLM call or processing for AI response (Attempt {attempt + 1}): {e}", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，AI大模型服务在接龙时出现问题。"

    logger.error(f"Exhausted all attempts to get a valid AI response for '{cleaned_user_line}' (sync). Returning None.")
    return None

