import urllib.request
import re
import feedparser
from datetime import datetime, timedelta
from config import RSS_FEEDS, LOOKBACK_DAYS

def fetch_all_feeds(topic, days=None):
    days = days or LOOKBACK_DAYS
    cutoff = datetime.utcnow() - timedelta(days=days)
    all_articles = []
    for name, feed_url in RSS_FEEDS.items():
        articles = _fetch_single_feed(feed_url, topic, name, cutoff)
        all_articles.extend(articles)
    return all_articles

def _fetch_single_feed(feed_url, topic, source_name, cutoff):
    articles = []
    kw = topic.replace("-", " ").lower()
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            pub_str = _parse_date(entry)
            if pub_str and _is_recent(pub_str, cutoff):
                title = entry.get("title", "Untitled")
                if kw not in title.lower() and kw not in (entry.get("summary", "") + entry.get("description", "")).lower():
                    continue
                summary = _clean_summary(entry)
                articles.append({
                    "title": title,
                    "url": entry.get("link") or entry.get("id", ""),
                    "summary": summary[:500],
                    "author": _get_author(entry),
                    "published_at": pub_str[:10],
                    "source": source_name.capitalize(),
                    "topic": topic,
                    "score": 0,
                })
    except Exception as e:
        print(f"  [rss:{source_name}] error: {e}")
    return articles

def _parse_date(entry):
    for field in ["published_parsed", "updated_parsed", "created_parsed"]:
        if hasattr(entry, field) and getattr(entry, field):
            import time
            return time.strftime("%Y-%m-%d", getattr(entry, field))
    for date_field in ["published", "updated", "created"]:
        d = entry.get(date_field, "")
        if d:
            return d[:10]
    return ""

def _is_recent(date_str, cutoff):
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d") >= cutoff
    except Exception:
        return False

def _clean_summary(entry):
    raw = entry.get("summary") or entry.get("description") or ""
    raw = re.sub(r'<[^>]+>', '', raw)
    raw = raw.replace("\n", " ").replace("  ", " ")
    return raw.strip()

def _get_author(entry):
    if hasattr(entry, "author"):
        return entry.author
    if hasattr(entry, "authors") and entry.authors:
        return entry.authors[0].get("name", "unknown")
    return "unknown"