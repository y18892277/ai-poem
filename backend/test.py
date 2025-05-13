from zhipuai import ZhipuAI
client = ZhipuAI(api_key="88ffb5e0bfbf45cd9fda66e87135ee74.MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAvMoglRYXkkFlWKSRGZ2vc/heVX4sjdsRKLsbpGQ4MABA3TL6pJsJiQA0kzKiLnErDaUrbu3LSh1L9HV4cX2hRwIDAQABAkAd8Ev0eJlqVzaUNRzRnCEL2hJTqnu0T05MUEfU7RPAALQJMY39THHov44uwI1P04Kz0b/YSdGL57jhp5eLhEFZAiEA+GgwgtP8BsS2x84pW4MG1j6HHZmTMtrE/wftRdO4k+MCIQDCj2zZViPrdcxFhfwlSLHfxkNt0sBODZ+Q5h21dWciTQIhAL4Q8nVX//Gp2HT/MLPdiICrbTTfyjpSHANLLGiOPB+jAiBGEUUQGFejSq8gMpqWCtIUVuCdwpKDCaD3nAgC+58C2QIgWTQ7vR5vVUGk6CQo3xtEEdgDwrtC/ehpp3dff8jU+m8=")  # 请填写您自己的APIKey
response = client.chat.completions.create(
    model="glm-4-plus",  # 请填写您要调用的模型名称
    messages=[
        {"role": "user", "content": "作为一名营销专家，请为我的产品创作一个吸引人的口号"},
        {"role": "assistant", "content": "当然，要创作一个吸引人的口号，请告诉我一些关于您产品的信息"},
        {"role": "user", "content": "智谱AI开放平台"},
        {"role": "assistant", "content": "点燃未来，智谱AI绘制无限，让创新触手可及！"},
        {"role": "user", "content": "创作一个更精准且吸引人的口号"}
    ],
)
print(response)