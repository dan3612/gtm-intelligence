"""
HubSpot API client — pulls and pushes CRM records using a Private App token.
All methods are async and handle pagination automatically.
"""

import httpx
from typing import Any

HS_BASE = "https://api.hubapi.com"

CONTACT_PROPS = [
    "firstname", "lastname", "email", "phone", "jobtitle",
    "company", "website", "hs_lead_status", "lifecyclestage",
    "city", "state", "country", "createdate", "lastmodifieddate",
]

COMPANY_PROPS = [
    "name", "domain", "phone", "industry", "city", "state",
    "country", "numberofemployees", "annualrevenue",
    "hs_lead_status", "lifecyclestage", "createdate", "lastmodifieddate",
]


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


async def verify_connection(api_key: str) -> dict:
    """Check that the API key is valid and return portal info."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{HS_BASE}/account-info/v3/details",
            headers=_headers(api_key),
        )
        r.raise_for_status()
        return r.json()


async def fetch_objects(api_key: str, object_type: str, properties: list[str], limit: int = 500) -> list[dict]:
    """Fetch CRM records with pagination. object_type: contacts | companies."""
    records = []
    after = None
    async with httpx.AsyncClient(timeout=30) as client:
        while len(records) < limit:
            batch = min(100, limit - len(records))
            params = {"limit": batch, "properties": ",".join(properties)}
            if after:
                params["after"] = after
            r = await client.get(
                f"{HS_BASE}/crm/v3/objects/{object_type}",
                headers=_headers(api_key),
                params=params,
            )
            r.raise_for_status()
            data = r.json()
            records.extend(data.get("results", []))
            paging = data.get("paging", {}).get("next", {})
            after = paging.get("after")
            if not after:
                break
    return records


async def fetch_contacts(api_key: str, limit: int = 500) -> list[dict]:
    return await fetch_objects(api_key, "contacts", CONTACT_PROPS, limit)


async def fetch_companies(api_key: str, limit: int = 500) -> list[dict]:
    return await fetch_objects(api_key, "companies", COMPANY_PROPS, limit)


async def merge_contacts(api_key: str, primary_id: str, secondary_id: str) -> dict:
    """Merge two contact records. Primary keeps its ID; secondary is absorbed."""
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"{HS_BASE}/crm/v3/objects/contacts/merge",
            headers=_headers(api_key),
            json={"primaryObjectId": primary_id, "objectIdToMerge": secondary_id},
        )
        r.raise_for_status()
        return r.json()


async def merge_companies(api_key: str, primary_id: str, secondary_id: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"{HS_BASE}/crm/v3/objects/companies/merge",
            headers=_headers(api_key),
            json={"primaryObjectId": primary_id, "objectIdToMerge": secondary_id},
        )
        r.raise_for_status()
        return r.json()


async def batch_update(api_key: str, object_type: str, updates: list[dict[str, Any]]) -> dict:
    """
    Batch update records. updates = [{"id": "123", "properties": {"field": "value"}}]
    HubSpot batch update accepts up to 100 records per call.
    """
    results = {"updated": 0, "errors": []}
    async with httpx.AsyncClient(timeout=30) as client:
        for i in range(0, len(updates), 100):
            chunk = updates[i:i + 100]
            r = await client.post(
                f"{HS_BASE}/crm/v3/objects/{object_type}/batch/update",
                headers=_headers(api_key),
                json={"inputs": chunk},
            )
            if r.status_code == 200:
                results["updated"] += len(chunk)
            else:
                results["errors"].append(r.text)
    return results


async def ensure_health_score_property(api_key: str, object_type: str) -> None:
    """Create the gtm_health_score custom property if it doesn't exist."""
    prop = {
        "name": "gtm_health_score",
        "label": "GTM Health Score",
        "type": "number",
        "fieldType": "number",
        "groupName": "contactinformation" if object_type == "contacts" else "companyinformation",
        "description": "AI-generated data completeness score (0–100). Set by GTM Intelligence.",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{HS_BASE}/crm/v3/properties/{object_type}",
            headers=_headers(api_key),
            json=prop,
        )
        # 409 = already exists, that's fine
        if r.status_code not in (200, 201, 409):
            r.raise_for_status()
