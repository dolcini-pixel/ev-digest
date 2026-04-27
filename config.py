import os
from dotenv import load_dotenv

load_dotenv("/home/pdolcini/Python/serach_info/.env")

OPENROUTER_API_KEY = os.getenv("API_KEY", "").strip('" ')
GITHUB_REPO = "dolcini-pixel/ev-digest"
GITHUB_PAGES_BRANCH = "gh-pages"
GITHUB_PAGES_SOURCE = "docs"
LOOKBACK_DAYS = 7
DB_PATH = os.path.join(os.path.dirname(__file__), "ev_digest.db")

BASE_TOPICS = ["plug-and-charge", "v2g-reversible-charge", "battery-technology"]

RSS_FEEDS = {
    "electrek": "https://electrek.co/feed/",
    "insideevs": "https://insideevs.com/feed/",
    "evnewsdaily": "https://evnewsdaily.com/feed/",
    "cleantechnica": "https://cleantechnica.com/feed/",
}

OEM_BRANDS = [
    "Tesla", "BYD", "Volkswagen", "BMW", "Mercedes", "Ford", "GM",
    "Hyundai", "Kia", "Rivian", "NIO", "Porsche", "Audi", "Lucid",
    "Volvo", "Xiaomi", "Polestar", "Chrysler", "Jeep", "Mazda",
]

ARXIV_KEYWORDS = {
    "plug-and-charge": [
        "plug and charge", "ISO 15118", "CCS charging", "vehicle grid communication",
        "EVSE authentication", "ISO 15118-20",
    ],
    "v2g-reversible-charge": [
        "vehicle to grid", "V2G", "bidirectional EV charging", "reversible charging",
        "vehicle-to-grid", "V2H", "vehicle to home", "demand response EV",
    ],
    "battery-technology": [
        "solid-state battery EV", "lithium-sulfur battery", "EV battery technology",
        "battery energy density", "next-generation battery electric vehicle",
        "battery thermal runaway",
    ],
}

LLM_MODEL = "openrouter/free"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"