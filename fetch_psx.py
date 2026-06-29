import json, datetime, os, time

def main():
    print(f"=== PSX Fetch started: {datetime.datetime.utcnow()} UTC ===")
    
    stocks = []
    indices = []
    
    # Method 1: psx-data-reader library
    try:
        from psx import stocks as psx_stocks, index
        print("Trying psx-data-reader...")
        
        end   = datetime.date.today()
        start = end - datetime.timedelta(days=5)
        
        SYMBOLS = [
            "HBL","UBL","MCB","NBP","ENGRO","OGDC","PPL","PSO","LUCK","MLCF",
            "HUBC","KAPCO","SSGC","SNGP","KEL","UNITY","TRG","AVN","SEARL","COLG",
            "NESTLE","ICI","EFERT","FFC","FATIMA","DGKC","PIOC","KOHC","CHCC","BAFL",
            "MEBL","FABL","AKBL","BAHL","PAKT","AGTL","HCAR","INDU","NCPL","HASCOL",
            "APL","SHEL","ATRL","DAWH","SILK","JSBL","SNBL","BIPL","HMBL","MARI",
            "POL","BYCO","NRL","PRL","PSMC","GHGL","LOTCHEM","EPCL","FFBL","NETSOL",
            "SYS","TPS","TPLP","PTCL","WTL","MUGHAL","ISL","ASTL","INIL","FHAM"
        ]
        
        for sym in SYMBOLS:
            try:
                df = psx_stocks(sym, start=start, end=end)
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    prev   = df.iloc[-2] if len(df) > 1 else latest
                    close  = float(latest.get('Close', latest.get('close', 0)))
                    prev_c = float(prev.get('Close',   prev.get('close',   close)))
                    chg    = round(close - prev_c, 2)
                    chgP   = round((chg / prev_c * 100) if prev_c else 0, 2)
                    stocks.append({
                        "symbol":   sym,
                        "close":    close,
                        "open":     float(latest.get('Open',   latest.get('open',   0))),
                        "high":     float(latest.get('High',   latest.get('high',   0))),
                        "low":      float(latest.get('Low',    latest.get('low',    0))),
                        "volume":   int(latest.get('Volume', latest.get('volume', 0))),
                        "change":   chg,
                        "change_p": chgP,
                    })
                    print(f"  {sym}: PKR {close} ({chg:+.2f})")
                time.sleep(0.2)
            except Exception as e:
                print(f"  {sym}: {e}")
        
        # Fetch KSE-100 index
        try:
            idx_df = index("KSE100", start=start, end=end)
            if idx_df is not None and not idx_df.empty:
                latest = idx_df.iloc[-1]
                prev   = idx_df.iloc[-2] if len(idx_df) > 1 else latest
                val    = float(latest.get('Close', 0))
                prev_v = float(prev.get('Close', val))
                chg    = round(val - prev_v, 2)
                indices.append({
                    "name": "KSE100", "value": val,
                    "change": chg,
                    "change_p": round((chg/prev_v*100) if prev_v else 0, 2)
                })
                print(f"  KSE-100: {val}")
        except Exception as e:
            print(f"  KSE-100 index: {e}")
            
    except ImportError:
        print("psx-data-reader not available")
    
    # Method 2: mstock fallback
    if not stocks:
        try:
            import mstock
            print("Trying mstock...")
            data = mstock.get_market_summary()
            if data:
                stocks = data
                print(f"Got {len(stocks)} from mstock")
        except Exception as e:
            print(f"mstock failed: {e}")

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

    print(f"=== Saved {len(stocks)} stocks ===")

if __name__ == "__main__":
    main()
