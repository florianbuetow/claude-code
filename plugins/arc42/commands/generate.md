---
description: Generate a complete arc42 architecture documentation set for a target repository. Runs evidence-scout (Phase A), all 12 section-author agents in dependency-ordered parallel waves (Phase B), and consistency-checker followed by index and GAP aggregation (Phase C). Pass an optional sub-path to scope a monorepo component.
argument-hint: "[target-path]"
---

# /arc42:generate

You are the **orchestrator** for the arc42 documentation generator. Follow every phase in order. Do not skip steps. Do not fabricate content — all documentation is produced by the subagents you dispatch.

---

## Setup — resolve paths

Before dispatching anything, establish these variables. Reference them by name throughout.

1. **`target-repo-root`** — the absolute path to the target repository. Use the current working directory (`pwd`) unless the user's session is already positioned inside a git repository root; in that case use `git rev-parse --show-toplevel`.

2. **`target-path`** — the optional sub-path argument from `$ARGUMENTS`. If `$ARGUMENTS` is empty or whitespace, `target-path` is unset. If set, it must be a path relative to `target-repo-root`.

3. **`arc42-kb-root`** — the absolute path to `skills/arc42-framework/references/` inside the arc42 plugin installation. Resolve it from the canonical Claude Code plugin env var:
   ```
   arc42-kb-root="${CLAUDE_PLUGIN_ROOT}/skills/arc42-framework/references"
   ```
   **Fail fast:** if `CLAUDE_PLUGIN_ROOT` is unset or empty, stop immediately and print:
   ```
   ERROR: CLAUDE_PLUGIN_ROOT is not set — cannot locate arc42 knowledge base. Ensure the arc42 plugin is installed and CLAUDE_PLUGIN_ROOT is provided by the Claude Code runtime.
   ```
   If `arc42-kb-root` does not exist as a directory after resolution, stop immediately and print:
   ```
   ERROR: arc42 knowledge base not found at <arc42-kb-root>. Re-install the arc42 plugin.
   ```

4. **`docs-root`** — `<target-repo-root>/docs/arc42`

5. **`force`** — set to `true` if `$ARGUMENTS` contains `--force`, otherwise `false`.

6. **`head-sha`** — `git -C <target-repo-root> rev-parse HEAD`. If this fails, note that idempotency checks will be skipped.

Load the **arc42-framework** skill now.

---

## Phase A — Evidence collection

Dispatch the **evidence-scout** agent with these inputs:

- `repo-root`: `<target-repo-root>`
- `target-path`: `<target-path>` (omit if unset)
- `arc42-kb-root`: `<arc42-kb-root>`

The agent writes `<target-repo-root>/docs/arc42/_evidence.md` and reports back with a `DONE: N fact records …` line or an `ERROR:` line.

**Fail-fast gate:** If the agent reports an `ERROR:`, stop immediately. Print the error and exit. Do not proceed to Phase B. A run without an evidence base is invalid.

After Phase A succeeds, note `<evidence-path>` = `<target-repo-root>/docs/arc42/_evidence.md`.

---

## Phase B — Section authoring (dependency-ordered waves)

Sections are generated in three waves. **Within a wave, all section-author dispatches run in parallel.** Waves execute sequentially — Wave 2 starts only when Wave 1 is fully settled.

> **Ordering note:** The wave order is code-derivable-first (Wave 1 = §3, §5, §7, §12), not a
> strict topological sort of the `Depends on` edges in the section specs. Cross-section
> consistency is enforced **post-hoc** by the consistency-checker in Phase C — in particular
> the §3↔§5 interface symmetry (`interfaces-match` rule). Other `Depends on` edges are
> best-effort: a section may be dispatched before all of its declared upstream sections exist,
> and that is by design. Do not reorder the waves to satisfy declared deps — the post-hoc
> checker is the correct enforcement point.

### Idempotency check

Before dispatching any section-author, check whether that section should be skipped:

1. Does `<docs-root>/<NN-slug>.md` already exist?
2. If yes, read its `source_commit` and `upstream_hash` front-matter fields.
3. If `source_commit` == `<head-sha>` AND `upstream_hash` matches the SHA-256 of the concatenated upstream files for this section (computed with `cat <upstream-files…> | sha256sum | awk '{print $1}'`), then skip this section **unless `force` is `true`**.
4. Track skipped sections in a list to report at the end.

