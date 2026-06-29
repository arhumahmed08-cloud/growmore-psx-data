import json, datetime, os, time, sys, subprocess

subprocess.check_call([sys.executable, "-m", "pip", "install", "psxdata", "-q"])

import psxdata

def safe_float(val, default=0.0):
    try:
        return float(val) if val is not None else default
    except:
        return default

def safe_int(val, default=0):
    try:
        return int(float(val)) if val is not None else default
    except:
        return default

def main():
    now_utc = datetime.datetime.utcnow()
    now_pk  = now_utc + datetime.timedelta(hours=5)
    print("=== PSX Fetch started: " + str(now_utc) + " UTC ===")

    stocks  = []
    indices = []

    # STEP 1: Get tickers
    try:
        tickers = list(psxdata.tickers())
        print("Total tickers: " + str(len(tickers)))
    except Exception as e:
        print("tickers() failed: " + str(e))
        tickers = [
            "HBL","UBL","MCB","NBP","ENGRO","OGDC","PPL","PSO","LUCK","MLCF",
            "HUBC","SSGC","SNGP","KEL","TRG","SEARL","EFERT","FFC","FATIMA",
            "DGKC","PIOC","KOHC","CHCC","BAFL","MEBL","FABL","AKBL","BAHL",
            "PAKT","AGTL","HCAR","INDU","NCPL","APL","SHEL","ATRL","MARI",
            "POL","LOTCHEM","EPCL","FFBL","NETSOL","SYS","PTCL","MUGHAL",
            "ISL","ASTL","UNITY","COLG","NESTLE","ICI","AVN","KAPCO","INIL",
            "JSBL","SNBL","BIPL","HMBL","GHGL","NRL","TELE","WTL","HASCOL"
        ]

    # STEP 2: Fetch EOD data for accurate OHLCV + correct change
    end_date   = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=10)

    print("Fetching EOD data for accurate OHLCV...")
    for sym in tickers[:100]:
        try:
            df = psxdata.stocks(sym, start=str(start_date), end=str(end_date))
            if df is not None and not df.empty:
                # Get last 2 rows for change calculation
                latest = df.iloc[-1]
                prev   = df.iloc[-2] if len(df) > 1 else latest

                # Try different column name formats
                def get_col(row, names):
                    for n in names:
                        if n in row.index and row[n] is not None:
                            v = row[n]
                            if str(v) not in ['nan', 'None', '']:
                                return v
                    return 0

                close  = safe_float(get_col(latest, ['Close','close','CLOSE']))
                open_  = safe_float(get_col(latest, ['Open', 'open', 'OPEN']))
                high   = safe_float(get_col(latest, ['High', 'high', 'HIGH']))
                low    = safe_float(get_col(latest, ['Low',  'low',  'LOW']))
                vol    = safe_int(get_col(latest,   ['Volume','volume','VOLUME','Vol','vol']))
                prev_c = safe_float(get_col(prev,   ['Close','close','CLOSE']))

                if prev_c == 0:
                    prev_c = close

                chg  = round(close - prev_c, 2)
                chgP = round((chg / prev_c * 100) if prev_c else 0, 2)

                # Get sector from quote if available
                sector = ""
                try:
                    q = psxdata.quote(sym)
                    if q is not None:
                        if hasattr(q, 'to_dict'):
                            q = q.to_dict()
                        sector = str(q.get("sector") or q.get("company") or q.get("name") or "")
                except:
                    pass

                stocks.append({
                    "symbol":   sym,
                    "close":    close,
                    "open":     open_,
                    "high":     high,
                    "low":      low,
                    "volume":   vol,
                    "change":   chg,
                    "change_p": chgP,
                    "sector":   sector,
                })
                print("  " + sym + ": PKR " + str(close) + " | O:" + str(open_) + " H:" + str(high) + " L:" + str(low) + " V:" + str(vol) + " Chg:" + str(chg))
            else:
                print("  " + sym + ": no EOD data")
            time.sleep(0.25)
        except Exception as e:
            print("  " + sym + ": " + str(e))

    # STEP 3: Fetch indices
    print("Fetching indices...")
    index_list = [
        ("KSE100", "KSE100"),
        ("KSE30",  "KSE30"),
        ("ALLSHR", "ALLSHR"),
        ("KMI30",  "KMI30"),
    ]
    for idx_key, idx_name in index_list:
        try:
            df = psxdata.indices(idx_key, start=str(start_date), end=str(end_date))
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                prev   = df.iloc[-2] if len(df) > 1 else latest

                def get_col(row, names):
                    for n in names:
                        if n in row.index and row[n] is not None:
                            v = row[n]
                            if str(v) not in ['nan','None','']:
                                return v
                    return 0

                val    = safe_float(get_col(latest, ['Close','close','Value','value']))
                prev_v = safe_float(get_col(prev,   ['Close','close','Value','value']))
                if prev_v == 0:
                    prev_v = val
                chg    = round(val - prev_v, 2)
                chgP   = round((chg / prev_v * 100) if prev_v else 0, 2)
                indices.append({
                    "name":     idx_name,
                    "value":    val,
                    "change":   chg,
                    "change_p": chgP,
                })
                print("  " + idx_name + ": " + str(val) + " (" + str(chg) + ")")
        except Exception as e:
            print("  " + idx_key + ": " + str(e))

    # STEP 4: Save
    output = {
        "updated_at": now_utc.isoformat() + "Z",
        "updated_pk": now_pk.strftime("%d %b %Y %I:%M %p PKT"),
        "stocks":     stocks,
        "indices":    indices,
        "count":      len(stocks),
        "source":     "psxdata"
    }

    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w") as f:
        json.dump(output, f)

    print("=== Saved " + str(len(stocks)) + " stocks, " + str(len(indices)) + " indices ===")

if __name__ == "__main__":
    main()
