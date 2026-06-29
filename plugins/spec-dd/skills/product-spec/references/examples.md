# Product Spec — Reference Guide

> "The PRD is a relic. Replace it with the Product Spec — a different kind of
> artifact, designed for the people who actually consume it: engineers,
> designers, and AI agents." — adapted from Gokul Rajaram

## Why the Product Spec, not the PRD

The PRD optimized for a vanished bottleneck: getting alignment from a room of
humans. Long docs and exhaustive sections were the price of that alignment. In
the agent era the bottleneck moved — it is now giving an engineer or an agent a
specification tight enough to ship from without a dozen clarifying questions.

A 10-page PRD fails that test. A one-page Product Spec with a falsifiable bet,
concrete acceptance criteria, and an evaluation plan passes it. The four pieces
are mandatory because each closes a class of question the implementer would
otherwise have to ask:

| Piece | The question it kills |
|-------|-----------------------|
| The problem | "Who is this even for, and why are we doing it now?" |
| The bet | "What does success actually look like, and by when?" |
| Success criteria | "How will I recognize it working in the wild?" |
| The evaluation | "When do we double down, keep going, or stop?" |

Anything that does not serve one of those four is throat-clearing. Cut it.

## The discipline: falsifiability

The single property that separates a Product Spec from a PRD is **falsifiability**.
A PRD can be "successful" no matter what happens because it never committed to a
losing condition. A Product Spec names, up front, the number that would prove the
team wrong. If you cannot write the kill threshold, you do not yet understand the
bet — keep interrogating.

## Piece 1 — The Problem: bad vs good

**Bad:** "Users find our onboarding confusing and we want to improve it."

**Good:** "New self-serve admins (companies of 5–20 seats, no dedicated IT)
abandon setup at the SSO step. Today they paste our SAML docs into a support
chat and wait an average of 6 hours for a human to walk them through it. Why now:
we just removed the free-tier phone support that used to absorb this, so these
tickets are now hitting a queue with a 1-day SLA and churn at trial-end spiked."

**Why:** the bad version names no specific sufferer, no current behavior, and no
trigger. The good version names exactly who hurts, what they literally do today
(paste docs, wait 6h), and what changed (support removed, churn spiked).

## Piece 2 — The Bet: bad vs good

**Bad:** "If we redesign onboarding, engagement will improve and users will be
happier."

Unfalsifiable: "engagement" and "happier" are not instrumented, there is no
specific user, no time window, and no outcome that could prove it wrong.

**Good:** "If we ship a guided SSO setup wizard, then new self-serve admins will
complete SSO configuration without opening a support ticket, within their first
session, measured by the SSO-setup completion rate (baseline: 41%)."

**Falsifying outcome (state it explicitly):** if completion rate does not rise
above 41% within four weeks of rollout, the bet is wrong.

**Why:** the good version fills every slot — X (guided wizard), specific user
(self-serve admins), observable change (complete setup without a ticket), time
(first session / four-week readout), metric (completion rate with a baseline) —
and names what would falsify it.

## Piece 3 — Success Criteria: bad vs good

**Bad:**
- Onboarding feels smooth and intuitive.
- Users are more confident.
- The new flow is modern and delightful.

Every line is an adjective or a feeling — none can be observed without asking
someone how they feel.

**Good:**
- An admin reaches "SSO connected" in a single session without leaving the app.
- SSO-related support tickets from trial accounts drop week over week.
- Admins who finish the wizard invite at least one teammate the same day.

Each is a behavior visible in product analytics or the support queue.

## Piece 4 — The Evaluation: bad vs good

**Bad:** "We'll track completion and engagement metrics in the dashboard and
iterate based on what we see."

No named instrument, no review window, no numbers, no kill condition.

**Good:**
- **How measured:** `sso_setup_completed` event divided by `sso_setup_started`
  event, segmented to trial accounts, in the Onboarding Mixpanel board.
- **Review window:** 4 weeks after 100% rollout.
- **Kill:** completion rate below 50% → revert the wizard, the bet was wrong.
- **Graduate:** 50–70% → keep iterating on the failing steps; stay in experiment.
- **Scale:** at or above 70% → make the wizard the default path and remove the
  legacy docs-and-ticket flow.

## Full worked example

```markdown
# Guided SSO Setup — Product Spec

| Field | Value |
|-------|-------|
| Owner | A. Rivera |
| Date  | 2026-06-29 |
| Status | Draft |

## The Problem
Who is hurting: new self-serve admins at 5–20 seat companies with no dedicated IT.
What they do today: paste our SAML docs into support chat and wait ~6h for a human.
Why now: we removed free-tier phone support; these tickets now sit in a 1-day-SLA
queue and trial-end churn spiked.

## The Bet
If we ship a guided SSO setup wizard, then new self-serve admins will complete SSO
configuration without opening a support ticket, within their first session,
measured by the SSO-setup completion rate (baseline: 41%).

## Success Criteria
We will see these behaviors when it is working:
- An admin reaches "SSO connected" in one session without leaving the app.
- SSO support tickets from trial accounts drop week over week.
- Admins who finish the wizard invite at least one teammate the same day.

## Evaluation
- **How measured:** sso_setup_completed / sso_setup_started for trial accounts,
  Onboarding Mixpanel board.
- **Review window:** 4 weeks after 100% rollout.
- **Kill:** completion rate below 50% → revert the wizard.
- **Graduate:** 50–70% → keep iterating on failing steps.
- **Scale:** 70%+ → make the wizard the default, retire the legacy docs flow.
```

## Interrogation question bank

Use these as starting prompts; adapt to the user's domain. Offer selectable
options where noted, always with a free-text escape.

**Problem**
- "Who specifically is hurting? Give me a role and a segment, not 'users'."
- "What do they do *today* to cope with this? Walk me through the workaround."
- "Why is now the moment — what changed?" (options: new constraint / new
  competitor / cost spike / regulation / scale tipping point / other)

**Bet**
- "Fill this in: *If we ship ___, then ___ will ___ within ___, measured by ___.*"
- "What number, if we saw it, would mean we were wrong?"
- "Which metric, and what is its value today?"
- "How long until we should expect the change?" (options: 1 week / 2 weeks /
  1 month / 1 quarter / other)

**Success criteria**
- "What would you *see people do* if this were working — in the logs, the
  product, or the support queue?"
- "Give me a behavior, not a feeling. What action would they take?"

**Evaluation**
- "What is the source of truth — which event, query, or dashboard?"
- "When do we look and decide?"
- "Below what number do we kill it?" / "Above what number do we scale it?" /
  "What is the in-between band where we keep iterating?"
