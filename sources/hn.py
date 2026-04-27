import urllib.request
import json
from datetime import datetime, timedelta
from config import LOOKBACK_DAYS

HN_BASE = "https://hn.algolia.com/api/v1/"

def fetch_hn(topic, days=None):
    days = days or LOOKBACK_DAYS
    ts = int((datetime.utcnow() - timedelta(days=days)).timestamp())
    articles = []
    try:
        url = (
            f"{HN_BASE}search?query={urllib.parse.quote(topic)}"
            f"&tags=story&numericFilters=created_at_i>{ts}"
            f"&hitsPerPage=30&attributesToRetrieve=title,url,author,points,num_comments,created_at"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for hit in data.get("hits", []):
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            articles.append({
                "title": hit.get("title", ""),
                "url": url,
                "summary": "",
                "author": hit.get("author", "unknown"),
                "published_at": hit.get("created_at", "")[:10],
                "source": "HackerNews",
                "topic": topic,
                "score": (hit.get("points") or 0) + (hit.get("num_comments") or 0),
            })
    except Exception as e:
        print(f"  [hn] error: {e}")
    return articles

import urllib.parse