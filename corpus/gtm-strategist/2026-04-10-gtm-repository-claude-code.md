---
slug: 2026-04-10-gtm-repository-claude-code
source: gtm-strategist
date: 2026-04-10
title: "The GTM Repository for Claude Code"
type: framework
audience: GTM leader, RevOps leader, Marketing Ops, Sales Ops
tags: [gtm-repository, claude-code, institutional-knowledge, signal-library, icp, skills, workflows, context-architecture]
concepts: [GTM repository, CLAUDE.md, signal decay, signal combinations, ICP evolution log, institutional memory, skills architecture, output archive, context layers]
url: https://knowledge.gtmstrategist.com/p/the-gtm-repository-for-claude-code
---

# The GTM Repository for Claude Code

**Source:** GTM Strategist · Maja Voje, Nico Druelle, Karl Rafidimanana · April 10, 2026

## Core Concept

A GTM repository is a set of markdown files in a git repo that captures institutional GTM knowledge in structured, queryable form. Claude Code reads these files automatically at session start — eliminating the need to rebuild context repeatedly. The repository doesn't write GTM strategy; it amplifies existing knowledge and makes it persist beyond individual contributors.

## Five-Layer Architecture

### 1. CLAUDE.md — The Brain
Automatically read by Claude at every session start. Contains ICP summary, top signals, positioning statement, team info, current priorities. Must be scannable in two minutes — deep details live in context files.

### 2. Context — Institutional Knowledge

- **context/profile.md** — Company overview, product, deal profile by segment, reference customers
- **context/icp-definition.md** — Tier definitions with employee range, technographic signals, organizational signals, anti-ICP exclusions, qualification framework, ICP evolution log
- **context/signal-library.md** — Signals with detection methods, point values, decay curves, message hooks
- **context/positioning.md** — Value pillars with proof points, messaging matrix by persona, "what not to say"
- **context/competitor-radar.md** — Battlecards: "we win when X, we lose when Y, exact language for [Competitor] objections"
- **context/personas/** — Individual files per buyer persona: decision role, metrics, buying process, attention triggers, outreach hooks

### 3. Skills — Repeatable Execution
- **Account Research** — Full intel brief: company snapshot, stakeholder map, signal score, competitive context, recommended first-line hook
- **Signal to Sequence** — Complete campaign: trigger logic, audience, sequence copy, measurement targets
- **ICP Scoring** — Score single account or batch 500+ accounts against ICP definition
- **Weekly Update** — Identifies stale sections, drafts updates, flags what needs human confirmation

### 4. Workflows — Operational Processes
- **enrichment.md** — Data waterfall, source sequence, quality thresholds, email deliverability infrastructure
- **signal-routing.md** — Decision tree: customer suppression, opportunity routing, 45-day cooldown, tier assignment
- **campaign-build.md** — Audience definition, approval requirements, copy review, QA checks

### 5. Outputs — The Archive
Every research brief, campaign brief, and sequence stored in outputs/. Creates feedback loop connecting past thinking to outcomes.

## Critical Concepts

### Signal Decay
Signals lose value over time. Example: "Series B announced in last 60 days, detected via Crunchbase webhook into Clay, worth 30 points, decay to 15 points after 60 days." Account scoring must incorporate time-weighted signal values.

### Signal Combinations
Two signals together score higher than their individual sum. Example: Series B + new RevOps hire = 80-point account with combination bonus — indicates both budget existence and active rebuilding simultaneously.

### ICP Evolution Log
Every ICP change is documented with rationale and date. Turns ICP definition from a static document into a learning system.

## Real-World Patterns

1. **Signal-driven ICP revision** — VP Eng targeting revealed "Platform Engineering" / "Developer Experience" team creation converted at 4x. Org signal outperformed company-type signal.
2. **Competitive battlecard staleness** — Lost 3 deals to same competitor using 14-month-old battlecard. Fresh battlecard won 2 of next 4.
3. **New hire onboarding** — RevOps hire accessed entire institutional context on day one: ICP evolution log, signal performance data, campaign archive. Strategic conversations replaced knowledge transfer.

## Maintenance
- Weekly (5 min): Update CLAUDE.md current priorities
- Post-campaign (15 min): Add results — reply rates, meeting rates, converting signals
- Post-win/loss (30 min): Update competitor battlecard
- Quarterly (1 hr): Review ICP definition, add evolution log entry

## RevOps + Toolkit Implications

The five-layer architecture maps directly to what a RevOps toolkit should generate:
- CRM hygiene tools (dedup, standardize, health) → clean data that feeds the signal library
- Account Scoring → implements signal decay + signal combinations, not just static ICP match
- GTM Knowledge Builder → generates the context layer files from CRM data
- The output archive pattern should inform how toolkit results are stored and fed back into future runs
