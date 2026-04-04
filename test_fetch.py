import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://www.idx.co.id/primary/StockData/GetSecuritiesStock?length=9999'

# Testing headers to bypass Cloudflare
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.idx.co.id/id/data-pasar/data-saham/daftar-saham/',
    'Sec-Ch-Ua': '\"Microsoft Edge\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '\"Windows\"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

print("Testing Official IDX API...")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
        content = response.read().decode('utf-8')
        data = json.loads(content)
        print("Success! Downloaded", len(data.get('data', [])), "records.")
except Exception as e:
    print("Failed API fetch:", e)

print("Testing alternative fallback sources...")
urls = [
    'https://raw.githubusercontent.com/yofriadi/idn-stock-list/master/lq45.json',
    'https://raw.githubusercontent.com/yofriadi/idn-stock-list/main/lq45.json',
    'https://raw.githubusercontent.com/sahamin-dev/idn-stock-dataset/main/lq45.json',
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print("Github Success! Found at", u)
            break
    except Exception as e:
        print(f"Github failed at {u} : {e}")