### Section dispatch parameters

For every section-author dispatch, inject these named inputs in the agent prompt:

- **`spec-path`**: absolute path to the section spec file, e.g. `<arc42-kb-root>/sections/05-building-block-view.md`
- **`evidence-path`**: `<evidence-path>`
- **`upstream-paths`**: space-separated absolute paths to already-generated upstream section files (from prior waves only, limited to the deps listed in the spec's `Depends on` field, and only those that were not skipped or failed). If none, omit.
- **`output-path`**: `<docs-root>/<NN-slug>.md`
- **`repo-root`**: `<target-repo-root>`
- **`arc42-kb-root`**: `<arc42-kb-root>`

**Override — GAP aggregation:** Include this directive verbatim in every section-author dispatch prompt:

> **ORCHESTRATOR OVERRIDE — skip Step 7:** Do NOT write to `_gaps.md`. Emit GAP flags inline in your section file only. The orchestrator aggregates all GAP flags centrally after Phase C to avoid parallel-append races.

### Wave 1 — §3, §5, §7, §12 (parallel)

No prior wave output exists. All four sections receive empty `upstream-paths`.

| Section | Spec file | Output file |
|---------|-----------|-------------|
| §3 Context and Scope | `sections/03-context-and-scope.md` | `03-context-and-scope.md` |
| §5 Building Block View | `sections/05-building-block-view.md` | `05-building-block-view.md` |
| §7 Deployment View | `sections/07-deployment-view.md` | `07-deployment-view.md` |
| §12 Glossary | `sections/12-glossary.md` | `12-glossary.md` |

Dispatch all four section-author agents in parallel. Collect results.

**Wave 1 failure handling:** If any Wave 1 section-author reports an `ERROR:`, mark that section as `FAILED`. Record the error detail. Dependent sections in later waves will be `SKIPPED:upstream-failed` if all of their available upstream files come from failed sections. Preserve all sections that did succeed.

### Wave 2 — §6, §8, §4, §9, §2 (parallel)

Prior-wave outputs available: §3, §5, §7, §12 (those that succeeded; failed sections are absent).

Inject upstream-paths as follows (use only paths for sections that are present and not failed):

| Section | Spec file | Output file | Upstream deps from prior waves |
|---------|-----------|-------------|-------------------------------|
| §6 Runtime View | `sections/06-runtime-view.md` | `06-runtime-view.md` | §5, §3 |
| §8 Crosscutting Concepts | `sections/08-crosscutting-concepts.md` | `08-crosscutting-concepts.md` | §5 |
| §4 Solution Strategy | `sections/04-solution-strategy.md` | `04-solution-strategy.md` | §3 |
| §9 Architecture Decisions | `sections/09-architecture-decisions.md` | `09-architecture-decisions.md` | (none from Wave 1) |
| §2 Constraints | `sections/02-constraints.md` | `02-constraints.md` | (none from Wave 1) |

Note: §4 depends on §1, §2, §3 per the spec, but §1 and §2 are not yet generated; inject only §3. §8 depends on §5 and §4, but §4 is in this same wave and not yet complete; inject only §5. §9 depends on §1 and §4, neither available; upstream-paths is empty.

Dispatch all five section-author agents in parallel. Collect results. Apply the same failure-handling rule as Wave 1.

### Wave 3 — §1, §10, §11 (parallel)

Prior-wave outputs available: §3, §5, §7, §12 (Wave 1) + §6, §8, §4, §9, §2 (Wave 2) — those that succeeded.

Inject upstream-paths as follows:

| Section | Spec file | Output file | Upstream deps from prior waves |
|---------|-----------|-------------|-------------------------------|
| §1 Introduction and Goals | `sections/01-introduction-and-goals.md` | `01-introduction-and-goals.md` | (none) |
| §10 Quality | `sections/10-quality.md` | `10-quality.md` | §4 |
| §11 Risks and Technical Debt | `sections/11-risks-and-technical-debt.md` | `11-risks-and-technical-debt.md` | §4, §8, §9 |

Note: §10 depends on §1.2 and §4; §1 is in this same wave (not yet complete); inject only §4. §11 depends on §1, §4, §8, §9; §1 is in this same wave; inject §4, §8, §9.

Dispatch all three section-author agents in parallel. Collect results.

### Phase B summary

After all three waves complete, print a table:

```
Phase B complete:
  Succeeded: <list of NN slugs>
  Skipped (idempotent): <list>
  Skipped (upstream-failed): <list with typed reason>
  Failed: <list with one-line error each>
```

If ALL 12 sections failed, stop. If at least some sections succeeded, continue to Phase C.

---

## Phase C — Consistency check, assembly, and GAP aggregation

### C.1 — Consistency check

Dispatch the **consistency-checker** agent with:

- `docs-root`: `<docs-root>`
- `arc42-kb-root`: `<arc42-kb-root>`

The agent returns a `CONSISTENCY CHECK REPORT` to the orchestrator. Print it inline. It does not write any file.

### C.2 — Assemble `docs/arc42/index.md`

Write `<docs-root>/index.md`. Include:

1. **Title:** `# arc42 Architecture Documentation`
2. **Generation metadata:** `source_commit`, `generated_at` (ISO-8601 now), `arc42_kb_version` (read from `<arc42-kb-root>/kb-version.txt`).
3. **Stance note:** a one-sentence note on which arc42 stance this run took — `lean` (short, essential only), `thorough` (full detail), or `essential` (balanced). Determine the stance by counting how many GAP flags are present across all section files: ≤5 = thorough, 6–20 = essential, >20 = lean.
4. **Table of contents:** a Markdown table linking to each section file that was generated, with columns: Section number | Title | Status (generated / skipped-idempotent / skipped-upstream-failed / failed).
5. **Consistency findings:** summary line from the consistency-checker report (violations count or "all checks passed").

### C.3 — Aggregate GAP flags into `_gaps.md`

Scan every successfully generated section file in `<docs-root>/` (files matching `[0-9][0-9]-*.md`). For each file:

1. Use Grep to find all `<!-- GAP:human-input … -->` and `<!-- GAP:no-evidence … -->` comment lines.
2. Note the section file they came from and the sub-section id from the nearest preceding `<!-- arc42-meta section:… -->` comment.

Write `<docs-root>/_gaps.md` (overwrite any existing file — the orchestrator is the sole writer of this file):

```markdown
---
generated_at: <ISO-8601>
source_commit: <head-sha>
total_gaps: <N>
---

# Arc42 GAP Registry

<!-- This file is generated by /arc42:generate. Run /arc42:fill-gaps to resolve gaps interactively. -->
<!-- Do not edit manually — re-running generate overwrites this file. -->

## Human-input gaps (<count>)

### <NN-slug> — <sub-section id>

- **Type**: human-input
- **Question**: <text from the GAP flag>
- **Section file**: <relative path from docs-root, e.g. 03-context-and-scope.md>
- **Arc42-meta**: section:<sub-section-id> (for re-tagging provenance after resolution)

...

## No-evidence gaps (<count>)

### <NN-slug> — <sub-section id>

- **Type**: no-evidence
- **Sought**: <text from the GAP flag>
- **Section file**: <relative path>
- **Arc42-meta**: section:<sub-section-id>

...
```

If zero GAP flags were found, write the file with `total_gaps: 0` and an empty registry body.

### C.4 — Inline gap interview (optional)

After writing `_gaps.md`, if there are any human-input GAP flags, ask the user:

> `<N> human-input gaps were identified. Would you like to fill them interactively now? (yes / no / later)`

If the user answers **yes**: proceed with the inline interview (same flow as `/arc42:fill-gaps` — see that command's recipe).

If the user answers **no** or **later**: print:

> Run `/arc42:fill-gaps` at any time to walk through the gaps and supply human input.

---

## Final report

Print a one-block summary:

```
/arc42:generate complete
  Target:    <target-repo-root> [<target-path> scope]
  Commit:    <head-sha>
  Sections:  <N> generated, <S> skipped (idempotent), <U> skipped (upstream-failed), <F> failed
  GAP flags: <H> human-input, <E> no-evidence
  Docs:      <docs-root>/
  Index:     <docs-root>/index.md
  Gaps:      <docs-root>/_gaps.md
  Consistency: <violations count or "all checks passed">
```
