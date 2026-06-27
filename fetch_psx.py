import requests, json, datetime, os, time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://dps.psx.com.pk/",
    "Origin": "https://dps.psx.com.pk",
    "Connection": "keep-alive",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

SYMBOLS = [
    "HBL","UBL","MCB","NBP","ENGRO","OGDC","PPL","PSO","LUCK","MLCF",
    "HUBC","KAPCO","SSGC","SNGP","KEL","UNITY","TRG","AVN","SEARL","COLG",
    "NESTLE","ICI","EFERT","FFC","FATIMA","DGKC","PIOC","KOHC","CHCC","BAFL",
    "MEBL","FABL","AKBL","BAHL","PAKT","AGTL","HCAR","INDU","NCPL","HASCOL",
    "APL","SHEL","ATRL","DAWH","SILK","JSBL","SNBL","BIPL","HMBL","GHGL",
    "MARI","POL","BYCO","NRL","PRL","PSMC","GHNL","GHNI","FHAM","LOTCHEM",
    "EPCL","FFBL","AGHA","MUGHAL","ISL","ASTL","INIL","NETSOL","SYS","TPS",
    "TPLP","TELE","PTCL","WTL","CNERGY","EPQL","HUBC","PKGP","LPCL","FECM"
]

def fetch_with_session():
    session = requests.Session()
    stocks = []

    # Step 1: Visit homepage first to get cookies
    try:
        print("Getting session cookies...")
        session.get("https://dps.psx.com.pk/", headers={
            "User-Agent": HEADERS["User-Agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }, timeout=20)
        time.sleep(2)
    except Exception as e:
        print(f"Homepage visit failed: {e}")

    # Step 2: Try market-watch endpoint
    try:
        print("Fetching market-watch...")
        r = session.get("https://dps.psx.com.pk/market-watch", headers=HEADERS, timeout=30)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            stocks = data if isinstance(data, list) else data.get("data", data.get("stocks", []))
            print(f"  Got {len(stocks)} stocks")
    except Exception as e:
        print(f"  market-watch failed: {e}")

    # Step 3: Try screener endpoint as fallback
    if not stocks:
        try:
            print("Trying screener endpoint...")
            r = session.get("https://dps.psx.com.pk/screener", headers=HEADERS, timeout=30)
            print(f"  Status: {r.status_code}, Length: {len(r.text)}")
            if r.status_code == 200 and r.text.strip().startswith('['):
                stocks = r.json()
                print(f"  Got {len(stocks)} stocks from screener")
        except Exception as e:
            print(f"  screener failed: {e}")

    # Step 4: Try individual EOD as last resort
    if not stocks:
        print("Falling back to individual symbol EOD fetch...")
        for sym in SYMBOLS:
            try:
                r = session.get(
                    f"https://dps.psx.com.pk/timeseries/eod/{sym}",
                    headers=HEADERS, timeout=15
                )
                if r.status_code == 200:
                    rows = r.json()
                    rows = rows if isinstance(rows, list) else rows.get("data", [])
                    if rows:
                        latest = rows[-1]
                        prev   = rows[-2] if len(rows) > 1 else latest
                        close  = float(latest.get("c") or latest.get("close") or 0)
                        prev_c = float(prev.get("c")   or prev.get("close")   or close)
                        chg    = round(close - prev_c, 2)
                        chgP   = round((chg / prev_c * 100) if prev_c else 0, 2)
                        stocks.append({
                            "symbol":   sym,
                            "close":    close,
                            "open":     float(latest.get("o") or latest.get("open")   or 0),
                            "high":     float(latest.get("h") or latest.get("high")   or 0),
                            "low":      float(latest.get("l") or latest.get("low")    or 0),
                            "volume":   int(latest.get("v")   or latest.get("volume") or 0),
                            "change":   chg,
                            "change_p": chgP,
                        })
                        print(f"  {sym}: PKR {close} ({chg:+.2f})")
                        time.sleep(0.3)
            except Exception as e:
                print(f"  {sym}: {e}")

    return stocks

def fetch_indices(session):
    try:
        r = session.get("https://dps.psx.com.pk/indices", headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Indices failed: {e}")
    return []

def main():
    print(f"\n=== PSX Fetch started: {datetime.datetime.utcnow()} UTC ===\n")
    stocks  = fetch_with_session()

    session = requests.Session()
    indices = fetch_indices(session)

    output = {
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "updated_pk": (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).strftime("%d %b %Y %I:%M %p PKT"),
        "stocks":     stocks,
        "indices":    indices,
        "count":      len(stocks),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w") as f:
        json.dump(output, f)

    print(f"\n=== Saved {len(stocks)} stocks, {len(indices)} indices ===")

if __name__ == "__main__":
    main()
