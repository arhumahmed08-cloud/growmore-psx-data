import requests, json, datetime, os

SYMBOLS = [
    "HBL","UBL","MCB","NBP","ENGRO","OGDC","PPL","PSO","LUCK","MLCF",
    "HUBC","KAPCO","SSGC","SNGP","KEL","UNITY","TRG","AVN","SEARL","COLG",
    "NESTLE","ICI","EFERT","FFC","FATIMA","DAWH","DGKC","PIOC","KOHC","CHCC",
    "BAFL","MEBL","FABL","AKBL","BAHL","SILK","JSBL","SNBL","BIPL","HMBL",
    "PAKT","AGTL","HCAR","INDU","GHNL","NCPL","HASCOL","APL","SHEL","ATRL"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://dps.psx.com.pk/",
}

def fetch_market():
    stocks = []
    try:
        r = requests.get("https://dps.psx.com.pk/market-watch", headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            stocks = data if isinstance(data, list) else data.get("data", data.get("stocks", []))
            print(f"Fetched {len(stocks)} stocks from market-watch")
    except Exception as e:
        print(f"market-watch failed: {e}")

    if not stocks:
        print("Trying individual symbols...")
        for sym in SYMBOLS:
            try:
                r = requests.get(f"https://dps.psx.com.pk/timeseries/eod/{sym}", headers=HEADERS, timeout=15)
                if r.status_code == 200:
                    d = r.json()
                    rows = d if isinstance(d, list) else d.get("data", [])
                    if rows:
                        latest = rows[-1]
                        stocks.append({
                            "symbol": sym,
                            "close": latest.get("c") or latest.get("close", 0),
                            "open":  latest.get("o") or latest.get("open",  0),
                            "high":  latest.get("h") or latest.get("high",  0),
                            "low":   latest.get("l") or latest.get("low",   0),
                            "volume":latest.get("v") or latest.get("volume",0),
                            "change":  0,
                            "change_p": 0,
                        })
                        print(f"  {sym}: OK")
            except Exception as e:
                print(f"  {sym}: {e}")

    return stocks

def fetch_indices():
    try:
        r = requests.get("https://dps.psx.com.pk/indices", headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"indices failed: {e}")
    return []

def main():
    print(f"Starting PSX fetch at {datetime.datetime.utcnow()} UTC")
    stocks  = fetch_market()
    indices = fetch_indices()

    output = {
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "updated_pk": (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).strftime("%d %b %Y %I:%M %p PKT"),
        "stocks":  stocks,
        "indices": indices,
        "count":   len(stocks),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w") as f:
        json.dump(output, f)

    print(f"Saved {len(stocks)} stocks to data/market.json")

if __name__ == "__main__":
    main()
