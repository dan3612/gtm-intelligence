#!/usr/bin/env python3
"""
GTM Intelligence — Email Ingestion Pipeline

Takes a raw email (text or .eml file) and outputs:
  - A clean markdown file in the appropriate corpus folder
  - An updated metadata.json index entry

Usage:
  python scripts/ingest.py --file path/to/email.txt --source selling-signals
  python scripts/ingest.py --file path/to/email.eml --source gtm-strategist
  python scripts/ingest.py --stdin --source selling-signals   # pipe raw text
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import anthropic

# ── Paths ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
CORPUS_DIR = ROOT / "corpus"
INDEX_FILE = ROOT / "index" / "metadata.json"

VALID_SOURCES = ["selling-signals", "gtm-strategist"]

# ── Claude extraction ─────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are processing a GTM newsletter email for a structured knowledge base.

Given the raw email content below, extract and return a JSON object with these exact fields:

{{
  "title": "Clean, descriptive title (not the email subject line noise — just the core topic)",
  "date": "ISO date string YYYY-MM-DD (from the email headers or content — if unknown use today)",
  "tags": ["list", "of", "topic", "tags", "max 6", "lowercase hyphenated"],
  "concepts": ["key concepts covered", "max 8", "noun phrases"],
  "audience": "who this content is most relevant to (e.g. RevOps leader, AE, SDR, CMO, GTM founder)",
  "type": "one of: tactical | strategic | framework | tooling | case-study",
  "summary": "2-3 sentence summary of the core insight or argument",
  "body": "The full cleaned body of the email. Strip: unsubscribe links, email headers, tracking pixels, nav menus, footer boilerplate, social share buttons, HTML artifacts. Keep: all substantive content, subheadings, lists, examples, data points, quotes. Preserve markdown-friendly formatting."
}}

Return only valid JSON. No preamble, no explanation, no markdown fences.

Raw email:
---
{raw_email}
---"""


def extract_with_claude(raw_text: str, source: str) -> dict:
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT.format(raw_email=raw_text),
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # Strip markdown fences if Claude wraps anyway
    if response_text.startswith("```"):
        response_text = re.sub(r"^```(?:json)?\n?", "", response_text)
        response_text = re.sub(r"\n?```$", "", response_text)

    return json.loads(response_text)


# ── File writing ──────────────────────────────────────────────────────────────

def build_frontmatter(meta: dict, source: str, slug: str) -> str:
    tags_str = "\n".join(f"  - {t}" for t in meta.get("tags", []))
    concepts_str = "\n".join(f"  - {c}" for c in meta.get("concepts", []))

    return f"""---
source: {source}
date: {meta['date']}
title: "{meta['title']}"
slug: {slug}
type: {meta['type']}
audience: {meta['audience']}
tags:
{tags_str}
concepts:
{concepts_str}
summary: "{meta['summary'].replace('"', "'")}"
---"""


def slugify(title: str, date: str) -> str:
    clean = re.sub(r"[^\w\s-]", "", title.lower())
    clean = re.sub(r"[\s_]+", "-", clean).strip("-")
    clean = clean[:60]
    return f"{date}-{clean}"


def write_corpus_file(meta: dict, source: str) -> Path:
    slug = slugify(meta["title"], meta["date"])
    output_dir = CORPUS_DIR / source
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{slug}.md"

    frontmatter = build_frontmatter(meta, source, slug)
    body = meta.get("body", "")

    content = f"{frontmatter}\n\n# {meta['title']}\n\n{body}\n"

    output_path.write_text(content, encoding="utf-8")
    return output_path


def update_index(meta: dict, source: str, slug: str, file_path: Path):
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {"entries": [], "last_updated": None}

    # Avoid duplicates by slug
    existing_slugs = {e["slug"] for e in index["entries"]}
    if slug in existing_slugs:
        print(f"  Skipping index update — slug already exists: {slug}")
        return

    entry = {
        "slug": slug,
        "source": source,
        "date": meta["date"],
        "title": meta["title"],
        "type": meta["type"],
        "audience": meta["audience"],
        "tags": meta.get("tags", []),
        "concepts": meta.get("concepts", []),
        "summary": meta["summary"],
        "file": str(file_path.relative_to(ROOT)),
    }

    index["entries"].append(entry)
    index["entries"].sort(key=lambda x: x["date"], reverse=True)
    index["last_updated"] = datetime.utcnow().isoformat()
    index["total"] = len(index["entries"])

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ingest a newsletter email into the GTM Intelligence corpus.")
    parser.add_argument("--file", type=str, help="Path to raw email file (.txt or .eml)")
    parser.add_argument("--stdin", action="store_true", help="Read raw email from stdin")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        choices=VALID_SOURCES,
        help=f"Newsletter source: {', '.join(VALID_SOURCES)}",
    )
    args = parser.parse_args()

    # Read raw input
    if args.stdin:
        print("Reading from stdin...")
        raw_text = sys.stdin.read()
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: file not found: {args.file}")
            sys.exit(1)
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    else:
        print("Error: provide --file or --stdin")
        sys.exit(1)

    if not raw_text.strip():
        print("Error: empty input")
        sys.exit(1)

    print(f"Extracting content from {args.source} email...")
    meta = extract_with_claude(raw_text, args.source)

    slug = slugify(meta["title"], meta["date"])

    print(f"  Title:    {meta['title']}")
    print(f"  Date:     {meta['date']}")
    print(f"  Type:     {meta['type']}")
    print(f"  Audience: {meta['audience']}")
    print(f"  Tags:     {', '.join(meta.get('tags', []))}")
    print(f"  Slug:     {slug}")

    corpus_path = write_corpus_file(meta, args.source)
    print(f"\nCorpus file written: {corpus_path}")

    update_index(meta, args.source, slug, corpus_path)
    print(f"Index updated: {INDEX_FILE}")

    print("\nDone.")


if __name__ == "__main__":
    main()
