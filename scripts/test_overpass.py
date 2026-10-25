import requests
import json

mirrors = [
    'https://overpass.kumi.systems/api/interpreter',
    'https://overpass.private.coffee/api/interpreter',
    'https://overpass-api.de/api/interpreter'
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
query = """
[out:json][timeout:25];
(
  way["highway"]["name"~"Kingston Bridge|George V Bridge|Glasgow Bridge|Clyde Arc"](55.84,-4.31,55.87,-4.24);
);
out body geom;
"""

for url in mirrors:
    print(f"Testing mirror: {url}")
    try:
        r = requests.post(url, data={'data': query}, headers=headers, timeout=20)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            elements = data.get('elements', [])
            print(f"SUCCESS! Elements found: {len(elements)}")
            for elem in elements[:5]:
                t = elem.get('tags', {})
                print(f"  Way {elem.get('id')}: {t.get('name')}, {t.get('highway')}, oneway={t.get('oneway')}, lanes={t.get('lanes')}")
            break
    except Exception as e:
        print(f"Failed: {e}")
