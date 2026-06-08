"""
GTM Intelligence — HubSpot Deployment Routes

POST /deploy/hubspot/connect     — Verify API key + fetch records, return preview count
POST /deploy/hubspot/dedup       — Pull contacts/companies, run dedup analysis
POST /deploy/hubspot/standardize — Pull records, run standardization analysis
POST /deploy/hubspot/health      — Pull records, run health scoring
POST /deploy/hubspot/apply       — Apply confirmed changes back to HubSpot
"""

import json
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
import httpx

import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from api.models import (
    HubSpotConnectRequest, HubSpotConnectResponse,
    DeployPreview, HubSpotApplyRequest, HubSpotApplyResponse,
)
from api.hubspot_client import (
    verify_connection, fetch_contacts, fetch_companies,
    merge_contacts, merge_companies, batch_update, ensure_health_score_property,
)
from rag.prompts import DEDUP_ANALYSIS_PROMPT, STANDARDIZATION_PROMPT, HEALTH_SCORE_PROMPT

router = APIRouter(prefix="/deploy/hubspot", tags=["Deploy"])
client = anthropic.Anthropic()


def _call_claude_json(prompt: str) -> list | dict:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        import re
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def _flatten_record(hs_record: dict) -> dict:
    """Flatten HubSpot's {id, properties: {...}} format for Claude analysis."""
    flat = {"id": hs_record["id"]}
    flat.update(hs_record.get("properties", {}))
    return flat


@router.post("/connect", response_model=HubSpotConnectResponse)
async def hs_connect(req: HubSpotConnectRequest):
    """Verify API key and return portal info + record count preview."""
    try:
        info = await verify_connection(req.api_key)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=401, detail="Invalid HubSpot API key")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if req.object_type == "both":
        contacts = await fetch_contacts(req.api_key, limit=10)
        companies = await fetch_companies(req.api_key, limit=10)
        fetched = len(contacts) + len(companies)
    elif req.object_type == "companies":
        records = await fetch_companies(req.api_key, limit=10)
        fetched = len(records)
    else:
        records = await fetch_contacts(req.api_key, limit=10)
        fetched = len(records)

    return HubSpotConnectResponse(
        portal_id=str(info.get("portalId", "")),
        hub_domain=info.get("uiDomain", ""),
        records_fetched=fetched,
        object_type=req.object_type,
    )


@router.post("/dedup", response_model=DeployPreview)
async def hs_dedup_preview(req: HubSpotConnectRequest):
    """Pull records and return a deduplication preview."""
    try:
        if req.object_type in ("contacts", "both"):
            contacts = await fetch_contacts(req.api_key, req.limit)
        else:
            contacts = []
        if req.object_type in ("companies", "both"):
            companies = await fetch_companies(req.api_key, req.limit)
        else:
            companies = []
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=401, detail="Invalid HubSpot API key")

    all_records = [_flatten_record(r) for r in contacts + companies]
    if not all_records:
        raise HTTPException(status_code=400, detail="No records found")

    # Run in batches of 200 to stay within Claude context
    findings = []
    for i in range(0, len(all_records), 200):
        batch = all_records[i:i + 200]
        prompt = DEDUP_ANALYSIS_PROMPT.format(records=json.dumps(batch, indent=2))
        try:
            batch_findings = _call_claude_json(prompt)
            findings.extend(batch_findings if isinstance(batch_findings, list) else [])
        except Exception:
            continue

    # Only HIGH/MEDIUM confidence
    filtered = [f for f in findings if f.get("confidence") in ("HIGH", "MEDIUM")]

    return DeployPreview(
        tool="dedup",
        records_analyzed=len(all_records),
        changes_found=len(filtered),
        summary=f"Found {len(filtered)} duplicate pairs across {len(all_records)} records. High confidence: {sum(1 for f in filtered if f.get('confidence') == 'HIGH')}.",
        preview_data=filtered[:50],  # Cap preview at 50 pairs
    )


