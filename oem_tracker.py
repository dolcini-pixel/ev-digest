import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import db as _db
import sources.ev_database as evdb

def update_oem_tracker():
    conn = _db.get_db()
    prev = _db.get_oem_prev(conn)
    prev_keys = set(prev.keys())

    rows = evdb.fetch_ev_db()
    n_updated = 0
    for row in rows:
        _db.upsert_oem(conn, row)
        key = f"{row['oem']}|{row['model']}"
        if key in prev_keys:
            if _changed(prev[key], row):
                n_updated += 1
        else:
            n_updated += 1

    # Current state
    cur = conn.cursor()
    cur.execute("SELECT * FROM oem_tech ORDER BY oem, model")
    current = [dict(r) for r in cur.fetchall()]

    # Diff
    diff = []
    for key, prev_row in prev.items():
        cur_row = next((r for r in current if f"{r['oem']}|{r['model']}" == key), None)
        if cur_row and _changed(prev_row, cur_row):
            diff.append({"before": prev_row, "after": cur_row})

    conn.close()
    return {"current": current, "diff": diff, "n_updated": n_updated}

def _changed(before, after):
    return any(
        before.get(k) != after.get(k)
        for k in ["battery_chem", "v2g", "plug_charge", "max_dc_kw", "range_km", "notable_tech"]
    )

if __name__ == "__main__":
    result = update_oem_tracker()
    print(f"OEM tracker: {result['n_updated']} rows updated, {len(result['diff'])} changes")