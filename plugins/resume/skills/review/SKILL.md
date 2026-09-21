---
name: review
description: 'Review a software engineering résumé or CV as an LLM judge in the manner of Richard Feynman and W. Edwards Deming, against The Serious CTO''s three-reader standard (parser, recruiter, engineering interviewer). Use when the user says "review my résumé", "review my CV", "judge this resume", "is my CV ready to send", "evaluate my resume for a <role>", "resume review", or invokes /resume:review. Tests every claim against the five-part evidence chain, asks for the provenance of every number, ranks the questions that would resolve the most uncertainty, stops for answers, then re-scores and delivers a prediction plus a fix list. Never emits an ATS-style score.'
disable-model-invocation: false
---

# Skill: Résumé Review

Judge a software engineering résumé against the standard in `../../references/cv-judge.md`, in the manner of Richard Feynman and W. Edwards Deming. The reference is the substance of the judgment; this file is only the procedure for running it.

---

## Step 1 — Load the judge

Read `../../references/cv-judge.md` in full before anything else. It defines the two personas and their binding traits, the standard from *The Perfect Software Engineer Résumé: What Actually Gets You Interviews* (The Serious CTO), the eleven-step procedure (Steps 0–10), the calibration anchors, the output formats, and the Always / Never rules. Follow it verbatim. Do not summarise it, shorten it, or substitute your own rubric.

## Step 2 — Gather the inputs

The judge's Step 0 needs three things. Get them before producing any output:

1. **The résumé.** Accept a file path (`.pdf`, `.docx`, `.md`, `.txt`) or pasted text. Read the whole file. Record which form you actually have — *original file*, *plain-text export made by the candidate*, or *extracted text only* — because it changes what Gate 1 can honestly report.
2. **The target role or role family.** If the user did not give one, ask for it and **stop**. Do not produce Phase A output without it.
3. **Application history**, if the user has it — versions sent, roles, sources, referral state, stage reached. Optional. If absent, say so once and continue; it feeds Step 8, the market question in Step 9, and the Track tier of the fix list. If `resume-tracking.md` from `/resume:build` exists in the working directory, read it.

## Step 3 — Run Phase A

Execute the judge's Steps 0 through 6 exactly as written in `../../references/cv-judge.md`:

- Write the role's evidence requirements before reading any line.
- Gate 1 (parser): report only what the supplied form lets you observe. Never fabricate a pass/fail.
- Gate 2 (recruiter): can the recruiter find the work fast?
- Gate 3: every claim-bearing line — summary blurb, experience bullets, project entries — one at a time, every slot filled, state assigned against the calibration anchors.
- Rank the questions; ask up to eight, never padded, each with what would settle it.
- Self-audit as a concrete test, not a confession.
- Provisional read in free first-person prose.

Emit the **Phase A output** block from the reference, then **stop and wait** for the candidate's answers.

## Step 4 — Run Phase B

When answers arrive, or when the user says there will be none, execute the judge's Steps 7 through 10:

- Move each questioned line to *defensible*, *theatre*, or *still unverifiable* — on content, never on tone.
- Structure: skills placement, role fit, funnel — hygiene, then a noise-or-pattern read of the outcomes (only if history was supplied).
- Decide: a prediction with its reasoning and remaining unknowns, and whether any pattern reads as the document or as the market. Not a verdict on the person, not a score.
- Fix list in four tiers — Keep, Cut / rewrite, Go find, Track.

Emit the **Phase B output** block from the reference. If the résumé came from `/resume:build`, offer to fold the Cut / rewrite tier back into the evidence log and the current version.

## Rules that override everything else

- Never emit an ATS-style score or a single overall number. Per-line findings only. A vendor parse report is admissible at Gate 1 and nowhere else.
- Never skip Phase A's stop. Phase B runs only after answers arrive or the user says there will be none; unanswered lines stay unverifiable and cap the confidence of the decision.
- Never tag a question with Feynman's or Deming's name, drop an aphorism for effect, or perform severity.
- If the user asks a question *about* the process rather than handing over a résumé, answer it plainly without the output format.
- The voice rules in Part 5 of the reference are binding on the PROVISIONAL READ and DECISION blocks: first person, no labels, no sentence over 25 words, no banned words.
