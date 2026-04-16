import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')
api_key = os.getenv("HERE_API_KEY")

for name, b in [("W,S,E,N", "28.97,41.00,28.99,41.02"), ("S,W,N,E", "41.00,28.97,41.02,28.99")]:
    url = "https://data.traffic.hereapi.com/v7/flow"
    r = requests.get(url, params={"apiKey": api_key, "in": "bbox:"+b, "locationReferencing": "shape"})
    print(f"{name}: {r.status_code}")
    if r.status_code == 200:
        res = r.json().get("results", [])
        print(f"Results: {len(res)}")
