
import urllib.request
import json
import datetime
import urllib.parse
import re

today = datetime.datetime.utcnow()
date_wiki = today.strftime('%Y-%m-%d')
y = today.strftime('%Y')
m = today.strftime('%m')
d = today.strftime('%d')

# Step1: Wikimedia Featured Content API から今日の注目画像取得
url1 = f"https://api.wikimedia.org/feed/v1/wikipedia/ja/featured/{y}/{m}/{d}"
req = urllib.request.Request(url1, headers={
    'User-Agent': 'reTerminal-Dashboard/1.0 (github-actions)',
    'Api-User-Agent': 'reTerminal-Dashboard/1.0'
})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())

img = data.get('image', {})
image_url = img.get('image', {}).get('source', '') or img.get('thumbnail', {}).get('source', '')
title_ja = img.get('title', '').replace('File:', '').rsplit('.', 1)[0].replace('_', ' ')
title_ja = re.sub('<[^>]+>', '', title_ja).strip()
artist = img.get('artist', {}).get('text', '')
artist = re.sub('<[^>]+>', '', artist).strip()
desc_ja = img.get('description', {}).get('text', '')
desc_ja = re.sub('<[^>]+>', '', desc_ja).strip()

print(f"タイトル: {title_ja}")
print(f"画像URL: {image_url}")

# Step2: 日本語Wikipediaで豆知識を取得
trivia = ''
try:
    search_candidates = [title_ja, img.get('title', '').replace('File:', '').rsplit('.', 1)[0].replace('_', ' ')]
    extract = ''
    for candidate in search_candidates:
        if not candidate:
            continue
        search_url = f"https://ja.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={urllib.parse.quote(candidate)}&srlimit=1&origin=*" # type: ignore
        req_s = urllib.request.Request(search_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'}) # type: ignore
        with urllib.request.urlopen(req_s, timeout=10) as r:
            search_data = json.loads(r.read()) # type: ignore
        results = search_data.get('query', {}).get('search', [])
        if results:
            found_title = results[0]['title']
            ext_url = f"https://ja.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&explaintext=true&redirects=1&titles={urllib.parse.quote(found_title)}&origin=*" # type: ignore
            req_e = urllib.request.Request(ext_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'}) # type: ignore
            with urllib.request.urlopen(req_e, timeout=10) as r:
                ext_data = json.loads(r.read()) # type: ignore
            wiki_page = list(ext_data['query']['pages'].values())[0]
            extract = wiki_page.get('extract', '')
            if extract:
                break
    trivia = extract[:300].strip() if extract else ''
except:
    trivia = ''

trivia_block = f'<div id="trivia-label">豆知識</div><div id="trivia">{trivia}</div>' if trivia else ''

# Step5: HTML生成
html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:800px; height:480px; overflow:hidden; background:#111; font-family:sans-serif; }}
#bg-blur {{ position:absolute; inset:0; background:url('{image_url}') center/cover; filter:blur(18px); opacity:0.35; z-index:0; }}
#bg-wrap {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; z-index:1; }}
#bg-wrap img {{ max-width:100%; max-height:100%; object-fit:contain; }}
#overlay {{ position:absolute; bottom:0; left:0; right:0; padding:50px 20px 14px; background:linear-gradient(transparent,rgba(0,0,0,0.88)); color:white; z-index:2; }}
#title {{ font-size:20px; font-weight:bold; margin-bottom:4px; }}
#artist {{ font-size:12px; opacity:0.75; margin-bottom:6px; }}
#desc {{ font-size:13px; opacity:0.85; line-height:1.7; margin-bottom:6px; }}
#trivia-label {{ font-size:10px; opacity:1; margin-bottom:2px; letter-spacing:0.08em; }}
#trivia {{ font-size:11px; opacity:1; line-height:1.6; border-top:0.5px solid rgba(255,255,255,0.8); padding-top:6px; margin-top:4px; }}
</style>
</head>
<body>
<div id="bg-blur"></div>
<div id="bg-wrap"><img src="{image_url}"></div>
<div id="overlay">
  <div id="title">{title_ja}</div>
  <div id="artist">{artist}</div>
  <div id="desc">{desc_ja}</div>
  {trivia_block}
</div>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"完了: {title_ja}")

