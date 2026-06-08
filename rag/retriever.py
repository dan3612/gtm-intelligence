"""
GTM Intelligence — RAG Retriever

Searches the corpus and assembles context for Claude queries.
No vector DB. Uses keyword matching + metadata filtering on the JSON index,
then loads full markdown files for the top matches.

At corpus scale (< 200 files), this is fast, transparent, and portable.
"""

import json
import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
INDEX_FILE = ROOT / "index" / "metadata.json"
CORPUS_DIR = ROOT / "corpus"

# How many corpus entries to include in a single query context
MAX_CONTEXT_ENTRIES = 6
# Rough token budget per entry body (to avoid blowing context window)
MAX_BODY_CHARS = 3000


def load_index() -> list[dict]:
    if not INDEX_FILE.exists():
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", [])


def load_corpus_file(entry: dict) -> str:
    file_path = ROOT / entry["file"]
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


def extract_body(markdown: str) -> str:
    """Strip frontmatter and return body only."""
    if markdown.startswith("---"):
        parts = markdown.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return markdown.strip()


def score_entry(entry: dict, query_tokens: list[str]) -> float:
    """
    Simple relevance score based on token overlap across metadata fields.
    Weights: concepts > tags > title > summary > audience
    """
    score = 0.0
    query_lower = set(t.lower() for t in query_tokens)

    def token_overlap(text: str) -> float:
        words = set(re.findall(r"\w+", text.lower()))
        return len(query_lower & words) / max(len(query_lower), 1)

    # Title match
    score += token_overlap(entry.get("title", "")) * 2.0

    # Tag match (exact token match on tag strings)
    tag_text = " ".join(entry.get("tags", []))
    score += token_overlap(tag_text) * 3.0

    # Concept match
    concept_text = " ".join(entry.get("concepts", []))
    score += token_overlap(concept_text) * 3.5

    # Summary match
    score += token_overlap(entry.get("summary", "")) * 1.5

    # Audience match
    score += token_overlap(entry.get("audience", "")) * 1.0

    return score


def retrieve(
    query: str,
    source_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    max_results: int = MAX_CONTEXT_ENTRIES,
) -> list[dict]:
    """
    Retrieve the most relevant corpus entries for a query.

    Returns a list of dicts with keys:
      - entry: the metadata entry
      - body: the cleaned body text (truncated if needed)
      - score: relevance score
    """
    index = load_index()

    if not index:
        return []

    # Apply metadata filters
    if source_filter:
        index = [e for e in index if e.get("source") == source_filter]
    if type_filter:
        index = [e for e in index if e.get("type") == type_filter]

    # Tokenize query
    query_tokens = re.findall(r"\w+", query)

    # Score all entries
    scored = []
    for entry in index:
        score = score_entry(entry, query_tokens)
        if score > 0:
            scored.append((score, entry))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Load and return top results
    results = []
    for score, entry in scored[:max_results]:
        raw = load_corpus_file(entry)
        body = extract_body(raw)
        if len(body) > MAX_BODY_CHARS:
            body = body[:MAX_BODY_CHARS] + "\n\n[... truncated for context ...]"

        results.append({
            "entry": entry,
            "body": body,
            "score": round(score, 3),
        })

    return results


def build_context_block(results: list[dict]) -> str:
    """
    Format retrieved results into a context block for Claude.
    """
    if not results:
        return "No relevant corpus entries found."

    blocks = []
    for i, r in enumerate(results, 1):
        entry = r["entry"]
        block = f"""--- SOURCE {i} ---
Title: {entry['title']}
Newsletter: {entry['source']}
Date: {entry['date']}
Type: {entry['type']}
Tags: {', '.join(entry.get('tags', []))}
Summary: {entry['summary']}

{r['body']}"""
        blocks.append(block)

    return "\n\n".join(blocks)


def get_index_stats() -> dict:
    index = load_index()
    if not index:
        return {"total": 0, "sources": {}, "types": {}}

    sources: dict = {}
    types: dict = {}
    for entry in index:
        src = entry.get("source", "unknown")
        typ = entry.get("type", "unknown")
        sources[src] = sources.get(src, 0) + 1
        types[typ] = types.get(typ, 0) + 1

    return {
        "total": len(index),
        "sources": sources,
        "types": types,
        "latest": index[0]["date"] if index else None,
    }
