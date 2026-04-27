import urllib.request
import json
import re
from datetime import datetime
from config import OEM_BRANDS

EV_DB_BASE = "https://www.ev-database.org"

def fetch_ev_db(oem_filter=None):
    brands = [oem_filter] if oem_filter else OEM_BRANDS
    all_entries = []
    seen = set()
    for brand in brands:
        entries = _fetch_brand(brand)
        for e in entries:
            key = f"{e['oem']}|{e['model']}"
            if key not in seen:
                seen.add(key)
                all_entries.append(e)
    return all_entries

def _fetch_brand(brand):
    entries = []
    try:
        search_url = f"https://www.ev-database.org/?Search=Search&Brand={urllib.parse.quote(brand)}"
        req = urllib.request.Request(search_url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; EVdigest/1.0)",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        entries = _parse_ev_db_html(html, brand)
    except Exception as e:
        print(f"  [ev_database:{brand}] error: {e}")
        entries = _fallback_entries(brand)
    return entries

def _parse_ev_db_html(html, brand):
    entries = []
    # Look for car cards in the HTML - these typically contain model info
    # Pattern: data in structured divs or JSON blocks
    models = re.findall(r'data-model="([^"]+)"', html)
    if not models:
        # Try to extract from page title or links
        titles = re.findall(rf'class="[^"]*title[^"]*">([^<]+{re.escape(brand)}[^<]*)<', html, re.I)
        if not titles:
            titles = re.findall(r'href="/[^"]*/([^"]+)"[^>]*>\s*([^<]+\s*{re.escape(brand)}[^<]*)\s*<'.replace("{re.escape(brand)}", brand[:4]), html)
        for model in list(set(titles))[:10]:
            entries.append(_make_entry(brand, model.strip()))
    else:
        for model in models[:15]:
            entries.append(_make_entry(brand, model.strip()))
    return entries

def _make_entry(brand, model_name):
    clean_model = re.sub(r'\s+', ' ', model_name).strip()
    clean_model = clean_model[:80]
    # Heuristic battery chem detection from model name
    chem = "NMC"
    model_lower = model_name.lower()
    if any(x in model_lower for x in ["lfp", "blade", "byd"]):
        chem = "LFP"
    elif any(x in model_lower for x in ["solid-state", "ssb"]):
        chem = "Solid-state"
    # V2G rough heuristic
    v2g = 0
    if any(x in model_lower for x in ["id.", "iq3", "ix3", "eqs", "bz4x", "ioniq"]):
        v2g = 1
    return {
        "oem": brand,
        "model": clean_model,
        "battery_chem": chem,
        "v2g": v2g,
        "plug_charge": 1,
        "max_dc_kw": None,
        "range_km": None,
        "notable_tech": "",
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
    }

def _fallback_entries(brand):
    return [_make_entry(brand, f"{brand} EV (current)")]

import urllib.parse