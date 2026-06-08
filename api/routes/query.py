"""
GTM Intelligence — Query Route

POST /query — Ask a GTM question, get a grounded answer from the corpus.
GET /corpus/index — List all corpus entries with metadata.
"""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from api.models import QueryRequest, QueryResponse, SourceCitation, CorpusIndexResponse, CorpusEntry
from rag.retriever import retrieve, get_index_stats, load_index, build_context_block
from rag.prompts import QUERY_SYSTEM_PROMPT, QUERY_USER_PROMPT

router = APIRouter()
client = anthropic.Anthropic()


@router.post("/query", response_model=QueryResponse)
async def query_corpus(request: QueryRequest):
    """
    Ask a GTM question. Returns a grounded answer with source citations
    drawn from the curated newsletter corpus.
    """
    results = retrieve(
        query=request.query,
        source_filter=request.source_filter,
        type_filter=request.type_filter,
        max_results=request.max_sources or 6,
    )

    context_block = build_context_block(results)
    stats = get_index_stats()

    user_prompt = QUERY_USER_PROMPT.format(
        context_block=context_block,
        query=request.query,
    )

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2048,
            system=QUERY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        answer = message.content[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")

    sources = [
        SourceCitation(
            index=i + 1,
            title=r["entry"]["title"],
            source=r["entry"]["source"],
            date=r["entry"]["date"],
        )
        for i, r in enumerate(results)
    ]

    return QueryResponse(
        query=request.query,
        answer=answer,
        sources=sources,
        corpus_entries_searched=stats.get("total", 0),
    )


@router.get("/corpus/index", response_model=CorpusIndexResponse)
async def get_corpus_index():
    """
    Return the full corpus index with metadata for all entries.
    Used by the frontend to show corpus stats and browse entries.
    """
    stats = get_index_stats()
    raw_entries = load_index()

    entries = [CorpusEntry(**e) for e in raw_entries]

    return CorpusIndexResponse(
        total=stats["total"],
        sources=stats["sources"],
        types=stats["types"],
        latest=stats.get("latest"),
        entries=entries,
    )
