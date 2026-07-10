import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET

def get_f1_standings():
    # 抓取 2026 最新 F1 積分榜
    url = "https://ergast.com/api/f1/current/driverStandings.json"
    try:
        res = requests.get(url).json()
        standings = res['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        return [{"pos": d['position'], "driver": d['Driver']['familyName'], "points": d['points'], "team": d['Constructors'][0]['name']} for d in standings]
    except:
        return []

def get_racing_news():
    # 抓取賽車新聞 RSS Feed
    url = "https://www.motorsport.com/rss/f1/news/"
    try:
        res = requests.get(url)
        root = ET.fromstring(res.content)
        news_list = []
        for item in root.findall('.//item')[:10]:
            news_list.append({
                "title": item.find('title').text,
                "link": item.find('link').text
            })
        return news_list
    except:
        return []

if __name__ == "__main__":
    # 建立一個存放資料的目錄（如果不存在的話）
    import os
    if not os.path.exists('public'):
        os.makedirs('public')
        
    data = {
        "f1_standings": get_f1_standings(),
        "news": get_racing_news()
    }
    with open('public/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
