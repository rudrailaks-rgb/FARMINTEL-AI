import requests
import json

url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
lat = 42.0308
lon = -93.6319

query = f"""
SELECT
    m.mukey, m.muname, m.musym,
    c.cokey, c.compname, c.comppct_r, c.drainagecl, c.hydgrp,
    ch.chkey, ch.hzname, ch.hzdept_r, ch.hzdepb_r,
    ch.sandtotal_r, ch.silttotal_r, ch.claytotal_r,
    ch.om_r, ch.ph1to1h2o_r, ch.awc_r, ch.ksat_r
FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('point({lon} {lat})') p
INNER JOIN mapunit m ON m.mukey = p.mukey
INNER JOIN component c ON c.mukey = m.mukey AND c.majcompflag = 'Yes'
LEFT JOIN chorizon ch ON ch.cokey = c.cokey
ORDER BY c.comppct_r DESC, ch.hzdept_r ASC
"""

r = requests.post(url, json={"query": query, "format": "JSON"})
print("Status:", r.status_code)
data = r.json()
table = data.get("Table", [])
print(f"Returned {len(table)} rows:")
for row in table[:6]:
    print(row)
