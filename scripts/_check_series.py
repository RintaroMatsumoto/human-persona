import urllib.request, json, os
key = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'key_token', 'dev_to_2.txt')).read().strip()
out = []
page = 1
while True:
    req = urllib.request.Request(f'https://dev.to/api/articles/me/all?page={page}&per_page=100', headers={'api-key': key, 'User-Agent': 'check_series/1.0', 'Accept': 'application/json'})
    data = json.loads(urllib.request.urlopen(req).read())
    if not data: break
    out.extend(data)
    if len(data) < 100: break
    page += 1
from collections import Counter
series_counts = Counter((a.get('collection_id') or a.get('series') or '<none>') for a in out)
print(f'Total articles: {len(out)}')
print('series/collection_id distribution:')
for s, c in series_counts.most_common():
    print(f'  {c:3d}  {s!r}')
print('---')
# Group by collection_id to find the 41-series
groups: dict = {}
for a in out:
    k = a.get('collection_id') or a.get('series') or '<none>'
    groups.setdefault(k, []).append(a)
biggest = max(groups.values(), key=len)
print(f'Biggest group ({len(biggest)} articles):')
for a in sorted(biggest, key=lambda x: x.get('id', 0)):
    print(f"  [{a.get('id')}] published={a.get('published')!s:5}  {a.get('title')}")
