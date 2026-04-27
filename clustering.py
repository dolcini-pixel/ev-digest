import numpy as np

def cluster_articles(articles, n_topics=5):
    if len(articles) < 3:
        for i, a in enumerate(articles):
            a["cluster_id"] = i
            a["cluster_label"] = a.get("topic", "general")
        return articles

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [
            f"{a.get('title','')} {a.get('summary','')[:200]}".strip()
            for a in articles
        ]
        embeddings = model.encode(texts, show_progress_bar=False)
        cluster_ids = _agglomerate(embeddings, n_topics or 5)
        for a, cid in zip(articles, cluster_ids):
            a["cluster_id"] = int(cid)
    except Exception as e:
        print(f"  [cluster] fallback to topic-based clustering: {e}")
        for i, a in enumerate(articles):
            a["cluster_id"] = i % (n_topics or 5)
    return articles

def _agglomerate(embeddings, n_clusters):
    from sklearn.cluster import AgglomerativeClustering
    n_clusters = min(n_clusters, len(embeddings))
    if n_clusters < 2:
        return np.zeros(len(embeddings), dtype=int)
    X = np.array(embeddings)
    model = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric="cosine",
        linkage="average",
    )
    return model.fit_predict(X)

def group_by_cluster(articles):
    groups = {}
    for a in articles:
        cid = a.get("cluster_id", 0)
        groups.setdefault(cid, []).append(a)
    return groups