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
    "SNBL.KA","BIPL.KA","HMBL.KA","GHGL.KA","BYCO.KA","NRL.KA",
    "KAPCO.KA","FHAM.KA","TELE.KA","WTL.KA","INIL.KA","HASCOL.KA"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def fetch_yahoo(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        result = data["chart"]["result"]
        if not result:
            return None
        meta  = result[0]["meta"]
        close = float(meta.get("regularMarketPrice", 0))
        prev  = float(meta.get("chartPreviousClose", close))
        chg   = round(close - prev, 2)
        chgP  = round((chg / prev * 100) if prev else 0, 2)
        sym   = symbol.replace(".KA", "")
        return {
            "symbol":   sym,
            "close":    close,
            "open":     float(meta.get("regularMarketOpen", 0)),
            "high":     float(meta.get("regularMarketDayHigh", 0)),
            "low":      float(meta.get("regularMarketDayLow", 0)),
            "volume":   int(meta.get("regularMarketVolume",
