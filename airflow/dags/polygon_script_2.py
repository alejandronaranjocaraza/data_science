import requests


key = "oFqrkL3zTnVJ2GmKVpUiyqjN01GXhj4h"

stock_ticker = "AAPL"
date_str = "2025-01-03"
url = f"https://api.polygon.io/v1/open-close/{stock_ticker}/{date_str}?adjusted=true&apiKey={key}"

response = requests.get(url)

print(response.json())
