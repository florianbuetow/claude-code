# resume

Build and review software engineering résumés from an evidence chain, not a
template — in the manner of Richard Feynman and W. Edwards Deming.

## Usage

```
/resume:review ~/cv.pdf for a senior platform engineer role
/resume:build
```

Both skills apply the same standard, from *The Perfect Software Engineer
Résumé: What Actually Gets You Interviews* (The Serious CTO): a résumé
must survive three readers — the parser, the recruiter, and the
engineering interviewer — and it does that only when every claim carries
context, action, constraint, result, and ownership, every number has a
baseline, a window, and a method, and the skills section sits at the
bottom as an index rather than standing in for proof.

## Skills

| Skill | Purpose |
|-------|---------|
| `resume:review` | Two-phase judge — tests every line, asks up to eight ranked questions, stops; re-scores on the answers into a prediction and a four-tier fix list |
| `resume:build` | Interactive build — harvests accomplishments one at a time into a win log with provenance, writes five-part bullets, assembles one version per role family, runs the two pre-apply tests, sets up tracking |

## The judge

`references/cv-judge.md` is the substance of both skills. It carries the
two personas with the traits each one binds — Feynman's provenance,
reconstruction, picture-it, and don't-fool-yourself; Deming's operational
definitions, common versus special cause, whose-system, drive out fear,
and cease dependence on inspection — and the resolution of the one place
they differ: Deming sets the burden of attribution, Feynman sets the
method, both bind the verdict.

Every rule in it carries a provenance tag: `[T]` transcript, `[F]` Feynman,
`[D]` Deming, `[J]` judge design.

## What it will not do

- Emit an ATS-style score, or accept one as evidence. Such tools tell you
  whether the document parses and nothing else.
- Reject a number for being a number. It asks where the number came from.
- Treat a weak résumé as a weak engineer. Unverifiable claims are
  questions, not verdicts.
- Invent a metric while building. If the candidate has no number with
  its baseline, the bullet gets a bounded outcome instead.
- Fix a bad market.

## Files the build skill writes

| File | What it is |
|------|-----------|
| `resume-evidence.md` | The win log — every accomplishment with its five parts and its provenance. The deliverable that survives. |
| `resume-<role-family>-v1.md` | One version per role family, derived from the log. |
| `resume-tracking.md` | Version, role family, source, referral state, stage reached, and the one thing changed since the last send. |
