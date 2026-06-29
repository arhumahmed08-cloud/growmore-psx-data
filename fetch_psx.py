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

SYMBOLS = [
    "HBL","UBL","MCB","NBP","ENGRO","OGDC","PPL","PSO","LUCK","MLCF",
    "HUBC","SSGC","SNGP","KEL","TRG","SEARL","EFERT","FFC","FATIMA","DGKC",
    "PIOC","KOHC","CHCC","BAFL","MEBL","FABL","AKBL","BAHL","PAKT","AGTL",
    "HCAR","INDU","NCPL","APL","SHEL","ATRL","MARI","POL","LOTCHEM","EPCL",
    "FFBL","NETSOL","SYS","PTCL","MUGHAL","ISL","ASTL","UNITY","COLG","NESTLE",
    "ICI","AVN","KAPCO","INIL","JSBL","SNBL","BIPL","GHGL","NRL","TELE",
    "WTL","HASCOL","DAWH","SILK","HMBL","PSMC","FHAM","GWLC","JLICL","PKGS",
    "TRIPF","SIEM","HGFA","FCEPL","CEPB","PNSC","SRVI","BWCL","ANL","AMTEX",
    "CRTM","GATM","GTYR","HINO","OTSU","ENGRO","MLCF","INIL"
]

SYMBOLS = list(dict.fromkeys(SYMBOLS))

# Sector mapping
SECTORS = {
    "HBL":"Commercial Banks","UBL":"Commercial Banks","MCB":"Commercial Banks",
    "NBP":"Commercial Banks","BAFL":"Commercial Banks","MEBL":"Commercial Banks",
    "FABL":"Commercial Banks","AKBL":"Commercial Banks","BAHL":"Commercial Banks",
    "JSBL":"Commercial Banks","SNBL":"Commercial Banks","BIPL":"Commercial Banks",
    "HMBL":"Commercial Banks","ENGRO":"Fertilizer","EFERT":"Fertilizer",
    "FFC":"Fertilizer","FATIMA":"Fertilizer","FFBL":"Fertilizer",
    "OGDC":"Oil & Gas","PPL":"Oil & Gas","PSO":"Oil & Gas","APL":"Oil & Gas",
    "SHEL":"Oil & Gas","ATRL":"Oil & Gas","MARI":"Oil & Gas","POL":"Oil & Gas",
    "NRL":"Oil & Gas","HASCOL":"Oil & Gas","SSGC":"Gas & Fuel","SNGP":"Gas & Fuel",
    "KEL":"Power","HUBC":"Power","KAPCO":"Power","NCPL":"Power",
    "LUCK":"Cement","MLCF":"Cement","DGKC":"Cement","PIOC":"Cement",
    "KOHC":"Cement","CHCC":"Cement","BWCL":"Cement",
    "TRG":"Technology","NETSOL":"Technology","SYS":"Technology",
    "PTCL":"Telecom","TELE":"Telecom","WTL":"Telecom",
    "PAKT":"Tobacco","COLG":"Personal Care","NESTLE":"Food & Beverages",
    "SEARL":"Pharma","ICI":"Chemicals","EPCL":"Chemicals","LOTCHEM":"Chemicals",
    "HCAR":"Automobiles","INDU":"Automobiles","AGTL":"Automobiles",
    "PSMC":"Automobiles","HINO":"Automobiles","OTSU":"Automobiles",
    "MUGHAL":"Steel","ISL":"Steel","ASTL":"Steel",
    "UNITY":"Sugar","FHAM":"Sugar",
    "AVN":"Insurance","JLICL":"Insurance",
    "PNSC":"Transport","SRVI":"Transport",
    "PKGS":"Paper & Board","AMTEX":"Textile","ANL":"Textile",
    "GWLC":"Glass","SIEM":"Engineering","GHGL":"Glass",
    "CRTM":"Ceramics","GATM":"General Industry","GTYR":"Tyres",
    "HGFA":"General Industry","FCEPL":"Chemicals","CEPB":"Chemicals",
    "DAWH":"General Industry","SILK":"Textile","BIPL":"Commercial Banks",
    "INIL":"General Industry","TRIPF":"Finance"
}

