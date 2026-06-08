"""
GTM Intelligence — Salesforce Tools Route

POST /tools/salesforce/dedup         — Deduplicate Leads/Contacts/Accounts
POST /tools/salesforce/standardize   — Standardize field values
POST /tools/salesforce/health        — Score data health

Mirrors the HubSpot routes. Salesforce-specific field mapping and
SOQL integration will be layered in as the CRM connectors are built.
"""

import json
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from api.models import (
    DedupeRequest, DedupeResponse, DuplicateFinding,
    StandardizeRequest, StandardizeResponse, StandardizationResult,
    HealthScoreRequest, HealthScoreResponse, HealthScoreResult,
)
from rag.prompts import DEDUP_ANALYSIS_PROMPT, STANDARDIZATION_PROMPT, HEALTH_SCORE_PROMPT

router = APIRouter(prefix="/tools/salesforce", tags=["Salesforce"])
client = anthropic.Anthropic()


def call_claude_json(prompt: str) -> list | dict:
    """Call Claude and parse JSON response."""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        import re
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


@router.post("/dedup", response_model=DedupeResponse)
async def salesforce_dedup(request: DedupeRequest):
    """
    Analyze Salesforce records (Leads, Contacts, Accounts) for duplicates.

    Handles the Lead-to-Contact conversion duplicate scenario that is
    endemic in Salesforce orgs with manual data entry and poor governance.

    Future: SOQL queries to pull and deduplicate directly from SFDC org.
    """
    if not request.records:
        raise HTTPException(status_code=400, detail="No records provided")
    if len(request.records) > 500:
        raise HTTPException(status_code=400, detail="Max 500 records per request")

    records_json = json.dumps(request.records, indent=2)
    prompt = DEDUP_ANALYSIS_PROMPT.format(records=records_json)

    try:
        findings_raw = call_claude_json(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

    threshold_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    min_confidence = threshold_map.get(request.confidence_threshold or "MEDIUM", 2)

    findings = []
    for f in findings_raw:
        conf_level = threshold_map.get(f.get("confidence", "LOW"), 1)
        if conf_level >= min_confidence:
            findings.append(DuplicateFinding(**f))

    return DedupeResponse(
        crm="salesforce",
        records_analyzed=len(request.records),
        duplicates_found=len(findings),
        findings=findings,
    )


@router.post("/standardize", response_model=StandardizeResponse)
async def salesforce_standardize(request: StandardizeRequest):
    """
    Standardize field values across Salesforce records.

    Salesforce-specific: handles Lead Source normalization, Account naming
    conventions, and standard picklist value alignment.

    Future: Apex-compatible output format for direct SFDC import.
    """
    if not request.records:
        raise HTTPException(status_code=400, detail="No records provided")

    records_json = json.dumps(request.records, indent=2)
    prompt = STANDARDIZATION_PROMPT.format(records=records_json)

    try:
        results_raw = call_claude_json(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Standardization error: {str(e)}")

    results = [StandardizationResult(**r) for r in results_raw]

    return StandardizeResponse(
        crm="salesforce",
        records_processed=len(results),
        results=results,
    )


@router.post("/health", response_model=HealthScoreResponse)
async def salesforce_health(request: HealthScoreRequest):
    """
    Score data quality and completeness for Salesforce records.

    Salesforce-specific: accounts for Lead vs Contact object differences,
    Opportunity stage completeness, and Account hierarchy gaps.

    Future: writes scores back to SFDC as a custom field via REST API.
    """
    if not request.records:
        raise HTTPException(status_code=400, detail="No records provided")

    records_json = json.dumps(request.records, indent=2)
    prompt = HEALTH_SCORE_PROMPT.format(records=records_json)

    try:
        results_raw = call_claude_json(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health scoring error: {str(e)}")

    results = [HealthScoreResult(**r) for r in results_raw]

    total_score = sum(r.score for r in results)
    avg_score = round(total_score / len(results), 1) if results else 0.0

    grade_dist: dict = {"A": 0, "B": 0, "C": 0, "D": 0}
    for r in results:
        grade_letter = r.grade.split()[0] if r.grade else "D"
        if grade_letter in grade_dist:
            grade_dist[grade_letter] += 1

    return HealthScoreResponse(
        crm="salesforce",
        records_scored=len(results),
        average_score=avg_score,
        grade_distribution=grade_dist,
        results=results,
    )
