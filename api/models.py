"""
GTM Intelligence — API Models

Pydantic request and response models for all endpoints.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Query ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000, description="The GTM question to answer")
    source_filter: Optional[str] = Field(None, description="Filter by source: selling-signals | gtm-strategist")
    type_filter: Optional[str] = Field(None, description="Filter by type: tactical | strategic | framework | tooling | case-study")
    max_sources: Optional[int] = Field(6, ge=1, le=10, description="Max corpus entries to include")


class SourceCitation(BaseModel):
    index: int
    title: str
    source: str
    date: str
    url: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[SourceCitation]
    corpus_entries_searched: int


# ── Corpus ────────────────────────────────────────────────────────────────────

class CorpusEntry(BaseModel):
    slug: str
    source: str
    date: str
    title: str
    type: str
    audience: str
    tags: list[str]
    concepts: list[str]
    summary: str
    url: Optional[str] = None
    file: str


class CorpusIndexResponse(BaseModel):
    total: int
    sources: dict[str, int]
    types: dict[str, int]
    latest: Optional[str]
    entries: list[CorpusEntry]


# ── Dedup ─────────────────────────────────────────────────────────────────────

class DedupeRequest(BaseModel):
    records: list[dict[str, Any]] = Field(..., description="List of CRM records to check for duplicates")
    crm: str = Field(..., description="CRM type: hubspot | salesforce")
    confidence_threshold: Optional[str] = Field("MEDIUM", description="Minimum confidence to flag: HIGH | MEDIUM | LOW")


class DuplicateFinding(BaseModel):
    confidence: str
    record_ids: list[str]
    reason: str
    keep_record_id: str
    merge_fields: list[str]
    notes: Optional[str] = None


class DedupeResponse(BaseModel):
    crm: str
    records_analyzed: int
    duplicates_found: int
    findings: list[DuplicateFinding]


# ── Field standardization ─────────────────────────────────────────────────────

class StandardizeRequest(BaseModel):
    records: list[dict[str, Any]] = Field(..., description="List of CRM records to standardize")
    crm: str = Field(..., description="CRM type: hubspot | salesforce")
    fields: Optional[list[str]] = Field(None, description="Specific fields to standardize (default: all)")


class StandardizationResult(BaseModel):
    record_id: str
    original: dict[str, Any]
    standardized: dict[str, Any]
    changes: list[str]


class StandardizeResponse(BaseModel):
    crm: str
    records_processed: int
    results: list[StandardizationResult]


# ── Health score ──────────────────────────────────────────────────────────────

class HealthScoreRequest(BaseModel):
    records: list[dict[str, Any]] = Field(..., description="List of CRM records to score")
    crm: str = Field(..., description="CRM type: hubspot | salesforce")


class HealthScoreResult(BaseModel):
    record_id: str
    score: int
    grade: str
    missing_fields: list[str]
    recommendations: list[str]


class HealthScoreResponse(BaseModel):
    crm: str
    records_scored: int
    average_score: float
    grade_distribution: dict[str, int]
    results: list[HealthScoreResult]


# ── HubSpot Deploy ────────────────────────────────────────────────────────────

class HubSpotConnectRequest(BaseModel):
    api_key: str
    object_type: str = Field("contacts", description="contacts | companies | both")
    limit: int = Field(500, ge=10, le=2000)


class HubSpotConnectResponse(BaseModel):
    portal_id: str
    hub_domain: str
    records_fetched: int
    object_type: str


class DeployPreview(BaseModel):
    tool: str
    records_analyzed: int
    changes_found: int
    summary: str
    preview_data: Any


class HubSpotApplyRequest(BaseModel):
    api_key: str
    tool: str
    object_type: str
    confirmed_changes: list[dict[str, Any]]


class HubSpotApplyResponse(BaseModel):
    tool: str
    records_updated: int
    errors: list[str]
    summary: str


# ── General ───────────────────────────────────────────────────────────────────

class HealthCheck(BaseModel):
    status: str
    corpus_total: int
    sources: dict[str, int]
    version: str = "0.1.0"
