"""
GTM Intelligence — FastAPI Application

Entry point for the GTM Intelligence backend API.
Serves the RAG query layer and CRM tool endpoints.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))
from api.models import HealthCheck
from api.routes import query, hubspot, salesforce
from rag.retriever import get_index_stats

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="GTM Intelligence API",
    description="A curated GTM knowledge base and CRM data quality tooling platform. Built by Dan Cohen.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

_explicit_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    os.getenv("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in _explicit_origins if o],
    allow_origin_regex=r"https://.*\.(lovable\.app|lovableproject\.com|vercel\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(query.router, tags=["Knowledge Base"])
app.include_router(hubspot.router)
app.include_router(salesforce.router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthCheck)
async def root():
    """API health check and corpus status."""
    stats = get_index_stats()
    return HealthCheck(
        status="ok",
        corpus_total=stats.get("total", 0),
        sources=stats.get("sources", {}),
    )


@app.get("/health", response_model=HealthCheck)
async def health():
    """Health check endpoint for Railway."""
    stats = get_index_stats()
    return HealthCheck(
        status="ok",
        corpus_total=stats.get("total", 0),
        sources=stats.get("sources", {}),
    )
