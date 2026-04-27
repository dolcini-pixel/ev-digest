import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
from config import LOOKBACK_DAYS

LOB_BASE = "https://lobste.rs/api/v1/search_by_date?"

def fetch_lobsters(topic, days=None):
    days = days or LOOKBACK_DAYS
    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    articles = []
    try:
        q = topic.replace("-", "+")
        url = (
            f"{LOB_BASE}?q={urllib.parse.quote(q)}"
            f"&page=1&per_page=30"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        stories = data if isinstance(data, list) else data.get("stories", data.get("results", []))
        for story in stories:
            articles.append({
                "title": story.get("title", ""),
                "url": story.get("url", f"https://lobste.rs/s/{story.get('short_id')}"),
                "summary": story.get("description_plain", "")[:300],
                "author": story.get("submitter_user", {}).get("username", "unknown"),
                "published_at": story.get("created_at", "")[:10],
                "source": "Lobsters",
                "topic": topic,
                "score": story.get("score", 0),
            })
    except Exception as e:
        print(f"  [lobsters] error: {e}")
    return articles

import urllib.parse