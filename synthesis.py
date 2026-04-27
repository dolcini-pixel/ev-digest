import urllib.request
import json

def synthesize_cluster(cluster_articles, cluster_label):
    if not cluster_articles:
        return {
            "label": cluster_label,
            "synthesis": "No articles found for this topic this week.",
            "sources": [],
            "so_what": "No action needed.",
            "lab_vs_production": "unknown",
        }

    topic_intro = {
        "plug-and-charge": "Plug and Charge (ISO 15118)",
        "v2g-reversible-charge": "Vehicle-to-Grid (V2G) and Reversible Charging",
        "battery-technology": "EV Battery Technology",
    }
    display_name = topic_intro.get(cluster_label, cluster_label.replace("-", " ").title())

    article_lines = []
    for a in cluster_articles[:8]:
        title = a.get("title", "Untitled")[:120]
        url = a.get("url", "")
        src = a.get("source", "unknown")
        summary = a.get("summary", "")[:200]
        article_lines.append(f"- [{title}]({url}) ({src})\n  {summary}")

    context = "\n".join(article_lines)

    prompt = (
        f"You are a technical digest writer for the electric vehicle industry. "
        f"Given these {len(cluster_articles)} articles about **{display_name}**, produce a structured weekly digest.\n\n"
        f"ARTICLES:\n{context}\n\n"
        f'Write the response STRICTLY as a JSON object with this exact shape — no markdown, no preamble:\n'
        f'{{"synthesis": "2-3 sentence technical synthesis of what happened this week and why it matters",\n'
        f'"sources": [\n'
        f'  {{ "title": "...", "url": "...", "source": "..." }},\n'
        f'  {{ "title": "...", "url": "...", "source": "..." }},\n'
        f'  {{ "title": "...", "url": "...", "source": "..." }}\n'
        f'],\n'
        f'"so_what": "One sentence: should a builder act on this today or is it lab-only?",\n'
        f'"lab_vs_production": "lab | production | early_stages"\n'
        f'}}'
    )

    try:
        result = _call_llm(prompt)
        result["label"] = cluster_label
        return result
    except Exception as e:
        print(f"  [synthesis] error for {cluster_label}: {e}")
        return _fallback_synthesis(cluster_label, cluster_articles)

def _call_llm(prompt):
    import config

    payload = {
        "model": config.LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a concise, technically precise digest writer. "
                    "Respond ONLY with a JSON object. No markdown, no explanation, no preamble."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }

    req = urllib.request.Request(
        config.OPENROUTER_BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "HTTP-Referer": "https://dolcini-pixel.github.io/ev-digest",
            "X-Title": "EV Digest Agent",
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        raw_response = resp.read().decode("utf-8")
        if not raw_response.strip():
            raise ValueError("Empty response from LLM API")
        data = json.loads(raw_response)

    if "choices" not in data:
        raise ValueError(f"API error: {data.get('error', data)}")

    choice = data["choices"][0]
    raw = choice.get("message", {}).get("content") or ""

    if not raw:
        raw = choice.get("reasoning") or choice.get("text") or ""
        if not raw:
            raise ValueError(f"Empty content from model. Choice: {choice}")

    raw = raw.strip()

    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())

def synthesize_all(grouped_articles):
    results = {}
    for cluster_id, articles in grouped_articles.items():
        label = articles[0].get("topic") or f"cluster-{cluster_id}"
        results[label] = synthesize_cluster(articles, label)
    return results

def _fallback_synthesis(cluster_label, cluster_articles):
    topic_display = {
        "plug-and-charge": "Plug and Charge (ISO 15118)",
        "v2g-reversible-charge": "Vehicle-to-Grid (V2G) and Reversible Charging",
        "battery-technology": "EV Battery Technology",
    }
    display = topic_display.get(cluster_label, cluster_label.replace("-", " ").title())
    sources = [
        {"title": a.get("title", "")[:100], "url": a.get("url", ""), "source": a.get("source", "")}
        for a in cluster_articles[:3] if a.get("url")
    ]
    titles = " | ".join(a.get("title", "")[:80] for a in cluster_articles[:3])
    return {
        "label": cluster_label,
        "synthesis": f"{len(cluster_articles)} articles found about {display}: {titles}. See sources for details.",
        "sources": sources,
        "so_what": "Review sources for details.",
        "lab_vs_production": "unknown",
    }