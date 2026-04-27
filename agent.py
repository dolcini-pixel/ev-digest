import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))
import config
import db as _db
import sources.arxiv as arxiv_src
import sources.hn as hn_src
import sources.lobsters as lob_src
import sources.rss_utils as rss_src
import sources.ev_database as evdb_src
import sources.reddit as reddit_src
import clustering
import synthesis
import oem_tracker
import render
import deploy

def run_digest():
    week_ending = datetime.utcnow().strftime("%Y-%m-%d")
    print(f"[agent] Starting EV digest for week ending {week_ending}")

    # Init DB
    _db.init_db()
    conn = _db.get_db()

    # 1. Fetch all sources for all topics
    all_articles = []
    seen_urls = set()
    for topic in config.BASE_TOPICS:
        print(f"[agent] Fetching: {topic}")
        # arXiv
        for a in arxiv_src.fetch_arxiv(topic):
            if a["url"] and a["url"] not in seen_urls:
                seen_urls.add(a["url"])
                all_articles.append(a)
                _db.upsert_article(conn, a)
        # HN
        for a in hn_src.fetch_hn(topic):
            if a["url"] and a["url"] not in seen_urls:
                seen_urls.add(a["url"])
                all_articles.append(a)
                _db.upsert_article(conn, a)
                _db.upsert_contributor(conn, a["author"], "HackerNews", a.get("score", 0))
        # Lobsters
        for a in lob_src.fetch_lobsters(topic):
            if a["url"] and a["url"] not in seen_urls:
                seen_urls.add(a["url"])
                all_articles.append(a)
                _db.upsert_article(conn, a)
        # RSS feeds
        for a in rss_src.fetch_all_feeds(topic):
            if a["url"] and a["url"] not in seen_urls:
                seen_urls.add(a["url"])
                all_articles.append(a)
                _db.upsert_article(conn, a)
        # Reddit
        for a in reddit_src.fetch_reddit(topic):
            if a["url"] and a["url"] not in seen_urls:
                seen_urls.add(a["url"])
                all_articles.append(a)
                _db.upsert_article(conn, a)

    print(f"[agent] {len(all_articles)} unique articles collected")

    # 2. Cluster
    clustered = clustering.cluster_articles(all_articles, n_topics=len(config.BASE_TOPICS))
    grouped = clustering.group_by_cluster(clustered)

    # 3. Synthesize per cluster
    syntheses = synthesis.synthesize_all(grouped)
    print(f"[agent] {len(syntheses)} clusters synthesized")

    # 4. OEM tracker
    oem_result = oem_tracker.update_oem_tracker()
    print(f"[agent] OEM: {oem_result['n_updated']} updated, {len(oem_result['diff'])} changes")

    # 5. Render
    html = render.render_digest(syntheses, oem_result, week_ending)
    html_file = f"digest_{week_ending}.html"

    # 6. Deploy
    deploy.deploy(html, week_ending)

    # 7. Record
    _db.record_run(conn, len(all_articles), len(grouped), oem_result["n_updated"], html_file)
    _db.record_digest(conn, week_ending, html_file)
    conn.close()

    print(f"[agent] Digest complete — {len(all_articles)} articles, {len(syntheses)} topics")
    return html

if __name__ == "__main__":
    run_digest()