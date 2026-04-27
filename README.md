EV_Digest
=========
Weekly EV technology digest agent. Monitors arXiv, Hacker News, lobste.rs, RSS feeds (Electrek, InsideEVs, EV News Daily, CleanTechnica), Reddit, and EV Database. Clusters articles, synthesizes with LLM, tracks OEM tech deployments, and deploys to GitHub Pages.

Setup
------
::

    pip install -r requirements.txt
    # ensure OPENROUTER_API_KEY is in ~/.env (from serach_info/.env)
    python main.py          # manual run
    crontab -e            # add weekly schedule

Cron schedule (every Monday 08:00)::

    0 8 * * 1  cd ~/Python/ev_digest && /usr/bin/python3 main.py >> ~/Python/ev_digest/digest.log 2>&1

GitHub Pages
-----------
- Repo: ``dolcini-pixel/ev-digest`` (private)
- Branch: ``gh-pages`` / ``/docs`` folder
- URL: https://dolcini-pixel.github.io/ev-digest (after enabling Pages in repo settings)
- Deploys automatically on each ``git push`` to ``gh-pages``

Architecture
------------
- ``config.py``     — env vars, topics, source URLs, OEM brands
- ``db.py``          — SQLite schema and helper queries
- ``sources/``      — per-source fetchers (arXiv, HN, Lobsters, RSS, EV DB, Reddit)
- ``clustering.py``   — sentence-transformers embed + sklearn cluster
- ``synthesis.py``  — OpenRouter LLM synthesis per cluster
- ``oem_tracker.py`` — scrape EV Database → upsert SQLite → diff vs last run
- ``render.py``      — HTML page generator
- ``deploy.py``      — git push to gh-pages branch
- ``agent.py``       — main orchestrator
- ``main.py``        — CLI entry point