---
slug: 2026-05-01-content-engineering-ai-gtm-system-claude-code
source: gtm-strategist
date: 2026-05-01
title: "Content Engineering: How to Build a Content System in Claude Code"
type: framework
audience: GTM leader, CMO, Marketing Ops, RevOps leader, Content Strategist
tags: [content-engineering, ai-content, claude-code, aeo, gtm-system, sales-intelligence, knowledge-architecture]
concepts: [sophisticated slop, knowledge foundation, context scoping, signal-to-output workflow, GTM maturity model, call analyzer, content pipeline, ICP architecture]
url: https://knowledge.gtmstrategist.com/p/content-engineering-how-to-build-content-system-in-claude-code
---

# Content Engineering: How to Build a Content System in Claude Code

**Source:** GTM Strategist · Maja Voje & Benjamin Gibert (CMO, Base Operations) · May 1, 2026

## Core Thesis

90% of AI content output quality comes from what you feed the system — not from the sophistication of the agents. Most companies are building complex pipelines around shallow context. The differentiator is a rich, competitor-proof knowledge foundation that AI agents draw from selectively.

The practical test: "Could a competitor copy-paste this output and change the logo?" If yes, the context is the problem, not the AI.

## The "Sophisticated Slop" Problem

Teams invest in multi-agent pipelines while neglecting the knowledge layer that makes those pipelines produce differentiated output. The fix isn't more complex workflows — it's creating specific, structured context that reflects real customer intelligence competitors can't easily replicate.

## Knowledge Foundation Architecture

Five modular markdown files form the base layer:
1. **icp.md** — Firmographics, buying committee roles, in-market signals
2. **personas.md** — Buying psychology, pain points, decision criteria
3. **positioning.md** — Strategic narrative, differentiators with proof points
4. **voice-guide.md** — Tone rules, prohibited terms, editorial standards
5. **competitive-landscape.md** — Competitor mapping and positioning gaps

**Cascade principle:** Edit the master knowledgebase once; all derived modules update automatically through a sync skill.

**Differentiator layer:** Customer intelligence extracted from sales calls — exact quotes, speaker context, pain triggers, and a customer language lexicon capturing how buyers actually speak vs. marketing terminology.

## One Input → Multiple Outputs

A single sales call transcript → structured JSON intelligence → feeds four parallel systems:
- SEO/AEO articles
- LinkedIn thought leadership (persona-specific framing)
- ABM personalization (objection mapping)
- Product strategy (JTBD pattern analysis across calls)

## Six-Stage Content Pipeline

1. **Research & Intelligence** — Call Analyzer processes transcripts; Research Agent produces detailed briefs (keywords, pain points, value props, originality requirements)
2. **Enrichment & Outline** — Evidence maps to sections; output is writer-ready outline with word counts and proof points
3. ⚠️ **HUMAN REVIEW GATE** — Strategic approval before execution
4. **Writer** — Composes from approved outline only; "Feature → Benefit → Proof" patterns
5. **Editor** — Enforces voice consistency; edit diffs fed back to improve future agent performance
6. **Internal Linker** — Distributes priority URLs based on word count and content type
7. **Publisher** — Converts markdown to HTML, generates FAQ schema, creates Webflow CMS drafts

## Context Scoping Principle

Each agent loads only the context files it needs. The writer never sees the full knowledgebase — only the approved outline. Tight context scoping: better output, fewer tokens, reduced irrelevant information pull.

## GTM Maturity Model

- **Level 0:** Copy-paste into AI chat
- **Level 1:** ICP and positioning exist as readable files
- **Level 2:** AI drafts following your strategy
- **Level 3:** Signal-to-output workflows for each GTM motion
- **Level 4:** Performance data updates strategy in continuous cycles

## Tool Integrations (MCP)

Firecrawl (SERP analysis), HubSpot (deal data → content prioritization), Clay (company enrichment), Lemlist (customer insights → outbound), Webflow (CMS), Analytics feedback loop.

## Results (Base Operations)

- Organic traffic doubled in 3-4 months
- AEO citations increased 500-600%
- Ranked #1 on Google for core terms within weeks
- Inbound increasingly driving demo calls and pipeline

## RevOps Implications

The knowledge foundation architecture (icp.md, personas.md, positioning.md) is directly applicable to RevOps tooling. CRM data is the raw material for this layer — clean, standardized, well-scored records feed better AI outputs. This creates a direct link between CRM hygiene tools and GTM content quality: bad data → sophisticated slop.
