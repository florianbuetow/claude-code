Origin: plugin-original

# Output Conventions — Generated arc42 Documentation Contract

This file is the authoritative contract for what the `section-author` agent emits into a
target project. It is plugin-original (it describes the plugin's own output format, not arc42
content), so it carries no `Source:` line. Every format below is normative: the generator and
any downstream checker MUST agree on it.

The governing rule is **never fabricate**. Every factual statement in generated documentation
either traces to a recorded fact, is explicitly marked as an inference, or is replaced by a
typed GAP flag. There is no fourth option.

---

## 1. Target layout

The generator writes into `docs/arc42/` in the *target* project:

```
docs/arc42/
  index.md                         (TOC + the 3 standout keywords)
  01-introduction-and-goals.md … 12-glossary.md
  _evidence.md                     (fact records)
  _gaps.md                         (aggregated GAP flags)
```

- `index.md` — table of contents linking the 12 section files, plus a short note on the three
  standout arc42 keywords (`lean`, `thorough`, `essential`) and which stance this run took.
- `NN-*.md` — one file per arc42 section, `01-introduction-and-goals.md` through
  `12-glossary.md`.
- `_evidence.md` — the fact base: one record per extracted fact (schema in §3). Section files
  reference these records by id; they are never duplicated inline.
- `_gaps.md` — every typed GAP flag emitted anywhere, aggregated so a human can resolve them in
  one pass.

---

## 2. File-level YAML front-matter

Every `NN-*.md` section file begins with this front-matter block:

```yaml
---
arc42_section: 5
title: Building Block View
source_commit: <sha>
generated_at: <iso8601>
arc42_kb_version: <semver of the bundled knowledge base>
upstream_hash: <hash of consumed upstream section files>
---
```

- `arc42_section` — the integer section number (1–12).
- `title` — the canonical arc42 section title.
- `source_commit` — the git commit SHA of the target repository the documentation was derived
  from. Pins the documentation to a precise code state.
- `generated_at` — ISO-8601 timestamp of generation.
- `arc42_kb_version` — semver of the bundled knowledge base under
  `skills/arc42-framework/references/` (tracks the plugin version; `0.1.0` for this release).
- `upstream_hash` — a hash over the consumed upstream section/reference files, so a reader can
  tell whether the knowledge base changed between two generations.

None of these may be omitted or guessed. If a value is unavailable (e.g. the repo is not a git
checkout, so there is no `source_commit`), emit a GAP rather than inventing a placeholder.

---

## 3. Evidence fact-record schema

`_evidence.md` holds a list of fact records, one list item each:

```yaml
- id: F-042
  fact: "Service 'billing' exposes an HTTP API"
  value: "POST /charges, GET /charges/{id}"
  source: "services/billing/router.go:14-39"
  extraction_method: manifest-parse | import-graph | config-read | naming-inference
  confidence: high | medium | low
```

- `id` — stable `F-NNN` identifier, referenced from section files.
- `fact` — the claim in one sentence.
- `value` — the concrete extracted value (signatures, routes, names, counts).
- `source` — a precise `path:line-range` (or `path` for whole-file evidence) in the target repo.
- `extraction_method` — how the fact was obtained:
  - `manifest-parse` — read from a package/build/workspace manifest.
  - `import-graph` — derived from import/dependency edges.
  - `config-read` — read from a configuration / IaC / deployment descriptor.
  - `naming-inference` — inferred from directory/file/symbol naming conventions (weakest).
- `confidence` — `high | medium | low`, aligned with the confidence rubric in
  `diagram-conventions.md`.

Records are append-only within a run; section files cite ids, never copy the values.

---

## 4. Per-sub-section metadata block

Each arc42 sub-section (e.g. 5.1, 5.2) carries one HTML-comment metadata block immediately under
its heading:

```
<!-- arc42-meta section:5.1 provenance:code-derived confidence:high fact_refs:F-042,F-051 gaps:[] -->
```

- `section` — the sub-section number.
- `provenance` — one of:
  `code-derived | inferred | gap-human | gap-no-evidence | human-provided`.
- `confidence` — `high | medium | low`.
- `fact_refs` — comma-separated `F-NNN` ids backing the sub-section (or empty).
- `gaps` — list of open GAP ids for this sub-section (`[]` when none).

`provenance` values:
- `code-derived` — built directly from recorded facts.
- `inferred` — reasoned from facts/conventions; not directly stated by the code.
- `gap-human` — content withheld pending human input (paired with a `GAP:human-input` flag).
- `gap-no-evidence` — code-derivable in principle, but no evidence was found
  (paired with a `GAP:no-evidence` flag).
- `human-provided` — supplied by a person, not generated.

---

## 5. Per-claim anchor

Each factual claim in prose carries an inline anchor naming the facts that back it:

```
<!-- claim:5.1.3 facts:F-042,F-051 -->
```

- `claim` — a dotted id locating the claim within its sub-section.
- `facts` — the `F-NNN` ids that substantiate exactly this claim.

A factual claim without backing facts is not allowed; replace it with a GAP flag.

---

## 6. Typed GAP flags

When evidence is missing, emit a typed GAP flag instead of fabricating. Two types:

```
<!-- GAP:human-input <question> -->
```
Needs a person — the answer is a business/quality/intent decision the code cannot reveal
(e.g. "Which of these quality goals is the top priority?").

```
<!-- GAP:no-evidence <what was sought> -->
```
Code-derivable in principle, but nothing was found (e.g. "No deployment descriptor or IaC found
for the production environment").

Every GAP flag emitted in a section file is also aggregated into `_gaps.md`. GAP flags are the
only sanctioned way to represent unknowns — never paper over a gap with a plausible-sounding
guess.

---

## 7. Diagrams

The generator emits **Mermaid** diagrams where the code gives high-confidence structure, a
Mermaid diagram with an inline caveat where structure is inferred, and a labeled placeholder
where no faithful Mermaid representation exists. See `diagram-conventions.md` for the
section-to-diagram mapping, the confidence rubric, and the two placeholder-only cases (UML
deployment stereotypes in §7, swimlane activity diagrams in §6). arc42's own raster figures are
never embedded in generated output.
