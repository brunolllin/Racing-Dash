import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import os

def get_f1_standings():
    url = "https://ergast.com/api/f1/current/driverStandings.json"
    try:
        res = requests.get(url).json()
        standings = res['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        return [{"pos": d['position'], "driver": f"{d['Driver']['givenName']} {d['Driver']['familyName']}", "points": d['points'], "team": d['Constructors'][0]['name']} for d in standings[:15]]
    except:
        return []

def get_motogp_standings():
    # 爬取 Motorsport.com 2026 MotoGP 積分榜
    url = "https://www.motorsport.com/motogp/standings/2026/"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find('table').find_all('tr')[1:16] # 取前15名
        standings = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                standings.append({
                    "pos": cols[0].text.strip(),
                    "driver": cols[1].text.strip(),
                    "points": cols[-1].text.strip(), # 最後一格通常是總積分
                    "team": "MotoGP Rider"
                })
        return standings
    except:
        return []

def get_wec_standings():
    # 爬取 Motorsport.com 2026 WEC Hypercar 積分榜
    url = "https://www.motorsport.com/wec/standings/2026/"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.find('table').find_all('tr')[1:16]
        standings = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                standings.append({
                    "pos": cols[0].text.strip(),
                    "driver": cols[1].text.strip(),
                    "points": cols[-1].text.strip(),
                    "team": "WEC Driver"
                })
        return standings
    except:
        return []

def get_all_news():
    # 抓取綜合賽車新聞 RSS Feed
    url = "https://www.motorsport.com/rss/all/news/"
    try:
        res = requests.get(url)
        root = ET.fromstring(res.content)
        news_list = []
        for item in root.findall('.//item')[:15]: # 抓最新 15 條新聞
            title = item.find('title').text
            # 簡單分類標籤
            category = "綜合"
            if "F1" in title or "Formula 1" in title: category = "F1"
            elif "MotoGP" in title: category = "MotoGP"
            elif "WEC" in title or "Le Mans" in title: category = "WEC"
            
            news_list.append({
                "title": title,
                "link": item.find('link').text,
                "category": category
            })
        return news_list
    except:
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
