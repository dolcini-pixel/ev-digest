import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html as html_mod
from datetime import datetime, timedelta
from config import ARXIV_KEYWORDS, LOOKBACK_DAYS

ARXIV_BASE = "https://export.arxiv.org/api/query?"

def fetch_arxiv(topic, days=None):
    days = days or LOOKBACK_DAYS
    keywords = ARXIV_KEYWORDS.get(topic, [topic.replace("-", " ")])
    query_parts = [f'all:{kw}' for kw in keywords]
    query = "+OR+".join(query_parts)
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y%m%d%H%M")
    url = (
        f"{ARXIV_BASE}search_query={query}&start=0&max_results=30"
        f"&sortBy=submittedDate&sortOrder=descending"
    )
    articles = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
        root = ET.fromstring(data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            published_el = entry.find("atom:published", ns)
            author_els = entry.findall("atom:author/atom:name", ns)
            link_el = entry.find("atom:id", ns)
            authors = [a.text or "" for a in author_els]
            title = title_el.text.strip().replace("\n", " ") if title_el is not None else "Untitled"
            summary = summary_el.text.strip() if summary_el is not None else ""
            summary = html_mod.strip_tags(summary)[:500]
            published = published_el.text[:10] if published_el is not None else ""
            url = link_el.text if link_el is not None else ""
            if url and "arxiv.org/abs/" in url:
                url = url.replace("/abs/", "/v1/")
            articles.append({
                "title": title,
                "url": url or f"https://arxiv.org/abs/{entry.find('atom:id', ns).text.split('/')[-1]}",
                "summary": summary,
                "author": "; ".join(authors[:3]),
                "published_at": published,
                "source": "arXiv",
                "topic": topic,
                "score": 0,
            })
    except Exception as e:
        print(f"  [arxiv] error: {e}")
    return articles