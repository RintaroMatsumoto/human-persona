import urllib.request, json, sys, os
key = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'key_token', 'dev_to_2.txt')).read().strip()
aid = sys.argv[1]
req = urllib.request.Request(f'https://dev.to/api/articles/{aid}', headers={'api-key': key, 'User-Agent': 'publish_to_devto/2.0', 'Accept': 'application/json'})
data = json.loads(urllib.request.urlopen(req).read())
keep = ('id', 'title', 'published', 'url', 'published_at', 'main_image', 'canonical_url', 'tags', 'description')
print(json.dumps({k: data.get(k) for k in keep}, ensure_ascii=False, indent=2))
