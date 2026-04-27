import sqlite3
import os
from config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE, title TEXT, source TEXT, author TEXT,
            published_at TEXT, summary TEXT, topic TEXT, cluster_id INTEGER,
            engagement_score INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS digests (
            id INTEGER PRIMARY KEY,
            week_ending TEXT, html_file TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS oem_tech (
            id INTEGER PRIMARY KEY,
            oem TEXT, model TEXT,
            battery_chem TEXT, v2g INTEGER DEFAULT 0, plug_charge INTEGER DEFAULT 0,
            max_dc_kw REAL, range_km REAL, notable_tech TEXT, updated_at TEXT,
            UNIQUE(oem, model)
        );
        CREATE TABLE IF NOT EXISTS contributors (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE, source TEXT, score INTEGER DEFAULT 0, last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY,
            run_date TEXT, articles_fetched INTEGER, clusters_formed INTEGER,
            oem_updated INTEGER, deployed_at TEXT
        );
    """)
    conn.commit()
    return conn

def upsert_article(conn, article):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO articles (url, title, source, author, published_at, summary, topic, engagement_score)
        VALUES (:url, :title, :source, :author, :published_at, :summary, :topic, :score)
        ON CONFLICT(url) DO UPDATE SET
            engagement_score = MAX(articles.engagement_score, :score)
    """, article)
    conn.commit()

def upsert_oem(conn, row):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO oem_tech (oem, model, battery_chem, v2g, plug_charge, max_dc_kw, range_km, notable_tech, updated_at)
        VALUES (:oem, :model, :battery_chem, :v2g, :plug_charge, :max_dc_kw, :range_km, :notable_tech, :updated_at)
        ON CONFLICT(oem, model) DO UPDATE SET
            battery_chem = :battery_chem,
            v2g = :v2g,
            plug_charge = :plug_charge,
            max_dc_kw = :max_dc_kw,
            range_km = :range_km,
            notable_tech = :notable_tech,
            updated_at = :updated_at
    """, row)
    conn.commit()

def get_oem_prev(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM oem_tech")
    return {f"{r['oem']}|{r['model']}": dict(r) for r in cur.fetchall()}

def upsert_contributor(conn, name, source, score):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO contributors (name, source, score, last_seen)
        VALUES (:name, :source, :score, datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            score = MAX(contributors.score, :score),
            last_seen = datetime('now')
    """, {"name": name, "source": source, "score": score})
    conn.commit()

def record_run(conn, n_articles, n_clusters, n_oem, html_file):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO runs (run_date, articles_fetched, clusters_formed, oem_updated, deployed_at)
        VALUES (datetime('now'), :a, :c, :o, :f)
    """, {"a": n_articles, "c": n_clusters, "o": n_oem, "f": html_file})
    conn.commit()

def record_digest(conn, week_ending, html_file):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO digests (week_ending, html_file, created_at)
        VALUES (:w, :f, datetime('now'))
    """, {"w": week_ending, "f": html_file})
    conn.commit()