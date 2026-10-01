# ADR 0001: the shape of one run

**Filled by:** session 10, for the choice you measured in session 8 (chain,
loop or graph, and the model calls each one cost). The four fields are the
ones `ch10-e2` reads.

- Status: accepted
- Date: 2026-10-01

## Context

One question must cost at most one model call plus one corrective retry, then a
refusal. Measured on the FakeLLM lane: the chain in `agent.py` costs exactly 1
model call per supported question and 0 for refusals; the session-8 loop draft
cost 2 model calls on the same question with no score change on `grade`.

## Decision (`decision`)

We keep the chain in agent.py: retrieve top_k=3, one model call, verify citations, refuse otherwise.

## Options considered (`options_considered`)

1. Keep the chain in agent.py with one model call and one corrective retry.
2. Use the session-8 loop with capped reflection and up to 3 model calls per question.

## Why not the other option (`why_not`)

The loop spent 3 model calls per grounded question on the fake lane and still scored 3/10, so the extra calls bought latency without moving citation_recall or claim_support.

## What would reverse it (`reverses_it`)

When a grounded question needs more than 2 model calls in 10 of the golden cases, or p95 answer latency stays over 2000 ms for 15 minutes, we switch to the loop and re-measure.
