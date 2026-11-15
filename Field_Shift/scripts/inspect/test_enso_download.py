import urllib.request

urls = {
    "NOAA_ONI": "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
    "NOAA_NINO34_MONTHLY": "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.81-10.ascii",
    "PSL_DMI_IOD": "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for name, url in urls.items():
    print(f"Testing {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read(300).decode('utf-8', errors='ignore')
            print(f"Success! Status: {resp.status}, Sample:\n{content[:150]}\n")
    except Exception as e:
        print(f"Failed {name}: {e}\n")

