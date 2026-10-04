# The Skill Standard

A skill is a correction you got tired of making.

Every skill in this plugin judges, rewrites, or writes a skill against the
five rules below. Each rule ends in the checks that apply it. Cite rules
by number (R1–R5) and checks by id (R1.a, R2.b, …) in every finding.

---

## R1 — Target a correction you keep sending back

A skill earns its place by fixing a recurring failure, not by describing a
task you do often. If Claude already does the task right the first time,
the skill only costs tokens.

Aim at the **specific step** that fails, not the whole process. A skill
that walks the entire process end to end keeps the most common failure
alive: **asset rush** — producing the artifact before the thinking is
done, like a student raising a hand before checking the answer.

Checks:

- **R1.a — Named correction.** Can you state, in one sentence, the output
  the user kept sending back and what they changed? If not, the skill has
  no target.
- **R1.b — Failing step.** Does the skill concentrate on the step that
  failed, or spread evenly over steps Claude already gets right?
- **R1.c — Asset rush.** Does the skill let Claude produce the artifact
  before the step that needed guidance is finished? Look for a gate:
  "confirm X before writing Y".
- **R1.d — Default behavior.** Would Claude, with no skill loaded,
  already produce an acceptable result? Then the skill is a candidate for
  deletion.

---

## R2 — Use leading words

A **leading word** is an established term that recruits the model's
training priors: one word stands in for a body of practice. A made-up
word recruits no priors — you pay in definition tokens what a pre-trained
word gives free.

Before explaining a method, ask: is there an established framework or
term for this? See `leading-words.md` for a working list.

Checks:

- **R2.a — Explanation with a name.** Is a passage explaining, step by
  step, something an established term already names (refactor, steelman,
  premortem, BLUF, design tree, red-green-refactor)? Replace the passage
  with the term.
- **R2.b — Coined terms.** Does the skill invent a word and then define
  it? Swap it for an established word, or keep it only if no established
  word exists and the definition is one line.
- **R2.c — Weak verbs and adverbs.** Can one strong, precise word replace
  a weak phrase ("keep asking until satisfied" → "grill relentlessly")?

---

## R3 — Keep it small; invoke it deliberately

Length is not evidence of usefulness. A seven-line skill with the right
words can outperform two pages. Choose the right word for the model at
the right moment.

**Model invocation** is the model calling a skill without being asked.
Prefer user invocation (`disable-model-invocation: true` in the
frontmatter) for skills whose timing the user should own. It costs a
little cognitive load — remembering the skill exists, which practice
erases — and removes recurring context load (every model-invocable
description sits in context every turn). It also removes a class of
errors: did the right skill run, why did it run now, why this workflow
instead of that one.

Keep model invocation for skills that must fire on a reliable trigger the
user would otherwise forget (safety rails, file-type handlers).

Checks:

- **R3.a — Size.** Report line and word count of the body. Flag every
  section whose removal would not change behavior (see R5).
- **R3.b — Invocation mode.** State the current mode and recommend one,
  with the reason: who should decide when this runs?
- **R3.c — Description cost.** For a model-invocable skill, is the
  `description` as short as its trigger allows? Every word is paid on
  every turn.

---

## R4 — Grow it from real use

The test is simple: **if you no longer have to send the result back, the
skill is working.**

Each instruction should trace to a failure someone observed. Instructions
that anticipate problems nobody has seen are speculation; they dilute the
ones that matter. Examples of instructions that earned their place:

| Observed problem | One-sentence fix |
|---|---|
| Conversations dragged. | "Give your recommended answer." |
| Several questions at once overwhelmed the user. | "Ask one question at a time." |
| The agent skipped ahead and started building. | "Do not enact the plan until I confirm." |
| The agent began grilling itself. | "Split facts from decisions." |

The revision loop, roughly weekly:

1. Use the skill on real work, not constructed test cases.
2. Review the period's corrections — the times you sent output back.
3. Add a one-sentence fix for each recurring one.
4. Use the revised skill again. Add nothing for a problem you have not
   seen.

Checks:

- **R4.a — Traceability.** For each instruction, can you name the failure
  it prevents? Mark instructions with no plausible observed failure as
  speculative.
- **R4.b — Fix shape.** Is each fix one sentence, stated as the desired
  behavior?
- **R4.c — Evidence.** When session history is available, does it show
  the user still correcting the behavior this skill targets? Then the
  skill is not yet working (see `corrections.md`).

---

## R5 — Delete instructions that do no work

An instruction is a **no-op** when removing it does not change the output.
"Be thorough" is the archetype. For every sentence ask: would Claude have
done that anyway? If so, it is decoration with a token cost.

Two pruning methods:

| Method | Procedure |
|---|---|
| **Precise** | Remove one suspected no-op, run the skill again, compare the output. |
| **Aggressive** | Scan the whole skill for no-op language, delete it all, then watch the next real uses. |

Cleanup rules:

- **Delete whole sentences.** Trimming words from a no-op leaves a
  shorter no-op.
- **State the desired behavior.** Prohibitions name the unwanted
  behavior and pull it into focus — "don't think of an elephant". Write
  what to do instead.
- **Check for overlap.** Condense or remove skills that duplicate one
  another.
- **Compose before creating.** When existing skills already produce the
  behavior together, compose them instead of writing a new skill.

Checks:

- **R5.a — No-op sentences.** Quote each sentence Claude would follow
  anyway (be thorough, be careful, use best practices, think step by
  step, make sure to, it is important that).
- **R5.b — Negative phrasing.** Quote each "don't / never / avoid"
  instruction that could be rewritten as the desired behavior, with the
  rewrite. Keep a prohibition only when the forbidden act is specific,
  dangerous, and has no positive phrasing (e.g. "never force-push").
- **R5.c — Overlap.** Name any other installed skill that covers the same
  behavior, and whether to merge, compose, or delete.

---

## Ownership

Write skills you understand, built on failures you observed. A copied
skill encodes someone else's decisions and corrections; copying the file
does not copy the understanding. When critiquing or improving a skill you
did not write, ask the owner which corrections it was meant to stop.
