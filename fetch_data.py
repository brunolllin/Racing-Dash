import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import os

def get_f1_standings():
    # 因為 Ergast API 已停止維護，改用 2026 年社群主流的開源 OpenF1 API 或直接爬取官方替代源
    # 這裡採用對自動化請求最友善的 BBC Sport / Sky Sports 數據源
    url = "https://www.bbc.com/sport/formula1/standings"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table:
            return []
        rows = table.find_all('tr')[1:16]
        standings = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                standings.append({
                    "pos": cols[0].text.strip(),
                    "driver": cols[1].text.strip(),
                    "team": cols[2].text.strip() if len(cols) > 3 else "F1 Team",
                    "points": cols[-1].text.strip()
                })
        return standings
    except Exception as e:
        print(f"F1 Error: {e}")
        return []

def get_motogp_standings():
    # MotoGP 換到數據結構最乾淨的 Crash.net 爬取
    url = "https://www.crash.net/motogp/standings/2026"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table:
            # 嘗試找其他表格標籤
            table = soup.find('div', class_='table-responsive') or soup.find('div', class_='view-content')
        
        rows = table.find_all('tr')[1:16] if table else []
        standings = []
        for row in rows:
            cols = [td.text.strip() for td in row.find_all('td')]
            if len(cols) >= 3:
                standings.append({
                    "pos": cols[0],
                    "driver": cols[1],
                    "points": cols[-1]
                })
        return standings
    except Exception as e:
        print(f"MotoGP Error: {e}")
        return []

def get_wec_standings():
    # WEC 改抓官方或替代權威運動媒體
    url = "https://www.eurosport.com/wec/standings.shtml"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')[1:16] if table else []
        standings = []
        for row in rows:
            cols = [td.text.strip() for td in row.find_all('td')]
            if len(cols) >= 3:
                standings.append({
                    "pos": cols[0],
                    "driver": cols[1],
                    "points": cols[-1]
                })
        return standings
    except Exception as e:
        print(f"WEC Error: {e}")
        return []

def get_all_news():
    # Motorsport RSS 有時會擋 GitHub Actions 的 IP，改用非營利、無防爬機制的公共賽車新聞源
    url = "https://www.autosport.com/rss/f1/news/"
    try:
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.content)
        news_list = []
        for item in root.findall('.//item')[:15]:
            title = item.find('title').text
            category = "綜合"
            if "F1" in title or "Formula 1" in title: category = "F1"
            elif "MotoGP" in title or "Moto" in title: category = "MotoGP"
            elif "WEC" in title or "Hypercar" in title or "Le Mans" in title: category = "WEC"
            
            news_list.append({
                "title": title,
                "link": item.find('link').text,
                "category": category
            })
        return news_list
    except Exception as e:
        print(f"News Error: {e}")
        return []

if __name__ == "__main__":
    if not os.path.exists('public'):
        os.makedirs('public')
        
    data = {
        "f1_standings": get_f1_standings(),
        "motogp_standings": get_motogp_standings(),
        "wec_standings": get_wec_standings(),
        "news": get_all_news()
    }
    
    with open('public/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
