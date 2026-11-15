import urllib.request
import re

url = "https://erode.nic.in/document-category/maps/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'href=[\'"]([^\'"]+\.pdf)[\'"][^>]*>([^<]*)', html)
        print("Found PDF links:")
        for link, text in matches:
            print(f"- {text.strip()}: {link}")
except Exception as e:
    print("Error:", e)

