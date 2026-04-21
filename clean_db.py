import urllib.request
import json
api_key = '$2a$10$b1zk.UlxUmhefLmBtQ66DOhVPYpHQN6tYqtixNMQrAJGBDCWlYxey'

for bin_id in ['69d3d50daaba882197cd3fbd', '69e69213aaba8821971d5604']:
    req_get = urllib.request.Request(f'https://api.jsonbin.io/v3/b/{bin_id}/latest', headers={'X-Master-Key': api_key, 'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req_get)
    data = json.loads(resp.read().decode('utf-8'))['record']

    duplicate_count = 0
    if 'sprints' in data:
        for s in data['sprints']:
            if 'items' in s:
                unique_items = {}
                for item in reversed(s['items']):
                    # Normalize string to catch sneaky duplicates
                    normalized_name = str(item.get('name', '')).strip().lower().replace(' ', '')
                    if normalized_name not in unique_items:
                        unique_items[normalized_name] = item
                    else:
                        duplicate_count += 1
                        print(f"Removed duplicate: {repr(item.get('name'))} vs kept {repr(unique_items[normalized_name].get('name'))}")
                s['items'] = list(reversed(list(unique_items.values())))
    
    if duplicate_count > 0:
        encoded = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req_put = urllib.request.Request(f'https://api.jsonbin.io/v3/b/{bin_id}', data=encoded, method='PUT', headers={'X-Master-Key': api_key, 'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req_put)
        print(f"Removed {duplicate_count} duplicates from bin {bin_id}")
    else:
        print(f"No duplicates found in bin {bin_id}")
