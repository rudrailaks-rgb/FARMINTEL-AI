import requests

url = "https://sdmdataaccess.nrcs.usda.gov/Tabular/post.rest"
q = "SELECT * FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('point(-93.6319 42.0308)')"
r = requests.post(url, json={"query": q, "format": "JSON"})
print("Status:", r.status_code)
print("Response:", r.text)
