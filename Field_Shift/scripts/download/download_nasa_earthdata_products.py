"""
Script: download_nasa_earthdata_products.py
Purpose: Download NASA Earthdata products (SMAP, MODIS MOD13Q1, GPM IMERG) for Athani study area
         using official NASA Earthdata Login (EDL) authentication.
Author: Senior Geospatial Data Engineer, Field Shift Project
"""

import os
import urllib.request
import json
import ssl

def download_authenticated_file(url, target_path, username=None, password=None, token=None):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    print(f"Requesting: {url}")
    print(f"Target: {target_path}")
    
    headers = {'User-Agent': 'FieldShiftBot/1.0 (NASA Space Apps Challenge; contact@fieldshift.local)'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        
    req = urllib.request.Request(url, headers=headers)
    
    # Setup password manager if username and password are provided
    if username and password:
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, "https://urs.earthdata.nasa.gov", username, password)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)
        
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            content = resp.read()
            with open(target_path, "wb") as f:
                f.write(content)
            size_mb = os.path.getsize(target_path) / (1024 * 1024)
            print(f"Success: {size_mb:.2f} MB downloaded to {target_path}")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}: {e.reason}")
        if e.code == 401:
            print("Authentication required. Please authenticate via NASA Earthdata Login.")
        return False
    except Exception as e:
        print(f"Download error: {e}")
        return False

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    # Check for credentials in environment or ~/.netrc
    netrc_path = os.path.expanduser("~/.netrc")
    edl_token = os.environ.get("EARTHDATA_TOKEN")
    edl_user = os.environ.get("EARTHDATA_USERNAME")
    edl_pass = os.environ.get("EARTHDATA_PASSWORD")
    
    print("Checking Earthdata authentication credentials...")
    if not edl_token and not (edl_user and edl_pass) and not os.path.exists(netrc_path):
        print("NOTICE: No active Earthdata Login credentials found.")
        print("Please set EARTHDATA_TOKEN or configure ~/.netrc to authorize SMAP/MODIS/GPM downloads.")
        return
        
    print("Credentials detected. Ready to download target granules.")

if __name__ == "__main__":
    main()

