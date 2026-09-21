---
name: build
description: 'Build a software engineering résumé interactively from an evidence chain, not a template. Use when the user says "build my résumé", "write my CV", "help me create a resume", "rewrite my résumé from scratch", "build the perfect resume", "turn my experience into résumé bullets", "start a win log", or invokes /resume:build. Harvests accomplishments one at a time into a win log with provenance, writes five-part bullets (context, action, constraint, result, ownership), assembles a few coherent versions by role family, runs the two pre-apply tests with the /resume:review judge, and sets up tracking. Never invents a metric.'
disable-model-invocation: false
---

# Skill: Build a Résumé

"The fix isn't a perfect template. It's an evidence chain. Start with real work." This skill builds the chain first and the document second, and it asks the questions the `/resume:review` judge will ask — before the judge does.

Read `../../references/cv-judge.md` before starting. You need three things from it: **Part 2** (the standard every line must meet), **Part 1** (how to ask — picture it, by what method, whose system, drive out fear), and **Part 4** (the calibration anchors, so you recognise theatre, unverifiable, and defensible while writing, not after).

---

## How to run the conversation

- **One question at a time.** Wait for the answer. Never send a questionnaire.
- **Drive out fear.** "That was mostly the team," "I don't remember the number," and "I don't know" are good answers. They stop a bad bullet from being written. Say so early and mean it.
- **Never invent.** If the candidate does not have a number, do not estimate one. If they cannot name the constraint, the bullet does not get a constraint. Ask; do not fill in.
- **Every entry carries provenance.** Where the fact came from — a dashboard, an incident report, a design doc, memory — is recorded next to the fact.
- **Write files as you go.** The evidence log is the deliverable that survives; the résumé is derived from it and can be regenerated.

## Step 1 — Aim

Ask, in this order, one at a time:

1. **Which role family or families are you aiming at?** Platform (reliability, incidents, infrastructure, data, cloud) or product (user outcomes, APIs, trade-offs, delivery, collaboration) — or something else, named. This decides which evidence gets surfaced. Do not continue without it.
2. **Do you have an existing résumé?** If yes, read it. It is *raw material* for Step 2 — a list of things to ask about — never the template. Do not copy a line from it into the new version until it has been through Step 3.
3. **Do you have application history?** Versions sent, roles, sources, referral state, stage reached. Optional; it seeds Step 6.

## Step 2 — Harvest the evidence into a win log

Create `resume-evidence.md` in the working directory. Then walk the candidate's history **employer by employer, most recent first**, and within each, **accomplishment by accomplishment**.

Open each employer with: *"What is the one thing you did there that you would want an engineer to ask you about for five minutes?"* Then, for that accomplishment, ask for the five parts in this order, one question each, using the judge's moves:

| Part | Ask | Judge's move |
|---|---|---|
| Context | Where was this — which system, which team, what was at stake? Walk me through the day it mattered. | Picture it |
| Action | What did *you* do, as against the team? What would not have happened if you had been on vacation that quarter? | Whose system |
| Constraint | What made it hard? What ruled out the obvious fix? | Define the term |
| Result | What is different now? If there is a number: what was the baseline, over what window, measured how, by whom? | By what method |
| Ownership | What did you own — the change, the rollout, the decision — and what did you contribute to or watch? | Whose system |

Then ask for the **artifact**: *"Is there a dashboard, incident report, design doc, launch review, or project note that shows this? Name it, even if you can't share it."* Record it as the provenance line.

Write the entry to `resume-evidence.md` immediately:

```markdown
## <Employer> — <Title> — <dates>

### <one-line accomplishment name>
- Context: …
- Action: …
- Constraint: …
- Result: … (baseline / window / method / who measured — or "bounded outcome: …")
- Ownership: …
- Provenance: <artifact name, or "memory">
- Role family: platform | product | both
```

Keep going until the candidate says an employer is exhausted, then move to the next. Aim for depth on the last two or three employers; earlier ones can carry one entry each. Treat side projects and open-source work as employers.

