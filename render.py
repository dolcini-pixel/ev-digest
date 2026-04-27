from datetime import datetime

COLORS = {
    "bg": "#0d1117",
    "surface": "#161b22",
    "border": "#30363d",
    "text": "#e6edf3",
    "muted": "#8b949e",
    "accent": "#58a6ff",
    "green": "#3fb950",
    "yellow": "#d29922",
    "red": "#f85149",
    "tag_bg": "#1f6feb",
}

def render_digest(syntheses, oem_result, week_ending=None):
    week_ending = week_ending or datetime.utcnow().strftime("%Y-%m-%d")
    n_articles = sum(len(v.get("sources", [])) for v in syntheses.values())

    html = _header(week_ending, n_articles, len(syntheses))
    html += _topics_section(syntheses)
    html += _oem_section(oem_result)
    html += _footer()
    return html

def _header(week_ending, n_articles, n_topics):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EV Digest — Week of {week_ending}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: {COLORS['bg']}; color: {COLORS['text']}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }}
  header {{ margin-bottom: 2.5rem; }}
  h1 {{ font-size: 1.8rem; font-weight: 700; color: {COLORS['accent']}; }}
  .meta {{ color: {COLORS['muted']}; font-size: 0.9rem; margin-top: 0.3rem; }}
  .tag {{
    display: inline-block;
    background: {COLORS['tag_bg']};
    color: white;
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
  }}
  .topic-card {{ background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  .topic-card h2 {{ font-size: 1.15rem; color: {COLORS['accent']}; margin-bottom: 0.7rem; }}
  .topic-card p {{ color: {COLORS['text']}; margin-bottom: 1rem; }}
  .so-what {{
    background: {COLORS['bg']};
    border-left: 3px solid {COLORS['yellow']};
    padding: 0.6rem 1rem;
    margin-bottom: 1rem;
    color: {COLORS['yellow']};
    font-size: 0.9rem;
  }}
  .so-what span {{ font-weight: 600; margin-right: 0.4rem; }}
  .badge {{ display: inline-block; font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 3px; margin-right: 0.3rem; }}
  .badge-lab {{ background: {COLORS['red']}; color: white; }}
  .badge-prod {{ background: {COLORS['green']}; color: white; }}
  .badge-early {{ background: {COLORS['yellow']}; color: black; }}
  .sources {{ list-style: none; }}
  .sources li {{ margin-bottom: 0.5rem; }}
  .sources a {{ color: {COLORS['accent']}; text-decoration: none; font-size: 0.88rem; }}
  .sources a:hover {{ text-decoration: underline; }}
  .sources .src-meta {{ color: {COLORS['muted']}; font-size: 0.78rem; margin-left: 0.4rem; }}
  h3 {{ font-size: 1rem; color: {COLORS['text']}; margin: 2rem 0 1rem; border-bottom: 1px solid {COLORS['border']}; padding-bottom: 0.4rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ text-align: left; color: {COLORS['muted']}; padding: 0.5rem 0.7rem; border-bottom: 1px solid {COLORS['border']}; }}
  td {{ padding: 0.5rem 0.7rem; border-bottom: 1px solid {COLORS['border']}; color: {COLORS['text']}; }}
  tr:hover td {{ background: {COLORS['surface']}; }}
  .oem-badge {{
    display: inline-block; padding: 0.1rem 0.4rem; border-radius: 3px;
    font-size: 0.7rem; font-weight: 600;
  }}
  .yes {{ background: {COLORS['green']}; color: white; }}
  .no {{ background: {COLORS['muted']}; color: white; }}
  .changed {{ color: {COLORS['yellow']}; font-size: 0.8rem; }}
  .no-changes {{ color: {COLORS['muted']}; font-style: italic; }}
  footer {{ margin-top: 3rem; text-align: center; color: {COLORS['muted']}; font-size: 0.8rem; }}
</style>
</head>
<body>
<div class="container">
<header>
  <h1>EV Weekly Digest</h1>
  <div class="meta">Week ending {week_ending} &middot; {n_articles} articles &middot; {n_topics} topics &middot; Auto-generated</div>
</header>
"""

def _topics_section(syntheses):
    html = ""
    topic_display = {
        "plug-and-charge": "Plug & Charge (ISO 15118)",
        "v2g-reversible-charge": "Vehicle-to-Grid (V2G) & Reversible Charging",
        "battery-technology": "Battery Technology",
    }
    for label, data in syntheses.items():
        display = topic_display.get(label, label.replace("-", " ").title())
        badge_class = _badge_class(data.get("lab_vs_production", ""))
        badge_text = _badge_text(data.get("lab_vs_production", ""))
        html += f'<div class="topic-card">\n'
        html += f'  <h2>{display}</h2>\n'
        html += f'  <span class="badge {badge_class}">{badge_text}</span>\n'
        html += f'  <p>{data.get("synthesis", "No synthesis available.")}</p>\n'
        html += f'  <div class="so-what"><span>So what:</span>{data.get("so_what", "")}</div>\n'
        html += '  <ul class="sources">\n'
        for src in data.get("sources", [])[:3]:
            html += (
                f'    <li>'
                f'<a href="{src.get("url","#")}" target="_blank" rel="noopener">{src.get("title","Source")}</a>'
                f'<span class="src-meta">({src.get("source","")})</span>'
                f'</li>\n'
            )
        html += '  </ul>\n'
        html += '</div>\n'
    return html

def _oem_section(oem_result):
    html = '<h3>OEM Technology Tracker</h3>\n'
    diff = oem_result.get("diff", [])
    if diff:
        html += f'<p class="changed">🔄 {len(diff)} change(s) since last run</p>\n'
        html += '<table><tr><th>OEM</th><th>Model</th><th>Battery</th><th>V2G</th><th>PnC</th><th>DC kW</th><th>Range km</th><th>Notable</th></tr>\n'
        for d in diff:
            b, a = d["before"], d["after"]
            changed_fields = [k for k in ["battery_chem","v2g","plug_charge","max_dc_kw","range_km"]
                           if b.get(k) != a.get(k)]
            html += f'<tr>'
            html += f'<td>{a.get("oem","")}</td>'
            html += f'<td>{a.get("model","")}</td>'
            html += f'<td class="{"changed" if "battery_chem" in changed_fields else ""}">{a.get("battery_chem","")}</td>'
            html += f'<td>{_yn(a.get("v2g"))}</td>'
            html += f'<td>{_yn(a.get("plug_charge"))}</td>'
            html += f'<td class="{"changed" if "max_dc_kw" in changed_fields else ""}">{a.get("max_dc_kw","")}</td>'
            html += f'<td class="{"changed" if "range_km" in changed_fields else ""}">{a.get("range_km","")}</td>'
            html += f'<td>{a.get("notable_tech","")[:60]}</td>'
            html += f'</tr>\n'
        html += '</table>\n'
    else:
        html += '<p class="no-changes">No changes since last run.</p>\n'

    current = oem_result.get("current", [])
    if current:
        html += (
            '<details style="margin-top:1rem;">'
            '<summary style="cursor:pointer;color:#8b949e;font-size:0.85rem;margin-bottom:0.5rem;">'
            f'Full OEM table ({len(current)} models) ▸'
            '</summary>\n'
            '<table style="margin-top:0.5rem;"><tr>'
            '<th>OEM</th><th>Model</th><th>Battery</th><th>V2G</th><th>PnC</th><th>DC kW</th><th>Range km</th><th>Updated</th>'
            '</tr>\n'
        )
        for row in current[:80]:
            html += '<tr>'
            html += f'<td>{row.get("oem","")}</td>'
            html += f'<td>{row.get("model","")[:40]}</td>'
            html += f'<td>{row.get("battery_chem","")}</td>'
            html += f'<td>{_yn(row.get("v2g"))}</td>'
            html += f'<td>{_yn(row.get("plug_charge"))}</td>'
            html += f'<td>{row.get("max_dc_kw","")}</td>'
            html += f'<td>{row.get("range_km","")}</td>'
            html += f'<td>{row.get("updated_at","")[:10]}</td>'
            html += '</tr>\n'
        html += '</table></details>\n'
    return html

def _footer():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""
<footer>
  Generated {now} by EV Digest Agent · dolcini-pixel/ev-digest
</footer>
</div>
</body>
</html>
"""

def _yn(v):
    return '<span class="oem-badge yes">Yes</span>' if v else '<span class="oem-badge no">—</span>'

def _badge_class(lvp):
    return {"lab": "badge badge-lab", "production": "badge badge-prod", "early_stages": "badge badge-early"}.get(
        lvp, "badge badge-early"
    )

def _badge_text(lvp):
    return {"lab": "Lab only", "production": "Production-ready", "early_stages": "Early stages"}.get(
        lvp, "Unknown"
    )