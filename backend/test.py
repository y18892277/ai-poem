# deepseek.py 
 
import requests
 
# 填写你的 API Key
API_KEY = "sk-a09c76d135784ae9bb7543d758bedb3f"  
 
url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
 
data = {
    "model": "deepseek-reasoner",  # 指定使用 R1 模型（deepseek-reasoner）或者 V3 模型（deepseek-chat）
    "messages": [
        {"role": "system", "content": "你是一个专业的助手"},
        {"role": "user", "content": "你是谁？"}
    ],
    "stream": False  # 关闭流式传输
}
 
response = requests.post(url, headers=headers, json=data)
 
if response.status_code == 200:
    result = response.json()
    print(result['choices'][0]['message']['content'])
else:
    print("请求失败，错误码：", response.status_code)