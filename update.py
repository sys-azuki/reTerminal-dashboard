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
url1 = f"https://api.wikimedia.org/feed/v1/wikipedia/en/featured/{y}/{m}/{d}"
req = urllib.request.Request(url1, headers={
    'User-Agent': 'reTerminal-Dashboard/1.0 (github-actions)',
    'Api-User-Agent': 'reTerminal-Dashboard/1.0'
})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())

img = data.get('image', {})
image_url = img.get('image', {}).get('source', '') or img.get('thumbnail', {}).get('source', '')
title = img.get('title', '').replace('File:', '').rsplit('.', 1)[0].replace('_', ' ')
title = re.sub('<[^>]+>', '', title).strip()
artist = img.get('artist', {}).get('text', '')
artist = re.sub('<[^>]+>', '', artist).strip()
desc_en = img.get('description', {}).get('text', '')
desc_en = re.sub('<[^>]+>', '', desc_en).strip()

print(f"タイトル: {title}")
print(f"画像URL: {image_url}")

# Step2: 説明文を日本語翻訳
desc_ja = desc_en
if desc_en:
    try:
        trans_url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(desc_en)}&langpair=autodetect|ja"
        req3 = urllib.request.Request(trans_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
        with urllib.request.urlopen(req3, timeout=10) as r:
            trans_data = json.loads(r.read())
        desc_ja = trans_data['responseData']['translatedText']
    except:
        desc_ja = desc_en

# Step3: タイトルを日本語翻訳
title_ja = title
if title:
    try:
        trans_url2 = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(title)}&langpair=autodetect|ja"
        req4 = urllib.request.Request(trans_url2, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
        with urllib.request.urlopen(req4, timeout=10) as r:
            trans_data2 = json.loads(r.read())
        title_ja = trans_data2['responseData']['translatedText']
    except:
        title_ja = title

# Step4: Wikipedia検索で豆知識を取得・翻訳
trivia = ''
try:
    search_candidates = [title, img.get('title', '').replace('File:', '').rsplit('.', 1)[0].replace('_', ' ')]
    extract = ''
    for candidate in search_candidates:
        if not candidate:
            continue
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={urllib.parse.quote(candidate)}&srlimit=1&origin=*"
        req_s = urllib.request.Request(search_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
        with urllib.request.urlopen(req_s, timeout=10) as r:
            search_data = json.loads(r.read())
        results = search_data.get('query', {}).get('search', [])
        if results:
            found_title = results[0]['title']
            ext_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&explaintext=true&redirects=1&titles={urllib.parse.quote(found_title)}&origin=*"
            req_e = urllib.request.Request(ext_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
            with urllib.request.urlopen(req_e, timeout=10) as r:
                ext_data = json.loads(r.read())
            wiki_page = list(ext_data['query']['pages'].values())[0]
            extract = wiki_page.get('extract', '')
            if extract:
                break
    trivia_en = extract[:300].strip() if extract else ''
    if trivia_en:
        trans_url3 = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(trivia_en)}&langpair=autodetect|ja"
        req_t2 = urllib.request.Request(trans_url3, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
        with urllib.request.urlopen(req_t2, timeout=10) as r:
            trans3 = json.loads(r.read())
        trivia = trans3['responseData']['translatedText']
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
#trivia-label {{ font-size:10px; opacity:0.5; margin-bottom:2px; letter-spacing:0.08em; }}
#trivia {{ font-size:11px; opacity:0.6; line-height:1.6; border-top:0.5px solid rgba(255,255,255,0.3); padding-top:6px; margin-top:4px; }}
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
