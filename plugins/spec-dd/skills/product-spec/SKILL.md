---
name: product-spec
description: >
  Use when the user wants to write a "product spec" or "product specification",
  frame a "product bet", or define a falsifiable hypothesis before building.
  Also triggers on "replace the PRD", "retire the PRD", "the PRD is too long /
  too vague", "tighten this spec for an engineer or agent", "what's the bet",
  "what problem are we solving", "acceptance criteria", "success criteria",
  "kill / scale / graduate thresholds", "measurement plan", or when scoping a
  feature's problem, bet, success behaviors, and evaluation before any
  behavioral spec. Part of the spec-dd workflow; precedes /spec-dd:spec.
disable-model-invocation: false
---

# Product Spec

## Overview

A **Product Spec** is a one-page artifact built for the people who actually
consume it — engineers, designers, and AI agents — so they can ship without 12
follow-up questions. It replaces the PRD. It is **not** a PRD: no Background
section, no Goals section, no Customers section, no seven pages of feature
descriptions, no throat-clearing.

A Product Spec is exactly **four mandatory pieces, in order**, and nothing else:

1. **The problem** — who is hurting, what they do today, why now.
2. **The bet** — a falsifiable hypothesis.
3. **The success criteria** — the concrete behaviors we will see when this works.
4. **The evaluation** — how we measure it, and the kill / scale / graduate thresholds.

**Core principle:** a Product Spec earns its place only if it is falsifiable.
If nothing in it could ever prove the team *wrong*, it is a PRD wearing a new
name — start over.

This skill **interrogates the user for each of the four pieces**. You do not
write the document from assumptions, and you do not draft it until all four
pieces pass their acceptance test below.

## When to Use

- Before building a feature, when the team needs a tight, shippable spec.
- When someone hands you a long, vague PRD and wants it sharpened into a bet.
- When the request is "what are we actually betting on here?"
- As **Phase 0** of spec-dd — the Product Spec frames the problem and bet; the
  behavioral specification (`/spec-dd:spec`) then defines *what the system does*.

**Not for:** describing how a system works (that is the behavioral spec), or
producing exhaustive feature catalogs (that is the PRD you are replacing).

## Artifact

One file per feature, matching the spec-dd convention:

`docs/specs/<feature>-product-spec.md`

If no feature name is given, ask for one before writing.

## Interrogation Protocol

Interrogate the four pieces **one at a time, in order**. Do not batch all four
into one questionnaire, and do not move to the next piece until the current one
passes its acceptance test.

For each piece:

1. Ask **1–3 targeted questions**. Offer selectable options where the answer
   space is finite (who is hurting, time horizon, threshold direction) plus a
   free-text escape; use free text for narrative answers.
2. **Push back on vague answers** using that piece's *Reject when* list. Name the
   specific gap and re-ask. Do not accept an adjective where a behavior is
   required, or a wish where a number is required.
3. **Restate the captured piece** in its required form and get explicit
   confirmation before advancing.

Only after all four pass do you assemble the document, then run the **Shippable
gate** below.

For a per-piece bad-vs-good library, a full worked example, and a ready-to-use
question bank, read `references/examples.md`.

### Piece 1 — The Problem

**Must contain:** (a) a *specific* hurting party — a named role or segment, not
"users" or "everyone"; (b) what they do *today* to cope — the current workaround,
tool, or manual step; (c) *why now* — what changed that makes this urgent now and
not a year ago.

**Done when:** a stranger could point at exactly who is hurting, describe their
current workaround, and explain the trigger that makes this the moment to act.

**Reject when:**
- The sufferer is "users", "customers", "people", or "the business".
- No current behavior is described. Real pain has a coping mechanism — if you
  cannot find the workaround, you have not found the problem.
- "Why now" is "it would be nice" or "competitors have it" with no trigger.

### Piece 2 — The Bet

**Required form (fill every slot concretely):**

> If we ship **X**, then **[specific user]** will **[observable change]** within
> **[time]**, measured by **[metric]**.

- **X** — the specific thing shipped.
- **[specific user]** — the same hurting party from Piece 1, not a new vague group.
- **[observable change]** — a *behavior* visible in data, never an attitude
  ("loves it", "is satisfied", "finds it intuitive").
- **[time]** — a real window (days or weeks), not "eventually".
- **[metric]** — a named, instrumented number, with its current baseline if known.

