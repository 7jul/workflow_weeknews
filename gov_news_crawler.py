import os
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_page(url):
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding  # 自动检测编码
        return resp.text
    except Exception as e:
        print(f'请求失败: {e}')
        return None

def parse_news_list(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []
    
    for item in soup.select('.news_box li')[:10]:  # 假设新闻条目在li标签内
        link = item.find('a')
        if link:
            title = link.get_text(strip=True)
            href = link.get('href')
            full_url = urljoin(base_url, href)
            news_items.append({
                'title': title,
                'url': full_url
            })
    return news_items

def parse_news_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', class_='pages_content')  # 假设正文在特定div中
    return content.get_text(strip=True) if content else ''

def main():
    base_url = 'https://www.gov.cn/toutiao/liebiao/'
    
    list_html = get_page(base_url)
    if not list_html:
        return
    
    news_list = parse_news_list(list_html, base_url)
    results = []
    
    for news in news_list:
        print(f'正在处理: {news["title"]}')
        content_html = get_page(news['url'])
        if content_html:
            results.append({
                'title': news['title'],
                'content': parse_news_content(content_html)
            })
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'gov_news.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'成功抓取{len(results)}条新闻')

if __name__ == '__main__':
    main()