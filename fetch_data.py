import requests
import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime

def get_f1_standings():
    # Ergast 停用後，2026 年必須改用 Jolpica 代替端點以獲取即時動態積分
    url = "https://api.jolpica.io/ergast/f1/2026/driverStandings.json"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            standings_lists = data['MRData']['StandingsTable']['StandingsLists']
            if standings_lists:
                standings = standings_lists[0]['DriverStandings']
                return [{
                    "pos": str(d['position']),
                    "driver": f"{d['Driver']['givenName']} {d['Driver']['familyName']}",
                    "points": str(d['points']),
                    "team": d['Constructors'][0]['name'] if d['Constructors'] else "Independent"
                } for d in standings[:15]]
    except Exception as e:
        print(f"F1 實時 API 請求失敗: {e}")
    return []

def get_motogp_standings():
    # 使用 2026 即時維護的開源賽事節點
    url = "https://raw.githubusercontent.com/sportdata/motogp-data/main/2026/standings.json"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            return [{"pos": str(i+1), "driver": d['driver'], "points": str(d['points']), "team": d['team']} for i, d in enumerate(res.json()[:15])]
    except:
        pass
    return []

def get_wec_standings():
    # 2026 WEC Hypercar 實時動態源
    url = "https://fiawec.com/api/season/2026/standings"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            hypercar = [d for d in res.json() if d.get('category') == 'Hypercar']
            return [{"pos": str(i+1), "driver": d['drivers'], "points": str(d['points']), "team": d['team']} for i, d in enumerate(hypercar[:15])]
    except:
        pass
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
    except:
        return [{"title": "賽事動態實時更新中", "link": "#", "category": "綜合"}]

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
