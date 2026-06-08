# GTM Intelligence — CLAUDE.md

## What this is

The knowledge base and API backbone for the GTM portfolio. Three functions: (1) RAG knowledge base over curated GTM newsletters, (2) deployable CRM tools (HubSpot/Salesforce), (3) corpus that feeds portfolio content and toolkit context.

Deployed at: [gtm-intelligence-danielcohenmba.vercel.app](https://gtm-intelligence-danielcohenmba.vercel.app)

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.11+ |
| API | FastAPI |
| RAG | Claude API (context stuffing, no vector DB) |
| Corpus | Markdown files + JSON metadata index |
| Hosting | Vercel (auto-deploys from GitHub main) |

## Repo structure

```
gtm-intelligence/
├── corpus/
│   ├── selling-signals/     # One .md per article
│   └── gtm-strategist/      # One .md per article
├── index/
│   └── metadata.json        # Searchable index — must stay in sync
├── api/
│   ├── main.py
│   ├── routes/
│   │   ├── query.py         # RAG endpoint
│   │   └── corpus.py
│   └── models.py            # CorpusEntry (slug, source, date, title, tags, concepts, summary, url, file)
├── rag/
│   ├── retriever.py
│   └── prompts.py
└── scripts/
    └── ingest.py            # update_index() writes url field
```

## Corpus

**Sources**: GTM Strategist (Maja Voje, Nico Druelle, Karl Rafidimanana), Selling Signals

**Current entries** (5):
1. AI-Led GTM Reinvention: OAR Matrix and Four Buying Lanes (2026-06-08)
2. How to Rank #1 in ChatGPT: AEO Guide (2026-05-29)
3. More Data Isn't Creating More Clarity (2026-05-28, Selling Signals)
4. The GTM Repository for Claude Code (2026-04-10)
5. Content Engineering: Build a Content System in Claude Code (2026-05-01)

## Ingestion pipeline

```bash
python scripts/ingest.py --file path/to/article.md --source gtm-strategist
```

Each article → markdown file in `corpus/[source]/[slug].md` + entry in `index/metadata.json`. Always update `total` count and `last_updated` in metadata.json.

**Corpus frontmatter fields**: slug, source, date, title, type, audience, tags, concepts, url, file

## Current priorities

- Keep metadata.json in sync as articles are ingested (total count, last_updated)
- url field on CorpusEntry is now live — include for every new article
- Article pipeline informs both portfolio copy AND toolkit tool ideas

## Article → downstream pipeline

Each new article triggers:
1. **Ingest** → corpus .md + metadata.json entry
2. **Toolkit** → does this suggest a new tool or improvement?
3. **Portfolio** → does this change positioning copy or add a section?

## Key concepts from corpus

**GTM Repository architecture** (5 layers): CLAUDE.md → context/ → skills/ → workflows/ → outputs/
**Signal decay**: time-weight all signals; 30-pt signal decays to 15 after 60 days
**Signal combinations**: two signals > sum of parts (Series B + new RevOps hire = 80, not 50)
**Sophisticated slop**: 90% of AI output quality comes from context, not pipeline
**OAR Matrix**: Optimize → Amplify → Reinvent (AI placement framework)
**Four buying lanes**: Human-only → AI-assisted → AI-led → AI-to-AI
**AEO**: AI search visibility across ChatGPT, Claude, Perplexity
