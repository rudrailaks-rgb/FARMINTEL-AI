import requests
import json

url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
# Point in Ames, Iowa: -93.6319, 42.0308
# Query to get mapunit and dominant component properties
query = """
SELECT TOP 1
    m.mukey, m.muname, m.musym,
    c.compname, c.comppct_r, c.drainagecl, c.hydgrp,
    ch.hzdept_r, ch.hzdepb_r, ch.sandtotal_r, ch.silttotal_r, ch.claytotal_r,
    ch.om_r, ch.ph1to1h2o_r, ch.awc_r, ch.ksat_r
FROM sacatalog sac
INNER JOIN legend l ON l.areasymbol = sac.areasymbol
INNER JOIN mapunit m ON m.lkey = l.lkey
INNER JOIN component c ON c.mukey = m.mukey AND c.majcompflag = 'Yes'
INNER JOIN chorizon ch ON ch.cokey = c.cokey AND ch.hzdept_r = 0
WHERE sac.areasymbol = 'IA169'
"""

headers = {"Content-Type": "application/json"}
payload = {"query": query, "format": "JSON"}

try:
    print("Testing SDA query...")
    resp = requests.post(url, json=payload, timeout=20)
    print("Status:", resp.status_code)
    data = resp.json()
    print("Table columns:", data.get("Table", [[]])[0] if data.get("Table") else "Empty")
    if len(data.get("Table", [])) > 1:
        print("First row:", data["Table"][1])
except Exception as e:
    print("Error:", e)
