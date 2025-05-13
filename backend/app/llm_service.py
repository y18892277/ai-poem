import os
import requests # 保留导入
# from openai import OpenAI # 移除导入
from .core.config import settings
import logging
import re
from sqlalchemy.orm import Session # 导入 Session
from .models import Poetry # 导入 Poetry 模型
# from .core.database import get_db # 暂时不需要在这里获取db，由调用方传入
from typing import Optional, List, Set
from pypinyin import lazy_pinyin, Style # <--- 新增导入

print("########## llm_service.py TOP LEVEL CHECKPOINT 1 ##########") # 新增顶层打印

# 确保logging配置在模块级别尽早生效，以捕获可能的早期问题
logging.basicConfig(level=logging.INFO) # 可以考虑在这里也配置一下，尽管main.py也有
logger = logging.getLogger(__name__) # logger获取应该在basicConfig之后

print("########## llm_service.py TOP LEVEL CHECKPOINT 2 - Logger configured ##########") # 新增顶层打印

MAX_RETRIES = 3
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions" # 和test.py一致

def get_deepseek_api_key() -> Optional[str]: # 函数名和职责变更
    """获取DeepSeek API Key"""
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        logger.warning("DEEPSEEK_API_KEY not found in settings. LLM features will be disabled.")
        return None
    logger.info("DEEPSEEK_API_KEY found in settings.")
    return api_key

def _clean_line(line: str) -> str:
    """
    清理诗句，尝试移除常见干扰信息（如括号内容、常见前缀），然后提取汉字。
    过短的清理后结果视为空。
    """
    if not line:
        return ""

    # 1. 尝试移除括号及其内容（包括中文和英文圆括号、方括号、花括号）
    line = re.sub(r"[（\(\[].*?[）\)\]]", "", line) 
    line = re.sub(r"\{.*?\}", "", line)

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
    line = line.replace('"', '').replace('"', '').replace('"', '').replace('"', '') # 添加中文引号移除

    # 4. 提取所有汉字
    cleaned = "".join(re.findall(r'[一-鿿]+', line))
    
    # 5. 长度校验
    if len(cleaned) <= 1 and cleaned not in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']:
        return ""
    return cleaned.strip()

def is_line_in_db(line: str, db: Session) -> bool:
    logger.debug(f"[is_line_in_db] Received line for DB check: '{line}'")
    if not line or not db:
        logger.debug("[is_line_in_db] Empty line or no db session, returning False.")
        return False
    cleaned_line_for_query = line
    if not cleaned_line_for_query:
        logger.debug(f"[is_line_in_db] Cleaned line for query is empty. Original line: '{line}'. Returning False.")
        return False
    like_pattern = "%" + "%".join(list(cleaned_line_for_query)) + "%"
    logger.debug(f"[is_line_in_db] Constructed LIKE pattern: '{like_pattern}'")
    try:
        exists = db.query(Poetry.id).filter(Poetry.content.like(like_pattern)).limit(1).scalar() is not None
        logger.debug(f"[is_line_in_db] Query result for pattern '{like_pattern}' (original line: '{line}') in DB: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Database check failed for line '{line}' with pattern '{like_pattern}': {e}", exc_info=True)
        return False

def get_lazy_pinyin_set(char: str) -> Set[str]:
    """获取单个汉字所有读音的不带声调拼音集合。"""
    if not char or not '\u4e00' <= char <= '\u9fff': #确保是单个汉字
        return set()
    # 使用NORMAL风格获取所有读音的拼音列表，然后转换为集合
    pinyin_list = lazy_pinyin(char, style=Style.NORMAL)
    return set(p for sublist in pinyin_list for p in sublist) # lazy_pinyin返回[[p1],[p2]]或[[p]]

def are_chars_homophones_or_same(char1: str, char2: str) -> bool:
    """
    判断两个汉字是否相同，或者它们是否为游戏规则下的同音字（忽略声调）。
    """
    if not char1 or not char2 or not '\u4e00' <= char1 <= '\u9fff' or not '\u4e00' <= char2 <= '\u9fff':
        return False # 不是有效汉字输入
    if char1 == char2:
        return True
    
    pinyin_set1 = get_lazy_pinyin_set(char1)
    pinyin_set2 = get_lazy_pinyin_set(char2)
    
    # 检查两个拼音集合是否有交集
    return not pinyin_set1.isdisjoint(pinyin_set2)

