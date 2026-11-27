"""Story numbers for the Wire. Every story gets a number the first time it appears on the board:
month, its place in that month's count (three digits), and the Wire's year (2026 is year 0), written #11.143.0.
A story keeps its number for good. The register lives in numbers.json next to data.json.
Runs after every data.json change (see .github/workflows/share-pages.yml)."""
import json, os, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from share_pages import stories, slug

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, 'numbers.json')

def chicago_day(iso=None):
    # the board's own clock: San Antonio time (CST, UTC-6, or CDT, UTC-5 in summer)
    now = datetime.fromisoformat(iso) if iso else datetime.now(timezone.utc)
    if now.tzinfo is None: now = now.replace(tzinfo=timezone.utc)
    y = now.year
    def nth_sunday(m, n):
        d = datetime(y, m, 1, tzinfo=timezone.utc); d += timedelta(days=(6 - d.weekday()) % 7); return d + timedelta(weeks=n - 1)
    dst = nth_sunday(3, 2) + timedelta(hours=8) <= now.astimezone(timezone.utc) < nth_sunday(11, 1) + timedelta(hours=7)
    return now.astimezone(timezone(timedelta(hours=-5 if dst else -6))).date()

def assign(reg, data, day):
    nos = reg.setdefault('nos', {}); days = reg.setdefault('months', {})
    key = f'{day.year}-{day.month:02d}'; added = 0
    for title, _ in stories(data):
        sl = slug(title)
        if not sl or sl in nos: continue
        days[key] = days.get(key, 0) + 1
        nos[sl] = {'no': f'{day.month}.{days[key]:03d}.{day.year - 2026}', 'day': day.isoformat()}
        added += 1
    return added

def main():
    reg = json.load(open(REG, encoding='utf-8')) if os.path.exists(REG) else {}
    data = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
    n = assign(reg, data, chicago_day())
    json.dump(reg, open(REG, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    print('story numbers assigned:', n)

if __name__ == '__main__':
    main()
