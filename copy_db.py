import urllib.request
import json
import urllib.parse
api_key = '$2a$10$b1zk.UlxUmhefLmBtQ66DOhVPYpHQN6tYqtixNMQrAJGBDCWlYxey'
req_get = urllib.request.Request('https://api.jsonbin.io/v3/b/69d3d50daaba882197cd3fbd/latest', headers={'X-Master-Key': api_key, 'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req_get)
data = json.loads(resp.read().decode('utf-8'))['record']

encoded = json.dumps(data, ensure_ascii=False).encode('utf-8')
req_put = urllib.request.Request('https://api.jsonbin.io/v3/b/69e69213aaba8821971d5604', data=encoded, method='PUT', headers={'X-Master-Key': api_key, 'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'Mozilla/5.0'})
urllib.request.urlopen(req_put)
print("Copied successfully.")