def get_ai_starting_line(db: Session) -> Optional[str]:
    logger.info("!!!!!!!!!!!! get_ai_starting_line (USING REQUESTS) CALLED !!!!!!!!!!!!")
    api_key = get_deepseek_api_key()
    if not api_key:
        return "抱歉，AI服务API Key未配置。"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    # 基于之前的优化建议修改提示词
    system_content = (
        "你是一位顶级中国古诗词专家，你的任务是为诗词接龙游戏提供开场诗句。"
        "你提供的诗句必须是【真实存在于中国古古诗词中的原句片段】。"
        "诗句必须是【5到7个汉字】。"
        "诗句必须是【广为流传、有据可查的经典名句】，这样更容易被大众所知晓。"
        "你的回答必须【绝对纯净】，【只包含诗句本身的文字内容】，不包含任何诗名、作者、标点、序号、解释或任何其他字符。"
        "严格遵守上述所有规则。"
    )
    prompt_text = "请提供一句适合作为诗词接龙开头的、符合上述所有要求的诗句。"
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 100,
        "temperature": 0.6, # 之前讨论过降低此值
        "stream": False
    }

    for attempt in range(MAX_RETRIES + 1): # MAX_RETRIES 可以设为 1 或 2
        logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES + 1} to get starting line from DeepSeek (requests).")
        try:
            logger.info(f"Calling DeepSeek API (requests). URL: {DEEPSEEK_API_URL}, Payload: {str(payload)[:200]}...")
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=15) # 稍微增加单次timeout
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"DeepSeek API response (requests): {str(result)[:200]}...")

            if result.get('choices') and result['choices'][0].get('message') and result['choices'][0]['message'].get('content'):
                ai_line_raw = result['choices'][0]['message']['content'].strip()
                ai_line_cleaned = _clean_line(ai_line_raw)
                logger.info(f"LLM raw response: '{ai_line_raw}', Cleaned: '{ai_line_cleaned}'")

                if not ai_line_cleaned:
                    logger.warning("LLM returned empty or too short line after cleaning.")
                    if attempt < MAX_RETRIES: continue
                    else: return "抱歉，AI大模型未能生成有效的诗句内容。"

                if is_line_in_db(ai_line_cleaned, db):
                    logger.info(f"Line '{ai_line_cleaned}' FOUND in DB. Returning this line.")
                    return ai_line_cleaned
                else:
                    logger.warning(f"Line '{ai_line_cleaned}' NOT found in DB.")
                    if attempt < MAX_RETRIES:
                        # 反馈给AI，让它尝试生成更常见的诗句
                        payload["messages"].append({"role": "assistant", "content": ai_line_raw}) # 添加AI上一次的回答
                        payload["messages"].append({"role": "user", "content": "这句诗句很好，但不够广为人知或不在常用诗词库中。请再提供一句【更经典、更常见】的、符合所有原始要求的5-7字开场诗句。"})
                        continue
                    else: 
                        logger.error(f"Line '{ai_line_cleaned}' not in DB after all retries. LLM might be returning it, or a very similar one despite feedback.")
                        # 如果多次重试AI都给不在库中的，可以考虑返回一个预设的或者记录这个情况
                        # 为了游戏能开始，这里可以考虑返回ai_line_cleaned，即使它不在库中，并标记
                        # 但当前严格要求在库中，所以返回None或错误
                        return "抱歉，AI尽力了，但生成的诗句未能在我们的诗词库中得到广泛确认。请稍后再试。"
            else:
                logger.warning(f"LLM did not return valid content structure. Response: {str(result)[:200]}")
                if attempt < MAX_RETRIES: continue
                else: return "抱歉，AI大模型未能生成诗句。"

        except requests.exceptions.Timeout:
            logger.error(f"Timeout during DeepSeek call (Attempt {attempt + 1}) after 15s.", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，连接AI服务超时，请稍后再试。"
        except requests.exceptions.RequestException as e:
            logger.error(f"RequestException during DeepSeek call (Attempt {attempt + 1}): {type(e).__name__} - {str(e)}", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，连接AI服务时发生网络错误。"
        except Exception as e:
            logger.error(f"Generic exception during DeepSeek call processing (Attempt {attempt + 1}): {type(e).__name__} - {str(e)}", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，AI大模型服务暂时出现问题。"
    
    logger.error("Exhausted all attempts to get a valid starting line (requests). Returning None.")
    return "抱歉，AI多次尝试后仍未能提供合适的开场诗句。"

def get_ai_response_to_line(user_line: str, db: Session) -> Optional[str]:
    logger.info(f"!!!!!!!!!!!! get_ai_response_to_line (USING REQUESTS) CALLED with user_line: '{user_line}' !!!!!!!!!!!!")
    api_key = get_deepseek_api_key()
    if not api_key:
        return "抱歉，AI服务API Key未配置。"

    cleaned_user_line = _clean_line(user_line)
    if not cleaned_user_line:
        logger.warning(f"User line '{user_line}' is empty after cleaning. Cannot get AI response.")
        return "您的输入无效，AI无法接龙。"
    
    last_char = cleaned_user_line[-1]
    # 获取尾字的无声调拼音，用于更明确地指导AI
    last_char_pinyins = get_lazy_pinyin_set(last_char)
    pinyin_hint = f"（提示：它的拼音是 '{next(iter(last_char_pinyins))}'，注意寻找同音字哦！）" if last_char_pinyins else ""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 修改提示词以支持同音字
    system_content = """你是一位才华横溢、富有创造力的中国古诗词接龙大师。你的核心目标是运用你的智慧，让诗词接龙游戏尽可能地持续下去，同时严格遵守接龙规则。

【重要接龙规则】:

1. 你需要接一个大约【5到7个汉字】的纯粹的诗句。

2. 这个诗句必须是某一句较为常见或有据可查的【真实古诗词的片段】。

3. 你的诗句的【首字】必须与上一句诗词的【尾字】相同，或者是其【同音字】（声调不同也没关系，只要读音相似即可）。

4. 你的回答必须【仅仅包含诗句本身】，【绝对不能】包含任何其他文字，比如诗名、作者、标点符号、括号、解释、序号或者任何形式的聊天内容！

请沉思片刻，发挥你的文学积累，相信你能找到合适的诗句！"""
    
    base_prompt_text_template = """上一句的诗句是 '{user_line_placeholder}'，它的最后一个字是 '{last_char_placeholder}'{pinyin_hint_placeholder}。

现在，请你接一句以 '{last_char_placeholder}' 或其【同音字】开头的、符合所有系统指令中重要接龙规则的诗句："""
    
    current_prompt_text = base_prompt_text_template.format(
        user_line_placeholder=cleaned_user_line,
        last_char_placeholder=last_char,
        pinyin_hint_placeholder=pinyin_hint
    )

    for attempt in range(MAX_RETRIES + 1): # MAX_RETRIES 可以设为 1 或 2
        logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES + 1} for AI response to '{cleaned_user_line}' (requests). Current prompt: {current_prompt_text[:150]}...")
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": current_prompt_text}
            ],
            "max_tokens": 50,
            "temperature": 0.7, # 可以尝试调整
            "stop": ["\n", "（", "(", "【", "答：", "解：", "。", "！", "？"], # 增加常见标点作为停止符
            "stream": False
        }
        
        try:
            logger.info(f"Calling DeepSeek API for response (requests). URL: {DEEPSEEK_API_URL}, Payload: {str(payload)[:200]}...")
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=15) # 增加timeout
            response.raise_for_status()

            result = response.json()
            logger.info(f"DeepSeek API response for AI line (requests): {str(result)[:200]}...")

            if result.get('choices') and result['choices'][0].get('message') and result['choices'][0]['message'].get('content'):
                ai_line_raw = result['choices'][0]['message']['content'].strip()
                
                if any(phrase in ai_line_raw for phrase in ["我接不上", "接不上", "无法接龙", "抱歉"]):
                    logger.info(f"LLM explicitly stated it cannot chain. Response: '{ai_line_raw}'")
                    if attempt < MAX_RETRIES:
                        # 尝试给更具体的反馈
                        payload["messages"].append({"role": "assistant", "content": ai_line_raw})
                        payload["messages"].append({"role": "user", "content": f"再努力一下，大师！这对你来说肯定不难。请严格按照规则，接一个以'{last_char}'或其同音字开头的5-7字纯诗句。"})
                        current_prompt_text = payload["messages"][-1]["content"] # 更新prompt给下一次尝试
                        continue 
                    return "抱歉，AI多次尝试后仍表示无法接龙。"

                ai_line_cleaned = _clean_line(ai_line_raw) 
                logger.info(f"LLM raw response: '{ai_line_raw}', Cleaned: '{ai_line_cleaned}'")

                if not ai_line_cleaned:
                    logger.warning("LLM returned empty or too short line for AI response.")
                    if attempt < MAX_RETRIES:
                        payload["messages"].append({"role": "assistant", "content": ai_line_raw})
                        payload["messages"].append({"role": "user", "content": f"返回的诗句清理后内容太少。请确保返回的是约5-7个汉字的纯诗句部分，且以'{last_char}'或其同音字开头。"})
                        current_prompt_text = payload["messages"][-1]["content"]
                        continue
                    else: return "抱歉，AI大模型未能生成有效的诗句来接龙。"
                
                if not (4 <= len(ai_line_cleaned) <= 8):
                    logger.warning(f"AI response '{ai_line_cleaned}' length {len(ai_line_cleaned)} not ideal.")
                    if attempt < MAX_RETRIES:
                        payload["messages"].append({"role": "assistant", "content": ai_line_raw})
                        payload["messages"].append({"role": "user", "content": f"诗句长度 '{len(ai_line_cleaned)}' 不太符合期望的5-7字。请重新生成一个以'{last_char}'或其同音字开头的【纯粹的】5到7个汉字的诗句片段。"})
                        current_prompt_text = payload["messages"][-1]["content"]
                        continue

                # 使用新的同音字判断逻辑
                if not are_chars_homophones_or_same(ai_line_cleaned[0], last_char):
                    logger.warning(f"AI response '{ai_line_cleaned}' (first char: {ai_line_cleaned[0]}) does not start with expected char '{last_char}' or its homophone.")
                    if attempt < MAX_RETRIES:
                        payload["messages"].append({"role": "assistant", "content": ai_line_raw})
                        payload["messages"].append({"role": "user", "content": f"首字 '{ai_line_cleaned[0]}' 不对哦！必须是以 '{last_char}' 或其同音字开头的纯诗句。再想想看。"})
                        current_prompt_text = payload["messages"][-1]["content"]
                        continue
                    else: return f"抱歉，AI暂时未能找到以 '{last_char}' 或其同音字开头的诗句。"

                if is_line_in_db(ai_line_cleaned, db):
                    logger.info(f"AI response line '{ai_line_cleaned}' FOUND in DB. Returning.")
                    return ai_line_cleaned
                else:
                    logger.warning(f"AI response line '{ai_line_cleaned}' NOT found in DB.")
                    if attempt < MAX_RETRIES:
                        payload["messages"].append({"role": "assistant", "content": ai_line_raw})
                        payload["messages"].append({"role": "user", "content": f"这句 '{ai_line_cleaned}' 很有趣，但在我的常见诗词库中未能确认。能否换一个以 '{last_char}' 或其同音字开头的、更广为人知或明确有出处的5-7字纯诗句呢？"})
                        current_prompt_text = payload["messages"][-1]["content"]
                        continue
                    else: 
                        logger.error(f"AI response line '{ai_line_cleaned}' not in DB after all retries.")
                        # 如果多次尝试AI都给不在库中的，可以考虑返回ai_line_cleaned，即使它不在库中，并标记
                        return f"AI给出了诗句'{ai_line_cleaned}'，但它不在我们的常用诗词库中。您觉得算接上了吗？（可选择返回此句或判AI失败）" # 这是一个需要产品层面决定的点
            else:
                logger.warning(f"LLM did not return valid content structure for AI response. Response: {str(result)[:200]}")
                if attempt < MAX_RETRIES:
                    payload["messages"].append({"role": "assistant", "content": result.get('choices')[0].get('message').get('content') if result.get('choices') and result['choices'][0].get('message') else "Empty response"})
                    payload["messages"].append({"role": "user", "content": f"返回内容似乎是空的或格式不对。请给出一个以'{last_char}'或其同音字开头的5-7字纯诗句。"})
                    current_prompt_text = payload["messages"][-1]["content"]
                    continue
                else: return "抱歉，AI大模型未能生成诗句来接龙。"

        except requests.exceptions.Timeout:
            logger.error(f"Timeout during DeepSeek call for AI response (Attempt {attempt + 1}) after 15s.", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，连接AI服务超时，请稍后再试。"
        except requests.exceptions.RequestException as e:
            logger.error(f"RequestException during DeepSeek call for AI response (Attempt {attempt + 1}): {type(e).__name__} - {str(e)}", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，连接AI服务时发生网络错误。"
        except Exception as e:
            logger.error(f"Generic exception during DeepSeek call for AI response (Attempt {attempt + 1}): {type(e).__name__} - {str(e)}", exc_info=True)
            if attempt == MAX_RETRIES:
                return "抱歉，AI大模型服务在接龙时出现问题。"

    logger.error(f"Exhausted all attempts to get a valid AI response for '{cleaned_user_line}' (requests). Returning None.")
    return f"抱歉，AI多次尝试后仍未能为'{cleaned_user_line}'接上合适的诗句。"

async def judge_user_line_by_ai(ai_previous_line: str, user_current_line_raw: str, db: Session) -> tuple[bool, str]:
    """
    AI 判断用户当前的接龙诗句是否有效。
    主要基于首字规则（同音或同字）和数据库校验。
    返回一个元组 (is_correct: bool, message: str)
    """
    logger.info(f"!!!!!!!!!!!! judge_user_line_by_ai CALLED (Homophone Rule) !!!!!!!!!!!! AI_Prev: '{ai_previous_line}', User_Raw: '{user_current_line_raw}'")
    
    cleaned_user_line = _clean_line(user_current_line_raw)
    cleaned_ai_previous_line = _clean_line(ai_previous_line)

    if not cleaned_user_line:
        logger.warning(f"User line '{user_current_line_raw}' cleaned to empty.")
        return False, "您的回答似乎是空的或无效的，请输入一句诗词。"

    if not cleaned_ai_previous_line:
        logger.error(f"Critical: AI's previous line '{ai_previous_line}' cleaned to empty. This should not happen.")
        return False, "系统内部错误：AI的上一句诗词记录无效，无法判断您的回答。"

    # 1. 基本规则校验：首字是否接上（同字或同音字）
    expected_char_for_next_line = cleaned_ai_previous_line[-1]
    actual_first_char_of_user_line = cleaned_user_line[0]
    
    # 使用新的同音字判断逻辑
    if not are_chars_homophones_or_same(actual_first_char_of_user_line, expected_char_for_next_line):
        pinyins_expected = get_lazy_pinyin_set(expected_char_for_next_line)
        pinyin_hint_expected = f"(读音参考: {next(iter(pinyins_expected)) if pinyins_expected else '未知'})"
        logger.info(f"User line first char '{actual_first_char_of_user_line}' does not match AI prev last char '{expected_char_for_next_line}' or its homophones.")
        return False, f"首字不对哦！应该是以'{expected_char_for_next_line}'{pinyin_hint_expected}或其同音字开头的诗句，但您的是以'{actual_first_char_of_user_line}'开头。"

    # 2. 数据库校验：用户回答的诗句是否在库中
    if not is_line_in_db(cleaned_user_line, db):
        logger.info(f"User line '{cleaned_user_line}' NOT found in DB.")
        return False, f"您回答的诗句'{cleaned_user_line}'很有意境，但在我的诗词库中未能查证到呢。"
        
    logger.info(f"User line '{cleaned_user_line}' passed all checks (first char homophone/same & DB).")
    return True, "接得漂亮！"

