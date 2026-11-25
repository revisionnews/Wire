"""Builds one small page per story at s/<story>/ so a shared link shows a preview:
Revision News Wire, the headline, and one line of the story. The page then opens the story on the Wire.
Runs after every data.json change (see .github/workflows/share-pages.yml)."""
import html, json, os, re, unicodedata

SITE = 'https://wire.revision.news/'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def slug(t):
    t = unicodedata.normalize('NFKD', str(t or '').lower())
    t = ''.join(ch for ch in t if not unicodedata.combining(ch))
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:70]
    return t.rstrip('-')

def first_line(text, limit=160):
    text = re.sub(r'\s+', ' ', str(text or '')).strip()
    m = re.match(r'(.+?[.!?])(\s|$)', text)
    line = m.group(1) if m else text
    return line if len(line) <= limit else line[:limit - 1].rsplit(' ', 1)[0] + '…'

def stories(d):
    def t(i, top=False):
        return (i.get('headline') or i.get('title')) if top else (i.get('title') or i.get('headline'))
    for k in ('breaking', 'top'):
        for i in d.get(k) or []:
            yield t(i, True), i.get('summary')
    for c in d.get('compare') or []:
        hs = c.get('headlines') or []
        ai = next((h for h in hs if h.get('k') == 'AI'), hs[0] if hs else None)
        if ai:
            yield ai.get('headline'), ai.get('summary')
    for k in ('sports', 'politics', 'artistry', 'revolution', 'community', 'business', 'schools',
              'safety', 'weather', 'memos', 'events', 'county', 'city', 'ccrs', 'spurs', 'unions', 'neighborhoods'):
        for i in d.get(k) or []:
            if isinstance(i, dict):
                yield t(i), i.get('summary')
    for g in d.get('meeting_groups') or []:
        if g.get('title'):
            yield 'Meetings for ' + g['title'], g.get('note') or ''
    for a in ((d.get('archive') or {}).get('items') or []):
        yield a.get('h') or a.get('headline'), a.get('summary')

PAGE = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:site_name" content="Revision News Wire">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}apple-touch-icon.png?v=2">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="icon" href="/favicon.ico?v=2"><link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<meta http-equiv="refresh" content="0;url=/?s={slug}">
<script>location.replace('/?s={slug}')</script>
</head><body style="font-family:sans-serif;background:#D4D4D4"><p><a href="/?s={slug}">{title}</a></p></body></html>
'''

def main():
    d = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
    n = 0
    for title, summary in stories(d):
        sl = slug(title)
        if not sl:
            continue
        out = os.path.join(ROOT, 's', sl)
        os.makedirs(out, exist_ok=True)
        e = lambda x: html.escape(str(x or ''), quote=True)
        page = PAGE.format(title=e(title), desc=e(first_line(summary)), url=SITE + 's/' + sl + '/', site=SITE, slug=sl)
        path = os.path.join(out, 'index.html')
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != page:
            open(path, 'w', encoding='utf-8').write(page)
            n += 1
    print('share pages written:', n)

if __name__ == '__main__':
    main()