**Done when:** it is falsifiable — you can state the result that would prove the
bet **wrong**.

**Reject when:**
- You cannot name what outcome would falsify it.
- The change is a feeling, not a behavior.
- There is no time window, or the metric is not something you can actually count.

### Piece 3 — The Success Criteria

**Must contain:** 2–5 **concrete behaviors** you would observe when this is
working — things people *do*, visible in logs, usage, or support load. Not
adjectives, not internal milestones.

**Done when:** each criterion is something you could literally watch happen.

**Reject when:**
- It is an adjective or feeling ("delightful", "fast", "engaging").
- It describes team output, not user behavior ("we shipped it", "it's live" —
  shipping is not success).
- It cannot be observed without asking someone how they feel.

### Piece 4 — The Evaluation

**Must contain:** (a) the **measurement method** — the actual instrument, query,
dashboard, or event that is the source of truth; (b) the **review window** — when
you look and decide; (c) three **thresholds, each a number with a decision
attached**:

- **Kill** — below this, stop. The bet was wrong.
- **Scale** — at or above this, invest more. The bet paid off.
- **Graduate** — the middle band: keep iterating, or promote from experiment to
  default.

**Done when:** every threshold is a concrete number tied to a decision, and a
**kill** number exists.

**Reject when:**
- No instrument is named ("we'll see how it goes", "we'll know it when we see it").
- Thresholds have no numbers.
- There is no kill condition — a bet you can never lose is not a bet.

## Shippable Gate

Before declaring the Product Spec done, apply the test that defines the artifact:

> Could an engineer or an AI agent take this and ship the feature **without 12
> follow-up questions**?

Read it back as if you were the implementer. If a slot is still vague, name the
question that would be asked and loop back to that piece. This gate is advisory —
if the user consciously accepts a gap, note it and proceed.

## Artifact Template

Keep the whole document to roughly **one page**. If it grows past a page, you are
re-writing a PRD — cut, do not expand.

```markdown
# <Feature> — Product Spec

| Field | Value |
|-------|-------|
| Owner | <name> |
| Date  | <today's date> |
| Status | Draft / Active / Killed / Scaled |

## The Problem
Who is hurting: <specific role or segment>.
What they do today: <current workaround>.
Why now: <the trigger>.

## The Bet
If we ship **<X>**, then **<specific user>** will **<observable change>**
within **<time>**, measured by **<metric>** (baseline: <current value>).

## Success Criteria
We will see these behaviors when it is working:
- <observable behavior 1>
- <observable behavior 2>
- <observable behavior 3>

## Evaluation
- **How measured:** <instrument / query / dashboard / event>.
- **Review window:** <when we look and decide>.
- **Kill:** <metric> below <number> → stop.
- **Graduate:** <metric> between <number> and <number> → keep iterating.
- **Scale:** <metric> at or above <number> → invest more.
```

## Handoff to spec-dd

When the Product Spec passes the Shippable gate, offer the next step:

- The bet and success criteria become inputs to the **behavioral specification**.
  Recommend `/spec-dd:spec <feature>` to define *what the system does*, with the
  Product Spec's metrics flowing into measurable acceptance criteria.
- The evaluation thresholds become the yardstick the eventual
  `/spec-dd:verify` and `/spec-dd:review` phases measure against.

## Common Mistakes (PRD relapse)

| PRD-ism creeping in | The Product Spec move |
|---------------------|------------------------|
| Background / Goals / Customers sections | Delete them. Four pieces only. |
| "Users want a better experience" | Name the specific person hurting and their workaround. |
| "Increase engagement" as the bet | Falsifiable bet: specific user + observable change + time + metric. |
| Success = "the feature is shipped" | Success = behaviors you can watch users perform. |
| "We'll track metrics and iterate" | Named instrument + kill / scale / graduate numbers. |
| Page after page of feature descriptions | One page. If it grows, cut. |
| A bet with no way to lose | If nothing could prove it wrong, it is not a bet — rewrite. |

## Red Flags — Stop and Re-interrogate

- You are about to write the document but skipped interrogating a piece.
- A piece "feels close enough" but fails its *Done when* test.
- The bet has no falsifying outcome.
- The evaluation has no kill threshold.
- The draft is longer than a page.

All of these mean: go back to the failing piece and interrogate it to its
required form before writing.