@router.post("/standardize", response_model=DeployPreview)
async def hs_standardize_preview(req: HubSpotConnectRequest):
    """Pull records and return standardization changes preview."""
    try:
        if req.object_type in ("contacts", "both"):
            contacts = await fetch_contacts(req.api_key, req.limit)
        else:
            contacts = []
        if req.object_type in ("companies", "both"):
            companies = await fetch_companies(req.api_key, req.limit)
        else:
            companies = []
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=401, detail="Invalid HubSpot API key")

    all_records = [_flatten_record(r) for r in contacts + companies]
    if not all_records:
        raise HTTPException(status_code=400, detail="No records found")

    results = []
    for i in range(0, len(all_records), 100):
        batch = all_records[i:i + 100]
        prompt = STANDARDIZATION_PROMPT.format(records=json.dumps(batch, indent=2))
        try:
            batch_results = _call_claude_json(prompt)
            results.extend(batch_results if isinstance(batch_results, list) else [])
        except Exception:
            continue

    changed = [r for r in results if r.get("changes")]

    return DeployPreview(
        tool="standardize",
        records_analyzed=len(all_records),
        changes_found=len(changed),
        summary=f"{len(changed)} of {len(all_records)} records have fields that need standardization.",
        preview_data=changed[:50],
    )


@router.post("/health", response_model=DeployPreview)
async def hs_health_preview(req: HubSpotConnectRequest):
    """Pull records and return health scores preview."""
    try:
        if req.object_type in ("contacts", "both"):
            contacts = await fetch_contacts(req.api_key, req.limit)
        else:
            contacts = []
        if req.object_type in ("companies", "both"):
            companies = await fetch_companies(req.api_key, req.limit)
        else:
            companies = []
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=401, detail="Invalid HubSpot API key")

    all_records = [_flatten_record(r) for r in contacts + companies]
    if not all_records:
        raise HTTPException(status_code=400, detail="No records found")

    results = []
    for i in range(0, len(all_records), 100):
        batch = all_records[i:i + 100]
        prompt = HEALTH_SCORE_PROMPT.format(records=json.dumps(batch, indent=2))
        try:
            batch_results = _call_claude_json(prompt)
            results.extend(batch_results if isinstance(batch_results, list) else [])
        except Exception:
            continue

    avg = round(sum(r.get("score", 0) for r in results) / len(results), 1) if results else 0
    poor = [r for r in results if r.get("score", 100) < 50]

    return DeployPreview(
        tool="health",
        records_analyzed=len(all_records),
        changes_found=len(poor),
        summary=f"Average health score: {avg}/100. {len(poor)} records below 50 — flagged for enrichment.",
        preview_data=results[:50],
    )


@router.post("/apply", response_model=HubSpotApplyResponse)
async def hs_apply(req: HubSpotApplyRequest):
    """Apply confirmed changes to HubSpot."""
    errors = []
    updated = 0

    try:
        if req.tool == "dedup":
            for finding in req.confirmed_changes:
                primary = finding.get("keep_record_id")
                ids = finding.get("record_ids", [])
                secondary = next((i for i in ids if i != primary), None)
                if not primary or not secondary:
                    continue
                try:
                    if req.object_type in ("companies",):
                        await merge_companies(req.api_key, primary, secondary)
                    else:
                        await merge_contacts(req.api_key, primary, secondary)
                    updated += 1
                except Exception as e:
                    errors.append(f"Merge {primary}←{secondary}: {str(e)}")

        elif req.tool == "standardize":
            updates = []
            for result in req.confirmed_changes:
                if result.get("changes"):
                    updates.append({
                        "id": result["record_id"],
                        "properties": result["standardized"],
                    })
            if updates:
                obj = "companies" if req.object_type == "companies" else "contacts"
                r = await batch_update(req.api_key, obj, updates)
                updated = r["updated"]
                errors = r["errors"]

        elif req.tool == "health":
            obj = "companies" if req.object_type == "companies" else "contacts"
            await ensure_health_score_property(req.api_key, obj)
            updates = [
                {"id": r["record_id"], "properties": {"gtm_health_score": str(r["score"])}}
                for r in req.confirmed_changes
            ]
            if updates:
                r = await batch_update(req.api_key, obj, updates)
                updated = r["updated"]
                errors = r["errors"]

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=401, detail="HubSpot API error — check your key")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return HubSpotApplyResponse(
        tool=req.tool,
        records_updated=updated,
        errors=errors,
        summary=f"Applied {updated} changes to HubSpot.{' ' + str(len(errors)) + ' errors.' if errors else ''}",
    )