def main():
    now_utc = datetime.datetime.utcnow()
    now_pk  = now_utc + datetime.timedelta(hours=5)
    print("=== PSX Fetch started: " + str(now_utc) + " UTC ===")

    end_date   = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=10)

    stocks  = []
    indices = []

    # STEP 1: Fetch EOD stock data
    print("Fetching " + str(len(SYMBOLS)) + " stocks...")
    for sym in SYMBOLS:
        try:
            df = psxdata.stocks(sym, start=str(start_date), end=str(end_date))
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                prev   = df.iloc[-2] if len(df) > 1 else latest

                close  = safe_float(get_col(latest, ['Close','close','CLOSE']))
                open_  = safe_float(get_col(latest, ['Open','open','OPEN']))
                high   = safe_float(get_col(latest, ['High','high','HIGH']))
                low    = safe_float(get_col(latest, ['Low','low','LOW']))
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
                    "sector":   SECTORS.get(sym, ""),
                })
                print("  " + sym + ": " + str(close) + " chg:" + str(chg))
            else:
                print("  " + sym + ": no data")
            time.sleep(0.2)
        except Exception as e:
            print("  " + sym + ": " + str(e))

    # STEP 2: Fetch indices using psxdata.index() single method
    print("Fetching indices...")
    index_list = [
        ("KSE100","KSE100"),
        ("KSE30","KSE30"),
        ("ALLSHR","ALLSHR"),
        ("KMI30","KMI30"),
    ]
    for idx_key, idx_name in index_list:
        fetched = False
        # Try method 1: psxdata.indices()
        try:
            df = psxdata.indices(idx_key, start=str(start_date), end=str(end_date))
            if df is not None and not df.empty:
                print("  " + idx_key + " columns: " + str(list(df.columns)))
                latest = df.iloc[-1]
                prev   = df.iloc[-2] if len(df) > 1 else latest
                # Try all possible column names
                val    = safe_float(get_col(latest, ['Close','close','Value','value','INDEX','index','Last','last']))
                prev_v = safe_float(get_col(prev,   ['Close','close','Value','value','INDEX','index','Last','last']))
                if val == 0:
                    # Try first numeric column
                    for col in df.columns:
                        try:
                            val = safe_float(latest[col])
                            prev_v = safe_float(prev[col])
                            if val > 0:
                                break
                        except:
                            pass
                if prev_v == 0:
                    prev_v = val
                chg  = round(val - prev_v, 2)
                chgP = round((chg / prev_v * 100) if prev_v else 0, 2)
                indices.append({"name": idx_name, "value": val, "change": chg, "change_p": chgP})
                print("  " + idx_name + ": " + str(val))
                fetched = True
        except Exception as e:
            print("  " + idx_key + " indices() failed: " + str(e))

        # Try method 2: psxdata.index() singular
        if not fetched:
            try:
                df = psxdata.index(idx_key, start=str(start_date), end=str(end_date))
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    prev   = df.iloc[-2] if len(df) > 1 else latest
                    val    = safe_float(get_col(latest, ['Close','close','Value','value']))
                    prev_v = safe_float(get_col(prev,   ['Close','close','Value','value']))
                    if prev_v == 0:
                        prev_v = val
                    chg  = round(val - prev_v, 2)
                    chgP = round((chg / prev_v * 100) if prev_v else 0, 2)
                    indices.append({"name": idx_name, "value": val, "change": chg, "change_p": chgP})
                    print("  " + idx_name + ": " + str(val))
                    fetched = True
            except Exception as e:
                print("  " + idx_key + " index() failed: " + str(e))

        if not fetched:
            print("  " + idx_key + ": all methods failed")

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
