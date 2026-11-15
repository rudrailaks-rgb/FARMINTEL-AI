import requests
import json

url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
lat = 42.0308
lon = -93.6319

query = f"""
SELECT TOP 1
    m.mukey, m.muname, m.musym,
    c.compname, c.comppct_r, c.drainagecl, c.hydgrp,
    ch.hzname, ch.hzdept_r, ch.hzdepb_r, ch.sandtotal_r, ch.silttotal_r, ch.claytotal_r,
    ch.om_r, ch.ph1to1h2o_r, ch.awc_r, ch.ksat_r
FROM SDA_Get_Mukey_from_intersection_with_Wkt('POINT({lon} {lat})') p
INNER JOIN mapunit m ON m.mukey = p.mukey
INNER JOIN component c ON c.mukey = m.mukey AND c.majcompflag = 'Yes'
LEFT JOIN chorizon ch ON ch.cokey = c.cokey AND ch.hzdept_r = 0
ORDER BY c.comppct_r DESC
"""

payload = {"query": query, "format": "JSON"}
try:
    resp = requests.post(url, json=payload, timeout=20)
    print("Spatial query status:", resp.status_code)
    data = resp.json()
    print("Table:", data.get("Table"))
except Exception as e:
    print("Error:", e)
