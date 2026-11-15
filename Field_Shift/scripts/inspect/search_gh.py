import urllib.request
import json

headers = {'User-Agent': 'FieldShiftBot/1.0'}

# Search GitHub code for '803514' or 'Athani'
url = "https://api.github.com/search/code?q=803514+repo:datameet/indian_village_boundaries"
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Search results for 803514 in datameet/indian_village_boundaries:")
        print("Total count:", data.get('total_count'))
        for item in data.get('items', [])[:5]:
            print(item.get('name'), item.get('path'))
except Exception as e:
    print("Error:", e)

