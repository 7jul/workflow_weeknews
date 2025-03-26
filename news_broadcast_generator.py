import json
import os
import re
import requests
from datetime import datetime
import random
import string

def generate_broadcast():
    # 读取API密钥
    api_key = _get_api_key()
    if not api_key:
        print("错误：未找到api.key文件")
        return

    # 加载新闻数据
    try:
        with open('gov_news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        if len(news_data) != 10:
            print(f"新闻条目数量错误，预期10条，实际{len(news_data)}条")
            return
    except Exception as e:
        print(f"加载新闻数据失败：{str(e)}")
        return

    # 处理全部新闻
    print(f"正在处理{len(news_data)}条新闻...")
    combined_content = '\n\n'.join([_process_content(news) for news in news_data])
    broadcast = _call_deepseek_api(api_key, combined_content)
    if broadcast:
        _save_to_file(broadcast, "每周新闻播报")

def _process_content(news):
    # 统一替换称呼
    content = f"{news['title']}\n{news.get('content', '')}"
    pattern = r"习近平主席|习总书记|习主席|习近平"
    return re.sub(pattern, "习爷爷", content)

def _call_deepseek_api(api_key, content):
    prompt = f"请将以下10条新闻整合成一篇适合学生播报的一周新闻稿，栏目名称叫《红领巾一周新闻播报》，要求：\n1. 纯文字稿，字数3000字以上\n2. 尽可能保留原新闻的重要信息，添加背景知识和\n3. 使用'首先'、'接下来'、'最后'等过渡词连接不同新闻\n4. 语言口语化且生动有趣，适当使用比喻和拟人手法\n5. 保持整体结构连贯自然，包含开头问候和结尾总结\n新闻原文如下：\n{content}"

    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": "你是一个语文老师，擅长将新闻改写为适合学生播报的新闻稿"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,
                "max_tokens": 8000,
          
            }
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"API请求失败：{response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常：{str(e)}")
        return None

def _save_to_file(content, title):
    # 生成文件名
    date_str = datetime.now().strftime('%Y%m%d')
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    filename = f"broadcast_{date_str}_{rand_str}.txt"
    # 清理重复标题
    content = re.sub(r'#{2,}.*?\n', '', content)

    # 清理多余内容
    cleaned_content = _remove_think_content(content)
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{cleaned_content}")
        print(f"已保存文件：{filename}")
    except Exception as e:
        print(f"保存失败：{str(e)}")

def _remove_think_content(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def _get_api_key():
    key_path = os.path.join(os.path.dirname(__file__), "api.key")
    if os.path.exists(key_path):
        with open(key_path, 'r') as f:
            return f.read().strip()
    return None

if __name__ == "__main__":
    generate_broadcast()