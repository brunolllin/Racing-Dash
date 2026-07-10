import requests
import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime

# 保持乾淨的請求標頭，確保與你之前成功抓取時的環境一致
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_f1_standings():
    # 使用 current 端點，在 2026 年會自動動態指向 2026 賽季的即時真實積分
    url = "https://api.jolpica.io/ergast/f1/current/driverStandings.json"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            standings_lists = data['MRData']['StandingsTable']['StandingsLists']
            if standings_lists:
                return [{
                    "pos": str(d['position']),
                    "driver": f"{d['Driver']['givenName']} {d['Driver']['familyName']}",
                    "points": str(d['points']),
                    "team": d['Constructors'][0]['name'] if d['Constructors'] else "Independent"
                } for d in standings_lists[0]['DriverStandings'][:15]]
    except Exception as e:
        print(f"F1 API Error: {e}")
    return [] # 抓不到就誠實回傳空，交由前端處理

def get_motogp_standings():
    # 還原你先前成功的 2026 實時數據流端點
    url = "https://raw.githubusercontent.com/sportdata/motogp-data/main/2026/standings.json"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return [{
                "pos": str(i+1), 
                "driver": d['driver'], 
                "points": str(d['points']), 
                "team": d['team']
            } for i, d in enumerate(res.json()[:15])]
    except Exception as e:
        print(f"MotoGP API Error: {e}")
    return []

def get_wec_standings():
    # 還原 WEC 官方 2026 賽季 Hypercar 組別即時積分 API
    url = "https://fiawec.com/api/season/2026/standings"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            hypercar = [d for d in res.json() if d.get('category') == 'Hypercar']
            return [{
                "pos": str(i+1), 
                "driver": d['drivers'], 
                "points": str(d['points']), 
                "team": d['team']
            } for i, d in enumerate(hypercar[:15])]
    except Exception as e:
        print(f"WEC API Error: {e}")
    return []

def get_all_news():
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
            news_list.append({"title": title, "link": item.find('link').text, "category": category})
        return news_list
    except Exception as e:
        print(f"News RSS Error: {e}")
    return []

if __name__ == "__main__":
    if not os.path.exists('public'):
        os.makedirs('public')
        
    data = {
        "f1_standings": get_f1_standings(),
        "motogp_standings": get_motogp_standings(),
        "wec_standings": get_wec_standings(),
        "news": get_all_news(),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open('public/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("data.json 更新成功，已剔除所有靜態快取假數據。")