**Apply the metrics rule as you write.** A real number goes in only when baseline, window, and method are all present. Otherwise write the bounded outcome — *removed a manual handoff*, *reduced the failure class*, *made on-call diagnosis possible*, *enabled another team to ship* — and give it an operational definition (which handoff, between whom, gone since when).

**Apply the five-minute rule as you write.** For every noun, verb, number, and acronym in an entry, ask yourself whether the candidate just explained it in the conversation. If they could not, it does not go in.

## Step 3 — Write the bullets

From each evidence entry, write **one bullet** in the shape of the defensible anchors in Part 4 of the reference: context, action, constraint, result, ownership, in whatever order reads best, in the candidate's own words where possible. Show each bullet to the candidate with the three escalating questions an engineer would ask about it, and ask: *"Could you answer all three?"* If not, rewrite or drop.

Rules while writing:

- Nouns are not accomplishments. *Kubernetes, Kafka, platform, React, Python* appear only inside a sentence that says what was done with them.
- No résumé theatre: no logos, skill bars, hidden text, keywords lifted from a posting, or a skill wall under each employer.
- A bounded outcome beats an undefendable number. Never the reverse.
- Verbs over nominalisations: *cut*, not *achieved a reduction in*.

Append the finished bullet to its evidence entry under `- Bullet: …`.

## Step 4 — Assemble a few coherent versions

"Don't rebuild the whole damn thing for every posting. Select the right evidence." Make **one version per role family** the candidate named in Step 1, and no more:

- Select the bullets whose `Role family` matches. Platform versions surface reliability, incidents, infrastructure, data, cloud. Product versions surface user outcomes, APIs, trade-offs, delivery, collaboration.
- Layout, top to bottom: name and contact in body text; a short blurb that states the role family and the strongest piece of evidence; experience with the selected bullets; **skills once, at the bottom, as an index** — never repeated under employers.
- Plain structure the parser can read: real headings, real bullets, single column, dates and employers unambiguous, no tables, text boxes, or graphics.

Write each to `resume-<role-family>-v1.md`. The candidate converts to PDF with whatever tool they use; the markdown is the source of truth.

## Step 5 — Run the two tests before applying

1. **Parser test.** Tell the candidate to export the final document to plain text and open it in a parser preview, then check with them: reading order, name, contact, employers, dates, headings, bullets. If they hand you the plain-text export, check it yourself.
2. **Hostile human test.** Run `/resume:review` on the version, with the role family from Step 1 and `resume-evidence.md` as the artifact source. Take Phase A's questions back to the candidate; fold the answers into the evidence log; rewrite any line that came back *unverifiable* or *theatre*; then run Phase B. Repeat until the read has nothing left to ask that the evidence log cannot answer.

## Step 6 — Set up tracking

Create `resume-tracking.md`:

```markdown
| Date | Version | Role family | Company | Source | Referral | Stage reached | One thing changed since last |
|---|---|---|---|---|---|---|---|
```

Explain the discipline in three lines: one rejection is noise, a pattern is signal; change one thing at a time between versions, and write down what it was; keep every dated variant. Copy any history from Step 1 into the table.

## Step 7 — Close

Tell the candidate three things, plainly:

- The evidence log is the thing to keep. Append to it as work finishes — that is the win log, and the next résumé writes itself from it.
- A résumé cannot fix a bad market: arbitrary hiring, discrimination, location constraints, a role someone already has. It can only stop failing the handoff for avoidable reasons.
- If the evidence log is thin, the font is not the problem. Go do work worth writing down, and write it down.

## Never

- Never estimate, round up, or infer a number the candidate did not give with its provenance.
- Never write a bullet the candidate could not defend in the conversation you just had.
- Never put skills anywhere but the bottom, once.
- Never produce more versions than role families.
- Never copy a line from an existing résumé without taking it through Step 2 first.
- Never skip Step 5. A version that has not been through `/resume:review` is a draft.
