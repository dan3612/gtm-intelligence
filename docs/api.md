# GTM Intelligence API

Base URL: `https://your-railway-app.up.railway.app`

Auto-generated interactive docs available at `/docs` (Swagger) and `/redoc`.

---

## Authentication

No auth required for the public knowledge base query endpoint.

CRM tool endpoints will require API keys in a future release. For now, records are passed directly in the request body.

---

## Endpoints

### GET /

Health check. Returns corpus stats.

```json
{
  "status": "ok",
  "corpus_total": 9,
  "sources": {
    "selling-signals": 6,
    "gtm-strategist": 3
  },
  "version": "0.1.0"
}
```

---

### POST /query

Ask a GTM question. Returns a grounded answer with source citations.

**Request:**
```json
{
  "query": "What's the best way to build a lead scoring model without a data scientist?",
  "source_filter": null,
  "type_filter": null,
  "max_sources": 6
}
```

**Response:**
```json
{
  "query": "...",
  "answer": "Here is the answer with [Source 1] citations inline...",
  "sources": [
    {
      "index": 1,
      "title": "Lead Scoring Without a Data Team",
      "source": "selling-signals",
      "date": "2026-05-15"
    }
  ],
  "corpus_entries_searched": 9
}
```

---

### GET /corpus/index

List all corpus entries with full metadata.

---

### POST /tools/hubspot/dedup

Analyze HubSpot records for duplicates.

**Request:**
```json
{
  "records": [
    {
      "id": "hs_001",
      "firstname": "John",
      "lastname": "Smith",
      "email": "john.smith@acme.com",
      "company": "Acme Corp"
    },
    {
      "id": "hs_002",
      "firstname": "Jon",
      "lastname": "Smith",
      "email": "jsmith@acme.com",
      "company": "Acme"
    }
  ],
  "crm": "hubspot",
  "confidence_threshold": "MEDIUM"
}
```

**Response:**
```json
{
  "crm": "hubspot",
  "records_analyzed": 2,
  "duplicates_found": 1,
  "findings": [
    {
      "confidence": "HIGH",
      "record_ids": ["hs_001", "hs_002"],
      "reason": "Same person at same company, name and email variations",
      "keep_record_id": "hs_001",
      "merge_fields": ["email", "company"],
      "notes": null
    }
  ]
}
```

---

### POST /tools/hubspot/standardize

Standardize field values. Same request/response shape works for `/tools/salesforce/standardize`.

---

### POST /tools/hubspot/health

Score data quality. Returns 0-100 score per record with grade and enrichment recommendations.

Same shape works for `/tools/salesforce/health`.

---

## Roadmap

- [ ] HubSpot OAuth integration (pull/push records directly)
- [ ] Salesforce REST API integration
- [ ] Streaming responses for long query answers
- [ ] Corpus search endpoint (browse by tag, concept, type)
- [ ] HubSpot Marketplace app packaging
- [ ] Salesforce AppExchange packaging
