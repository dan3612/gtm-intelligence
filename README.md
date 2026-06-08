# GTM Intelligence

A source-agnostic GTM knowledge base and tooling platform built on curated newsletter content, with deployable integrations for HubSpot and Salesforce.

---

## What this is

GTM Intelligence does three things:

1. **Knowledge base** — A structured, queryable corpus built from the best GTM newsletters (Selling Signals, GTM Strategist). Ask any GTM question and get a grounded answer with source citations.

2. **Portfolio** — A public-facing showcase of how a senior RevOps professional thinks and builds. Live demo, real tools, real architecture.

3. **Deployable tools** — Production-ready integrations for HubSpot and Salesforce: deduplication, field standardization, data health scoring. Installable by any org.

---

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.11+ |
| API | FastAPI |
| RAG | Claude API (context stuffing, no vector DB needed at corpus scale) |
| Corpus | Markdown files + JSON metadata index |
| Hosting | Railway (auto-deploys from GitHub) |
| Frontend | Lovable (calls this API) |

---

## Repo structure

```
gtm-intelligence/
├── corpus/
│   ├── selling-signals/        # One .md file per email
│   └── gtm-strategist/         # One .md file per email
├── index/
│   └── metadata.json           # Searchable index of all corpus files
├── tools/
│   ├── hubspot/
│   │   ├── dedup/
│   │   ├── field-standardization/
│   │   └── health-score/
│   └── salesforce/
│       ├── dedup/
│       ├── field-standardization/
│       └── health-score/
├── rag/
│   ├── retriever.py            # Corpus search and chunk selection
│   └── prompts.py              # Claude prompt templates
├── api/
│   ├── main.py                 # FastAPI app entry point
│   ├── routes/
│   │   ├── query.py            # RAG query endpoint
│   │   ├── hubspot.py          # HubSpot tool endpoints
│   │   └── salesforce.py       # Salesforce tool endpoints
│   └── models.py               # Pydantic request/response models
├── scripts/
│   └── ingest.py               # Email ingestion pipeline
├── docs/
│   └── api.md                  # API documentation
├── requirements.txt
├── Procfile                    # Railway deployment
├── .env.example
└── README.md
```

---

## Corpus format

Every email becomes a single markdown file with YAML frontmatter:

```
corpus/selling-signals/2026-06-01-lead-scoring-frameworks.md
```

Frontmatter fields:
- `source` — newsletter slug
- `date` — ISO date string
- `title` — cleaned subject line
- `tags` — list of topic tags
- `concepts` — key concepts extracted
- `audience` — who this is most relevant to
- `type` — tactical | strategic | framework | tooling | case-study

---

## Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your ANTHROPIC_API_KEY

# Ingest an email
python scripts/ingest.py --file path/to/email.txt --source selling-signals

# Start the API
uvicorn api.main:app --reload
```

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/query` | Ask a GTM question, get a grounded answer |
| GET | `/corpus/index` | List all corpus entries with metadata |
| POST | `/tools/hubspot/dedup` | Run deduplication on HubSpot contacts |
| POST | `/tools/hubspot/standardize` | Standardize field values |
| POST | `/tools/hubspot/health` | Score contact/company data health |
| POST | `/tools/salesforce/dedup` | Run deduplication on Salesforce records |
| POST | `/tools/salesforce/standardize` | Standardize field values |
| POST | `/tools/salesforce/health` | Score record data health |

---

## Deployment

Connects to Railway via GitHub. Push to `main` triggers auto-deploy.

```
Procfile: web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

---

## Built by

Dan Cohen — Director of RevOps. Four founding RevOps roles at B2B SaaS companies. Deep HubSpot and Salesforce practitioner.

[LinkedIn](https://linkedin.com/in/danielcohenmba) · [GitHub](https://github.com/dan3612)
