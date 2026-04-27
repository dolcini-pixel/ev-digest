import urllib.request
import json
from config import LOOKBACK_DAYS

SUBREDDITS = ["electricvehicles", "teslamotors", "RealTesla"]

def fetch_reddit(topic=None, days=None):
    articles = []
    kw = (topic or "electric vehicle").replace("-", "+")
    for sub in SUBREDDITS:
        try:
            url = (
                f"https://www.reddit.com/r/{sub}/hot/.json?limit=20"
                f"&t=week&restrict_type=1"
            )
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                p = post.get("data", {})
                title = p.get("title", "")
                url = p.get("url", "")
                if not url or url == p.get("permalink", ""):
                    url = f"https://reddit.com{p.get('permalink','')}"
                articles.append({
                    "title": title,
                    "url": url,
                    "summary": p.get("selftext", "")[:300],
                    "author": p.get("author", "unknown"),
                    "published_at": "",
                    "source": f"Reddit/{sub}",
                    "topic": topic or "general",
                    "score": p.get("score", 0) or 0,
                })
        except Exception as e:
            print(f"  [reddit:{sub}] error: {e}")
    return articles