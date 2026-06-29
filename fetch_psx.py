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

def get_col(row, names):
    for n in names:
        if n in row.index and row[n] is not None:
            v = row[n]
            if str(v) not in ['nan', 'None', '']:
                return v
    return 0

# Hardcoded PSX equity symbols only
SYMBOLS = [
    "HBL","UBL","MCB","NBP","ENGRO","OGDC","PPL","PSO","LUCK","MLCF",
    "HUBC","SSGC","SNGP","KEL","TRG","SEARL","EFERT","FFC","FATIMA","DGKC",
    "PIOC","KOHC","CHCC","BAFL","MEBL","FABL","AKBL","BAHL","PAKT","AGTL",
    "HCAR","INDU","NCPL","APL","SHEL","ATRL","MARI","POL","LOTCHEM","EPCL",
    "FFBL","NETSOL","SYS","PTCL","MUGHAL","ISL","ASTL","UNITY","COLG","NESTLE",
    "ICI","AVN","KAPCO","INIL","JSBL","SNBL","BIPL","GHGL","NRL","TELE",
    "WTL","HASCOL","DAWH","SILK","HMBL","PSMC","BYCO","NRL","FHAM","INIL",
    "MLCF","GWLC","JLICL","PKGS","TRIPF","GHNL","SIEM","HGFA","FCEPL","CEPB",
    "PNSC","SRVI","BWCL","ANL","AMTEX","CRTM","GATM","GTYR","HINO","OTSU"
]

# Remove duplicates
SYMBOLS = list(dict.fromkeys(SYMBOLS))

def main():
    now_utc = datetime.datetime.utcnow()
    now_pk  = now_utc + datetime.timedelta(hours=5)
    print("=== PSX Fetch started: " + str(now_utc) + " UTC ===")
    print("Fetching " + str(len(SYMBOLS)) + " symbols...")

    end_date   = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=10)

    stocks  = []
    indices = []

    # STEP 1: Fetch EOD data per symbol
    for sym in SYMBOLS:
        try:
            df = psxdata.stocks(sym, start=str(start_date), end=str(end_date))
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                prev   = df.iloc[-2] if len(df) > 1 else latest

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

                stocks.append({
                    "symbol":   sym,
                    "close":    close,
                    "open":     open_,
                    "high":     high,
                    "low":      low,
                    "volume":   vol,
                    "change":   chg,
                    "change_p": chgP,
                    "sector":   "",
                })
                print("  " + sym + ": PKR " + str(close) + " O:" + str(open_) + " H:" + str(high) + " L:" + str(low) + " V:" + str(vol) + " Chg:" + str(chg))
            else:
                print("  " + sym + ": no data")
            time.sleep(0.2)
        except Exception as e:
            print("  " + sym + ": " + str(e))

    # STEP 2: Fetch indices
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
                val    = safe_float(get_col(latest, ['Close','close','Value','value','INDEX']))
                prev_v = safe_float(get_col(prev,   ['Close','close','Value','value','INDEX']))
                if prev_v == 0:
                    prev_v = val
                chg  = round(val - prev_v, 2)
                chgP = round((chg / prev_v * 100) if prev_v else 0, 2)
                indices.append({
                    "name":     idx_name,
                    "value":    val,
                    "change":   chg,
                    "change_p": chgP,
                })
                print("  " + idx_name + ": " + str(val) + " chg:" + str(chg))
            else:
                print("  " + idx_key + ": no data")
        except Exception as e:
            print("  " + idx_key + ": " + str(e))

    # STEP 3: Save
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
