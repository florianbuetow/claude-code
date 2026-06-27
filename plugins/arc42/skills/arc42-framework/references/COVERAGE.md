Origin: plugin-original

# COVERAGE — arc42 Corpus Derivation Manifest

This manifest accounts for **every file** in the arc42 corpus snapshot and maps each
one to the derived reference file(s) that consume it, or marks it `dropped:` with a
reason. It is the input to `plugins/arc42/tests/check_corpus_contract.py`, which enforces
100% coverage accounting (spec §8): a corpus file absent from this manifest is a hard
contract violation.

## Corpus snapshot

- Source corpus: the crawled arc42 framework knowledge base (root `index.md`, 12 section
  indexes, 144 per-section tips, `keywords.md`, and an `images/` tree).
- Path form: keys below are **corpus-relative** (e.g. `05-building-block-view/index.md`),
  matching the paths the checker enumerates when `--corpus` points at the corpus root
  (`.../crawl-arc42-doc/data/output`). The same corpus-relative form is used in the
  `Source:` lines of the derived reference files, so both resolve against the same root.

## File census (216 files)

| Group | Count | Destination |
|-------|------:|-------------|
| Root `index.md` | 1 | `expected-topics.md` (standout-keyword note) |
| `keywords.md` | 1 | `keyword-tags.md` |
| Section indexes (`NN-*/index.md`) | 12 | `sections/NN-*.md` + `expected-topics.md` |
| Tips (`NN-*/tips/*.md`) | 144 | `lint-checklist.md` + `keyword-tags.md` (12 cross-section tips also `consistency-rules.md`; 3 diagram tips also `diagram-conventions.md`) |
| Images (`images/**`) | 58 | dropped (generator emits Mermaid, not arc42's raster figures) |

## Assets

`assets/` is intentionally empty: the generator emits **Mermaid** diagrams it derives from
the target codebase, not arc42's own illustrative raster images. No reference file embeds a
corpus image, so none are bundled. All 58 images are therefore `dropped:` below.

---

## Root corpus files

- `index.md` -> `expected-topics.md` (root-index standout-keyword note: lean / thorough / essential)
- `keywords.md` -> `keyword-tags.md`

## Section indexes (12) -> per-section authoring specs + topic catalog

- `01-introduction-and-goals/index.md` -> `sections/01-introduction-and-goals.md` + `expected-topics.md`
- `02-constraints/index.md` -> `sections/02-constraints.md` + `expected-topics.md`
- `03-context-and-scope/index.md` -> `sections/03-context-and-scope.md` + `expected-topics.md`
- `04-solution-strategy/index.md` -> `sections/04-solution-strategy.md` + `expected-topics.md`
- `05-building-block-view/index.md` -> `sections/05-building-block-view.md` + `expected-topics.md`
- `06-runtime-view/index.md` -> `sections/06-runtime-view.md` + `expected-topics.md`
- `07-deployment-view/index.md` -> `sections/07-deployment-view.md` + `expected-topics.md`
- `08-crosscutting-concepts/index.md` -> `sections/08-crosscutting-concepts.md` + `expected-topics.md`
- `09-architecture-decisions/index.md` -> `sections/09-architecture-decisions.md` + `expected-topics.md`
- `10-quality/index.md` -> `sections/10-quality.md` + `expected-topics.md`
- `11-risks-and-technical-debt/index.md` -> `sections/11-risks-and-technical-debt.md` + `expected-topics.md`
- `12-glossary/index.md` -> `sections/12-glossary.md` + `expected-topics.md`

## Tips (144) -> lint checklist + keyword taxonomy (cross-section rules + diagram conventions where noted)

- `01-introduction-and-goals/tips/1-1.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-7.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-8.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-9.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-10.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-11.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-12.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-13.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-14.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-15.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-16.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-17.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-18.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-19.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-20.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-21.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-22.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-23.md` -> `lint-checklist.md` + `keyword-tags.md`
- `01-introduction-and-goals/tips/1-24.md` -> `lint-checklist.md` + `keyword-tags.md`
- `02-constraints/tips/2-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `02-constraints/tips/2-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `02-constraints/tips/2-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `02-constraints/tips/2-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `02-constraints/tips/2-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-5.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-7.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-8.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-9.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-10.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-11.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-12.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-13.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-14.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-15.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-16.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-17.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-18.md` -> `lint-checklist.md` + `keyword-tags.md`
- `03-context-and-scope/tips/3-19.md` -> `lint-checklist.md` + `keyword-tags.md`
- `04-solution-strategy/tips/4-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `04-solution-strategy/tips/4-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `04-solution-strategy/tips/4-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `04-solution-strategy/tips/4-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `04-solution-strategy/tips/4-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `04-solution-strategy/tips/4-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-3.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-4.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-7.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-8.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-9.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-10.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-11.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-12.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-13.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-14.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-15.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-16.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-17.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-18.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-19.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-20.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-21.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-22.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-23.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-24.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-25.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-26.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-27.md` -> `lint-checklist.md` + `keyword-tags.md`
- `05-building-block-view/tips/5-28.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-2.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-7.md` -> `lint-checklist.md` + `keyword-tags.md` + `diagram-conventions.md`
- `06-runtime-view/tips/6-8.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-9.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-10.md` -> `lint-checklist.md` + `keyword-tags.md`
- `06-runtime-view/tips/6-11.md` -> `lint-checklist.md` + `keyword-tags.md` + `diagram-conventions.md`
- `07-deployment-view/tips/7-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-6.md` -> `lint-checklist.md` + `keyword-tags.md` + `diagram-conventions.md`
- `07-deployment-view/tips/7-7.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-8.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-9.md` -> `lint-checklist.md` + `keyword-tags.md`
- `07-deployment-view/tips/7-10.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-3.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-7.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-8.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-9.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-10.md` -> `lint-checklist.md` + `keyword-tags.md`
- `08-crosscutting-concepts/tips/8-11.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-7.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-8.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-9.md` -> `lint-checklist.md` + `keyword-tags.md`
- `09-architecture-decisions/tips/9-10.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-7.md` -> `lint-checklist.md` + `keyword-tags.md`
- `10-quality/tips/10-8.md` -> `lint-checklist.md` + `keyword-tags.md`
- `11-risks-and-technical-debt/tips/11-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `11-risks-and-technical-debt/tips/11-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `11-risks-and-technical-debt/tips/11-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `11-risks-and-technical-debt/tips/11-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `11-risks-and-technical-debt/tips/11-5.md` -> `lint-checklist.md` + `keyword-tags.md`
- `11-risks-and-technical-debt/tips/11-6.md` -> `lint-checklist.md` + `keyword-tags.md`
- `12-glossary/tips/12-1.md` -> `lint-checklist.md` + `keyword-tags.md`
- `12-glossary/tips/12-2.md` -> `lint-checklist.md` + `keyword-tags.md`
- `12-glossary/tips/12-3.md` -> `lint-checklist.md` + `keyword-tags.md`
- `12-glossary/tips/12-4.md` -> `lint-checklist.md` + `keyword-tags.md`
- `12-glossary/tips/12-5.md` -> `lint-checklist.md` + `consistency-rules.md` + `keyword-tags.md`
- `12-glossary/tips/12-6.md` -> `lint-checklist.md` + `keyword-tags.md`

## Images (58) -> dropped

- `images/01-ISO-25010-EN.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/01-eGPM.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/01-quality-scenarios-schematic.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/01-requirements-cluster.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/01-simple-activity.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/01-stakeholder-prio-EN.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-big-context.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-business-context-with-technical-info.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-abstractions.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-compact.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-different-dependencies.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-extensive.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-for-mapping.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-user-product-service.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-with-ports.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-with-quality-goals.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-context-with-risk.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-overly-detailed-context.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-simple-context.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-technical-context-automotive.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/03-technical-context-info-sys.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-building-block-hierarchy.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-building-block-hierarchy.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-concepts-instead.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-infrastructure-in-building-block-view.jpg` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-interface-simple-variant.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-mapping-code-to-blocks.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-mutual-refinement-graphical.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-mutual-refinement.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-refine-only-few-blocks.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-similar-building-blocks.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-simple-mapping.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-third-party-element.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-whitebox-level-1-consistent.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/05-whitebox-with-other-info.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/06-activity-with-partition.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/06-activity-with-swimlane.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/06-long-and-mostly-boring.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/06-mixed-abstraction-levels.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/06-plantuml-example.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/06-short-and-interesting.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/06-textual-sequence.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/07-deployment-diagram.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/07-deployment-hierarchy.jpg` -> dropped: not needed for generation (generator emits Mermaid)
- `images/07-deployment-options.webp` -> dropped: not needed for generation (generator emits Mermaid)
- `images/07-deployment-overview.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/07-infrastructure-with-symbols.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/07-level-1-for-schematic-sequence.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/07-schematic-sequence.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/08-hospital-domain-EN.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/1-2-iso-25010-topics-en.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/10-quality-tree-example.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/10-quality-tree-mindmap-example.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/10-quality/arc42-system-qualities-overview.svg` -> dropped: not needed for generation (generator emits Mermaid)
- `images/12-graphical-glossary.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/8-concepts/08-concepts-EN.drawio.png` -> dropped: not needed for generation (generator emits Mermaid)
- `images/contact-icon.png` -> dropped: site UI chrome (FAQ / contact icon), not arc42 architecture content
- `images/faq-icon.png` -> dropped: site UI chrome (FAQ / contact icon), not arc42 architecture content
