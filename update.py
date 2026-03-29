
import urllib.request
import json
import datetime
import urllib.parse
import re

today = datetime.datetime.now()
y = today.strftime('%Y')
m = today.strftime('%m')
d = today.strftime('%d')

# Step1: 日本語版Wikipediaメインページから今日の一枚を取得
url1 = 'https://ja.wikipedia.org/w/api.php?action=parse&page=%E3%83%A1%E3%82%A4%E3%83%B3%E3%83%9A%E3%83%BC%E3%82%B8&prop=text&format=json'
req = urllib.request.Request(url1, headers={'User-Agent': 'reTerminal-Dashboard/1.0 (github-actions)'})
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())
html = data.get('parse', {}).get('text', {}).get('*', '')

# 今日の一枚セクションを切り出す
idx = html.find('今日の一枚')
section = html[idx:idx+3000]

# ファイル名取得（ファイル: リンク）
file_match = re.search(r'href=\"/wiki/(%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB:[^\"]+)\"', section)
file_name = urllib.parse.unquote(file_match.group(1)).replace('ファイル:', '') if file_match else ''

# 日本語タイトル/説明: mw-file-description の title 属性
title_match = re.search(r'class="mw-file-description"[^>]*title="([^"]+)"', section)
title_ja = title_match.group(1) if title_match else file_name.rsplit('.', 1)[0].replace('_', ' ')

# 本文中のキャプション（画像直下テキスト）
caption_match = re.search(r'</(?:img|span)></a><br\s*/>(.+?)</div>', section, re.DOTALL)
if caption_match:
    desc_ja = re.sub('<[^>]+>', '', caption_match.group(1)).strip()
else:
    desc_ja = title_ja

print(f"タイトル: {title_ja}")
print(f"ファイル名: {file_name}")

# Step2: 高解像度画像URLをimageinfo APIで取得
image_url = ''
if file_name:
    info_url = f'https://ja.wikipedia.org/w/api.php?action=query&titles=File:{urllib.parse.quote(file_name)}&prop=imageinfo&iiprop=url&format=json'
    req2 = urllib.request.Request(info_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
    with urllib.request.urlopen(req2, timeout=10) as r:
        info = json.loads(r.read())
    page_info = list(info['query']['pages'].values())[0]
    image_url = page_info.get('imageinfo', [{}])[0].get('url', '')

print(f"画像URL: {image_url}")

# Step3: 日本語Wikipediaで豆知識を取得
trivia = ''
try:
    search_q = title_ja.split('、')[0].split('の')[0]  # 最初のキーワードで検索
    search_url = f'https://ja.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={urllib.parse.quote(search_q)}&srlimit=1&origin=*'
    req_s = urllib.request.Request(search_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
    with urllib.request.urlopen(req_s, timeout=10) as r:
        search_data = json.loads(r.read())
    results = search_data.get('query', {}).get('search', [])
    if results:
        found_title = results[0]['title']
        ext_url = f'https://ja.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro=true&explaintext=true&redirects=1&titles={urllib.parse.quote(found_title)}&origin=*'
        req_e = urllib.request.Request(ext_url, headers={'User-Agent': 'reTerminal-Dashboard/1.0'})
        with urllib.request.urlopen(req_e, timeout=10) as r:
            ext_data = json.loads(r.read())
        wiki_page = list(ext_data['query']['pages'].values())[0]
        extract = wiki_page.get('extract', '')
        trivia = extract[:300].strip() if extract else ''
except:
    trivia = ''

trivia_block = f'<div id="trivia">{trivia}</div>' if trivia else ''

# Step4: HTML生成
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
#desc {{ font-size:13px; opacity:0.85; line-height:1.7; margin-bottom:6px; }}
#trivia {{ font-size:13px; opacity:1; line-height:1.6; border-top:0.5px solid rgba(255,255,255,0.8); padding-top:6px; margin-top:4px; }}
</style>
</head>
<body>
<div id="bg-blur"></div>
<div id="bg-wrap"><img src="{image_url}"></div>
<div id="overlay">
  <div id="title">{title_ja}</div>
  <div id="desc">{desc_ja}</div>
  {trivia_block}
</div>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"完了: {title_ja}")
