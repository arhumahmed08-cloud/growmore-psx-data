import requests, json, datetime, os, time

SYMBOLS = [
    "HBL.KA","UBL.KA","MCB.KA","NBP.KA","ENGRO.KA","OGDC.KA","PPL.KA",
    "PSO.KA","LUCK.KA","MLCF.KA","HUBC.KA","SSGC.KA","SNGP.KA","KEL.KA",
    "TRG.KA","SEARL.KA","EFERT.KA","FFC.KA","FATIMA.KA","DGKC.KA",
    "PIOC.KA","KOHC.KA","CHCC.KA","BAFL.KA","MEBL.KA","FABL.KA",
    "AKBL.KA","BAHL.KA","PAKT.KA","AGTL.KA","HCAR.KA","INDU.KA",
    "NCPL.KA","APL.KA","SHEL.KA","ATRL.KA","MARI.KA","POL.KA",
    "PSMC.KA","LOTCHEM.KA","EPCL.KA","FFBL.KA","NETSOL.KA","SYS.KA",
    "PTCL.KA","MUGHAL.KA","ISL.KA","ASTL.KA","UNITY.KA","COLG.KA",
    "NESTLE.KA","ICI.KA","AVN.KA","DAWH.KA","SILK.KA","JSBL.KA",
    "SNBL.KA","BIPL.KA","HMBL.KA","GHGL.KA","NRL.KA","KAPCO.KA",
    "TELE.KA","WTL.KA","INIL.KA","HASCOL.KA"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def fetch_yahoo(symbol):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol + "?interval=1d&range=5d"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        result = data["chart"]["result"]
        if not result:
            return None
        meta = result[0]["meta"]
        close = float(meta.get("regularMarketPrice", 0))
        prev = float(meta.get("chartPreviousClose", close))
        chg = round(close - prev, 2)
        chgP = round((chg / prev * 100) if prev else 0, 2)
        vol = meta.get("regularMarketVolume", 0)
        sym = symbol.replace(".KA", "")
        stock = {
            "symbol": sym,
            "close": close,
            "open": float(meta.get("regularMarketOpen", 0)),
            "high": float(meta.get("regularMarketDayHigh", 0)),
            "low": float(meta.get("regularMarketDayLow", 0)),
            "volume": int(vol) if vol else 0,
            "change": chg,
            "change_p": chgP,
            "sector": meta.get("longName", ""),
        }
        return stock
    except Exception as e:
        print("  " + symbol + ": " + str(e))
        return None

def fetch_index(symbol, name):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + symbol + "?interval=1d&range=2d"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        result = data["chart"]["result"]
        if not result:
            return None
        meta = result[0]["meta"]
        val = float(meta.get("regularMarketPrice", 0))
        prev = float(meta.get("chartPreviousClose", val))
        chg = round(val - prev, 2)
        chgP = round((chg / prev * 100) if prev else 0, 2)
        return {"name": name, "value": val, "change": chg, "change_p": chgP}
    except Exception as e:
        print("  " + name + ": " + str(e))
        return None

def main():
    print("=== PSX Fetch via Yahoo Finance: " + str(datetime.datetime.utcnow()) + " UTC ===")

    stocks = []
    for sym in SYMBOLS:
        result = fetch_yahoo(sym)
        if result:
            stocks.append(result)
            print("  " + result["symbol"] + ": PKR " + str(result["close"]) + " (" + str(result["change"]) + ")")
        else:
            print("  " + sym + ": no data")
        time.sleep(0.3)

    indices = []
    index_list = [("^KSE100", "KSE100"), ("^KSE30", "KSE30"), ("^ALLSHR", "ALLSHR")]
    for sym, name in index_list:
        idx = fetch_index(sym, name)
        if idx:
            indices.append(idx)
            print("  " + name + ": " + str(idx["value"]))
        time.sleep(0.3)

    now_utc = datetime.datetime.utcnow()
    now_pk = now_utc + datetime.timedelta(hours=5)

    output = {
        "updated_at": now_utc.isoformat() + "Z",
        "updated_pk": now_pk.strftime("%d %b %Y %I:%M %p PKT"),
        "stocks": stocks,
        "indices": indices,
        "count": len(stocks),
        "source": "Yahoo Finance"
    }

    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w") as f:
        json.dump(output, f)

    print("=== Saved " + str(len(stocks)) + " stocks, " + str(len(indices)) + " indices ===")

if __name__ == "__main__":
    main()
