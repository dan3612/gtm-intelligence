---
slug: 2026-06-11-custom-account-scoring-ai-model
source: default
date: 2026-06-11
title: "Custom Account Scoring AI Model"
type: technical
audience: RevOps leader, GTM leader, VP of Sales, Growth Engineer
tags: [account-scoring, signal-inference, icp, pipeline-prioritization, ai-gtm, crm-infrastructure, fit-timing, buying-signals]
concepts: [Fit x Timing framework, P1-P4 priority tiers, signal inference, job description analysis, unified signal layer, scoring infrastructure, TAM-wide scoring, labeled training data, gradient boosting, data ownership]
url: https://www.default.com/post/custom-account-scoring-ai-model
---

# Custom Account Scoring AI Model

**Source:** Default · Nandika Jhunjhunwala, Founding Growth Engineer · 2026

## Core Argument

Sales teams face thousands of accounts weekly with no clear way to rank them. Buying signals exist across multiple platforms but remain isolated and incomparable. The solution isn't more tools — it's a unified scoring infrastructure that consolidates signals into a single ranked priority list and writes it back to the CRM as a system of record.

> "These signals live in isolation, each in its own tool and format, with its own idea of what an account even is."

Built by one engineer in one month. Under $0.75 per account at scale (5,800+ accounts).

## The Framework: Fit × Timing

**Two-axis scoring model:**
- **Fit**: Long-term buyer suitability — employee count, vertical, funding stage, tech stack
- **Timing**: Active buying signals showing immediate purchase readiness — hiring patterns, funding events, website visits, news

**Four priority tiers:**
- **P1**: Fit ≥50 + Timing ≥22 → call now
- **P2**: Fit ≥50 + Timing 16–21 → active nurture
- **P3**: Lower fit or weak timing → automated sequences
- **P4**: Low fit + low timing → deprioritize

Any account with Fit ≥80 gets bumped up a tier automatically.

## Signal Inference with AI

Rather than simple data lookups, the system runs Claude Sonnet inference on job descriptions to extract structured signals:
- **ops-buildout**: Multiple similar roles posted quarterly = someone is building a function
- **pain-language**: Specific problems called out in job copy = active pain awareness
- **ai-initiative**: AI roadmap or transformation references = open to new infrastructure

Each inferred signal links back to the exact source text — transparency that drives adoption by skeptical sales teams.

## Technical Architecture

**Four-stage pipeline:**
1. **Inputs**: CSV imports, CRM sync, web app submissions, direct interactions
2. **Enrichment**: Firmographic/technographic data → JD inference → news inference
3. **Storage**: Postgres with quarterly history snapshots and full joinability
4. **Output**: CRM custom fields, dialer context, dashboard scorecard

**Why not Clay?** Clay excels at one-time enrichment. It can't scale to TAM-wide continuous scoring with audit logs, history snapshots, and complete joinability. You need infrastructure you own, not workflow software you rent.

> "Own your data before you buy agents. Agents built on niche data infrastructure outperform generic tools."

## Sales Integration

The system meets teams where they already work:
- **In CRM**: Custom tier/fit/timing fields on account records, P1/P2 focused books of business
- **In dialer**: Account and contact summaries pre-populated with signals and JD context
- **In dashboard**: Full scorecard showing every contributing rule and underlying source

## Results

- Outreach efficiency: 2x reduction in touches to book a qualified meeting (640 → 275)
- Pipeline concentration: P1/P2 share of pipeline 25% → 40%
- Opportunity conversion: doubled for teams working model rankings
- Scale: 8,200+ unified signals, 24,000+ inferred job descriptions, 300K+ scoring records

## The Path to ML

Every outreach outcome (calls, emails, bookings) is stored with its associated score — creating labeled training data. The roadmap: heuristic weights today → gradient-boosted model tomorrow, where real outcomes continuously refine future scoring rather than static rules.

## Core Principle

Successful GTM systems start with unified data, strong context, and clear purpose. The data layer is foundational. Context enables judgment. And context requires labeled, joinable, history-bearing records — not a stack of disconnected enrichment tools.
