import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')
api_key = os.getenv("HERE_API_KEY")

s,w,n,e = 35.70, 25.60, 42.20, 44.90
lat_step = (n - s) / 4
lon_step = (e - w) / 4

tile_south = s
tile_north = s + lat_step
tile_west = w
tile_east = w + lon_step
b = f"{tile_west:.6f},{tile_south:.6f},{tile_east:.6f},{tile_north:.6f}"

# 1/16th of Turkey
url = "https://data.traffic.hereapi.com/v7/flow"
r = requests.get(url, params={"apiKey": api_key, "in": "bbox:"+b, "locationReferencing": "shape"})
print(f"1/16th of Turkey Status: {r.status_code}")
if r.status_code != 200:
    print(r.text)
    
# Wait, let's try a smaller bbox
b2 = f"28.9,41.0,29.1,41.2" # istanbul 
r = requests.get(url, params={"apiKey": api_key, "in": "bbox:"+b2, "locationReferencing": "shape"})
print(f"Smaller Status: {r.status_code}")
