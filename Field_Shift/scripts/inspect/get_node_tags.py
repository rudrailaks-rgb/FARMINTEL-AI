import urllib.request
import xml.etree.ElementTree as ET

url = 'https://api.openstreetmap.org/api/0.6/node/1443165485'
req = urllib.request.Request(url, headers={'User-Agent': 'FieldShiftBot/1.0'})
try:
    with urllib.request.urlopen(req) as resp:
        root = ET.fromstring(resp.read().decode())
        print("OSM Node 1443165485 Tags:")
        for tag in root.findall('.//tag'):
            print(f"  {tag.attrib['k']}: {tag.attrib['v']}")
except Exception as e:
    print("Error:", e)

