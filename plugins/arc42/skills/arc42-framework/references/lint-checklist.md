Source: 01-introduction-and-goals/tips/, 02-constraints/tips/, 03-context-and-scope/tips/, 04-solution-strategy/tips/, 05-building-block-view/tips/, 06-runtime-view/tips/, 07-deployment-view/tips/, 08-crosscutting-concepts/tips/, 09-architecture-decisions/tips/, 10-quality/tips/, 11-risks-and-technical-debt/tips/, 12-glossary/tips/

Derived, reworded checklist — one rule per arc42 tip. Every rule is rephrased; see the source tip for the original rationale. `machine` = mechanically verifiable (counts, presence, structural match); `advisory` = requires human judgment.

<!-- §01 Introduction and Goals — 24 tips -->
- **T01-1** [`machine`] (§01): §1.1 requirements summary must fit on roughly one page; longer requirement details go in referenced documents.
- **T01-2** [`advisory`] (§01): Limit §1.1 to a handful of essential use cases; omit fine-grained individual requirements.
- **T01-3** [`advisory`] (§01): Make business objectives explicit in §1.1 — they belong in the documentation, not only in a project contract.
- **T01-4** [`advisory`] (§01): Group related use cases and functions into named clusters; describe the clusters, not every individual item.
- **T01-5** [`advisory`] (§01): Assign stable, unique IDs to requirements so they can be cited unambiguously in architecture decisions.
- **T01-6** [`advisory`] (§01): Use activity diagrams when you need to express concurrency, alternative paths, or exception flows in functional requirements.
- **T01-7** [`advisory`] (§01): Prefer BPMN over UML activity diagrams when stakeholders are business-oriented and unfamiliar with UML notation.
- **T01-8** [`advisory`] (§01): Use numbered lists to describe simple sequential processes when concurrency and branching are absent.
- **T01-9** [`advisory`] (§01): Express functional flows in a semi-formal textual notation (e.g., PlantUML) to gain version-control support alongside rendered diagrams.
- **T01-10** [`advisory`] (§01): Describe functional requirements as exemplary business-process models when the primary goal is stakeholder communication.
- **T01-11** [`advisory`] (§01): Always make quality requirements explicit; never leave quality attributes implied in a requirements document.
- **T01-12** [`advisory`] (§01): Express each quality requirement as a concrete scenario — usage, change, or failure type — with measurable acceptance criteria.
- **T01-13** [`advisory`] (§01): When stakeholders cannot supply quality requirements, draft educated-guess assumptions as scenarios and validate them explicitly.
- **T01-14** [`advisory`] (§01): Use the ISO-25010 quality hierarchy as a completeness checklist when eliciting quality requirements with stakeholders.
- **T01-15** [`advisory`] (§01): Use real-world quality scenario examples to help stakeholders articulate concrete quality goals.
- **T01-16** [`machine`] (§01): §1.2 must contain no more than the top 3–5 quality goals; move every remaining goal to §10.
- **T01-17** [`advisory`] (§01): Cross-reference the §4 solution-strategy table from §1.2 rather than repeating quality-to-decision mappings in both places.
- **T01-18** [`advisory`] (§01): Capture only the highest-priority quality requirements in §1; place all detailed scenarios in §10.
- **T01-19** [`advisory`] (§01): Identify every party who develops, operates, funds, audits, or is impacted by the system before finalizing the stakeholder list.
- **T01-20** [`advisory`] (§01): Ask each stakeholder what documentation content and form they need before writing the architecture document.
- **T01-21** [`advisory`] (§01): Capture stakeholders in a table that records role, contact, and their specific architectural documentation expectations.
- **T01-22** [`advisory`] (§01): Cross-reference an externally maintained stakeholder list rather than duplicating it — only if it already covers architecture-specific expectations.
- **T01-23** [`advisory`] (§01): When time is short, classify stakeholders by interest vs. influence to prioritize communication effort.
- **T01-24** [`advisory`] (§01): Use the open-source Q42 quality model as a starting point when stakeholders struggle to articulate quality requirements.

<!-- §02 Constraints — 5 tips -->
- **T02-1** [`advisory`] (§02): Discover constraints by examining what restrictions already govern other systems within the same organization.
- **T02-2** [`advisory`] (§02): Document the practical cost and effort impact of each constraint; negotiate any that impose unreasonable burden with stakeholders.
- **T02-3** [`advisory`] (§02): Record every organizational constraint (time, budget, process mandate, legal obligation) so the team can plan around it early.
- **T02-4** [`advisory`] (§02): Record every design and development constraint (mandated technology, hardware, frameworks) alongside organizational ones.
- **T02-5** [`advisory`] (§02): Categorize constraints by type (technical, organizational, political, convention) to make them easier to assign and address.

<!-- §03 Context and Scope — 19 tips -->
- **T03-1** [`advisory`] (§03): Draw an explicit system boundary that shows what is inside versus outside and names all external interfaces.
- **T03-2** [`advisory`] (§03): Represent the context as a diagram with the system drawn as a single black box in the center surrounded by external actors.
- **T03-3** [`advisory`] (§03): Pair every context diagram with a table that gives each external neighbor a short ID and a brief explanation.
- **T03-4** [`advisory`] (§03): Mark interfaces that carry availability, cost, security, or volatility risks visually in the context diagram.
- **T03-5** [`machine`] (§03): All external interfaces and neighbor systems must be present in the context; omit internal implementation detail from this view.
- **T03-6** [`advisory`] (§03): Reduce context-diagram clutter by grouping functionally equivalent external systems into a single named category.
- **T03-7** [`advisory`] (§03): Aggregate external neighbors sharing common data, timing, technology, or organizational affiliation into explicit clusters with stated criteria.
- **T03-8** [`advisory`] (§03): Use UML port symbols to represent clusters of external neighbors and show which internal component connects to each port.
- **T03-9** [`machine`] (§03): Every external neighbor must appear in the context diagram; reduce complexity through abstraction, not by omitting neighbors.
- **T03-10** [`advisory`] (§03): Add a technical context view alongside the business context whenever hardware, protocols, or infrastructure are architecturally significant.
- **T03-11** [`advisory`] (§03): Use data-flow arrows (direction of data movement) in the business context when communicating with non-UML stakeholders.
- **T03-12** [`advisory`] (§03): Show non-data dependencies (temporal, spatial, hardware, indirect) when they affect quality requirements.
- **T03-13** [`advisory`] (§03): Include transitive dependencies only when they are essential for understanding; keep the context economical otherwise.
- **T03-14** [`advisory`] (§03): Annotate external interfaces that carry SLAs, safety levels, or special quality obligations directly in the context diagram.
- **T03-15** [`advisory`] (§03): Draw a technical context diagram whenever hardware, processors, buses, or transmission channels are central to system behavior.
- **T03-16** [`advisory`] (§03): Label every communication protocol or physical channel explicitly in the technical context.
- **T03-17** [`advisory`] (§03): Combine business and technical context in a single diagram when the efficiency gain outweighs the added complexity.
- **T03-18** [`advisory`] (§03): Provide an explicit mapping table from domain-level interface names to their technical realizations (protocols, channels).
- **T03-19** [`advisory`] (§03): Defer infrastructure and protocol details to §7 when the business context alone meets all stakeholder needs.

<!-- §04 Solution Strategy — 6 tips -->
- **T04-1** [`advisory`] (§04): Summarize the solution strategy as a compact keyword list or short bullet overview, not a detailed narrative.
- **T04-2** [`advisory`] (§04): Present solution approaches in a four-column table: quality goal, scenario, solution approach, and link to details.
- **T04-3** [`advisory`] (§04): Tie each solution approach to the specific quality scenario it addresses to make quality-to-decision tracing explicit.
- **T04-4** [`advisory`] (§04): Link to §5, §6, or §8 for full details rather than restating content already documented in those sections.
- **T04-5** [`advisory`] (§04): Add entries to the solution strategy only after an approach has been validated; avoid speculative up-front decisions.
- **T04-6** [`advisory`] (§04): Record the reasoning behind each strategic decision explicitly — the "why" is more valuable than the "what."

<!-- §05 Building Block View — 28 tips -->
- **T05-1** [`advisory`] (§05): Apply consistent whitebox templates (structure + rationale) and blackbox templates (responsibility + interfaces) at every hierarchy level.
- **T05-2** [`advisory`] (§05): Structure the building block view as a hierarchy: context diagram → level-1 whitebox → deeper levels only where justified.
- **T05-3** [`machine`] (§05): Level-1 of the building block view must always be present, even when all other documentation is reduced to a minimum.
- **T05-4** [`machine`] (§05): Every external interface in §3 context must appear in the §5 level-1 diagram, and no new external interfaces may emerge below level-1.
- **T05-5** [`advisory`] (§05): Give every blackbox a one-to-two-sentence responsibility statement describing the "what," never the internal "how."
- **T05-6** [`advisory`] (§05): Do not expose a blackbox's internal workings unless the consumer genuinely needs that knowledge to use it.
- **T05-7** [`advisory`] (§05): Use a minimal tabular blackbox template (purpose, interface) for lean but consistent documentation of blackboxes.
- **T05-8** [`advisory`] (§05): Justify every whitebox decomposition: state why those sub-blocks exist and why those dependencies are there.
- **T05-9** [`advisory`] (§05): Convey the required internal behavior of a whitebox through pseudo-code, activity diagrams, or state machines rather than fully specifying its internals.
- **T05-10** [`advisory`] (§05): Factor shared structural patterns used in multiple building blocks into a §8 crosscutting concept rather than repeating the pattern.
- **T05-11** [`advisory`] (§05): Refine building blocks below level-1 only when specific stakeholders genuinely need that additional depth.
- **T05-12** [`advisory`] (§05): Every building block must trace to a direct parent one level above; do not skip levels in the hierarchy.
- **T05-13** [`advisory`] (§05): Explain which source-code artifacts (packages, modules, files) implement each architectural building block.
- **T05-14** [`advisory`] (§05): Point to the repository root or top-level directory per building block; do not enumerate every individual source file.
- **T05-15** [`advisory`] (§05): Mirror building-block names in the directory structure so the mapping from code to architecture is immediately self-evident.
- **T05-16** [`advisory`] (§05): Map level-1 building blocks to the primary modularization construct of your programming language wherever feasible.
- **T05-17** [`advisory`] (§05): Apply cohesion as the dominant criterion when deciding which elements belong inside the same building block.
- **T05-18** [`machine`] (§05): Every line of system-specific source code must have a corresponding building block in §5; no code may be structurally orphaned.
- **T05-19** [`advisory`] (§05): Include third-party libraries or products in the building block view only when their presence is required for architectural understanding.
- **T05-20** [`machine`] (§05): Third-party building blocks must be visually distinguished from custom-built ones through stereotype, color, or naming convention.
- **T05-21** [`advisory`] (§05): Describe internal interfaces with minimal detail; rely on source code for the full interface specification.
- **T05-22** [`advisory`] (§05): Use unit tests as living documentation for interfaces — they make prerequisites and expected outcomes explicit without duplication.
- **T05-23** [`advisory`] (§05): Model multi-step interface handshakes as runtime scenarios in §6 and link to them from the relevant building-block descriptions.
- **T05-24** [`advisory`] (§05): Annotate level-1 building blocks with supplementary metadata (language, team, status) using color or stereotypes when it aids communication.
- **T05-25** [`advisory`] (§05): Refine sibling building blocks into a shared whitebox only when they are tightly coupled or structurally similar enough to justify it.
- **T05-26** [`advisory`] (§05): In a mutually refined whitebox, make the origin of each contained element explicit via naming convention or graphical marker.
- **T05-27** [`advisory`] (§05): Refine only a selective subset of building blocks; leave the rest as opaque blackboxes to control documentation effort.
- **T05-28** [`advisory`] (§05): Explain the dominant architectural principle or style when it is more informative than detailing individual building blocks — but always keep a level-1 view.

<!-- §06 Runtime View — 11 tips -->
- **T06-1** [`advisory`] (§06): Assign every activity in a runtime scenario to a specific building block from §5 using swimlanes or sequence-diagram lifelines.
- **T06-2** [`machine`] (§06): Keep the documented set of runtime scenarios to a small representative number (typically 1–3); discard scenarios that served only design purposes.
- **T06-3** [`advisory`] (§06): Default to schematic scenarios referencing level-1 building blocks; reserve instance-level detail for cases where a stakeholder explicitly requires it.
- **T06-4** [`advisory`] (§06): Document instance-level runtime scenarios only when a named stakeholder has a specific, justified need for that precision.
- **T06-5** [`advisory`] (§06): Treat runtime scenarios primarily as design tools for clarifying building-block responsibilities; minimize what survives into the delivered documentation.
- **T06-6** [`advisory`] (§06): Show only the risky, complex, or architecturally interesting excerpt of a scenario; cut boring or repetitive parts.
- **T06-7** [`advisory`] (§06): Use UML activity diagrams with swimlanes to map activities to building blocks when sequence diagrams are not preferred.
- **T06-8** [`advisory`] (§06): Use partitioned activity diagrams as an alternative to swimlanes for grouping activities by building block or thread.
- **T06-9** [`advisory`] (§06): Use a textual DSL (e.g., PlantUML) for runtime scenarios to enable version control and reduce graphical-tool maintenance overhead.
- **T06-10** [`advisory`] (§06): Mix building blocks from different abstraction levels in one scenario to hide unnecessary internal detail while keeping important interactions visible.
- **T06-11** [`advisory`] (§06): Use UML sequence diagrams to make per-building-block responsibility distribution immediately visible in runtime scenarios.

<!-- §07 Deployment View — 10 tips -->
- **T07-1** [`advisory`] (§07): Document the full physical and virtual infrastructure — nodes, channels, firewalls, storage — on which the system executes.
- **T07-2** [`advisory`] (§07): Explain the reasoning behind hardware selection decisions, not just the resulting topology.
- **T07-3** [`advisory`] (§07): Document all deployment environments (DEV, CI, TEST, PROD) and the significant differences between them.
- **T07-4** [`advisory`] (§07): Organize the deployment view hierarchically when the infrastructure is distributed, layered, or heterogeneous.
- **T07-5** [`advisory`] (§07): Explicitly document how software artifacts map to hardware nodes, including any variant deployment configurations.
- **T07-6** [`advisory`] (§07): Use UML deployment diagrams to show hardware topology and software placement in a single, integrated view.
- **T07-7** [`advisory`] (§07): Replace deployment diagrams with a simple table when a graphical view would add effort without improving understanding.
- **T07-8** [`advisory`] (§07): Explain any node that has unusual technical characteristics or special significance for the system's operation.
- **T07-9** [`advisory`] (§07): List every operational setup step (OS config, accounts, middleware, network rules, secrets) needed to run the system; automate them via scripts.
- **T07-10** [`advisory`] (§07): Delegate infrastructure documentation to infrastructure owners; include in §7 only what is needed to understand software architecture decisions.

<!-- §08 Crosscutting Concepts — 11 tips -->
- **T08-1** [`advisory`] (§08): Document crosscutting concepts because they carry the fundamental solution approaches and are the foundation of architectural consistency.
- **T08-2** [`advisory`] (§08): Use one consistent term for crosscutting things throughout the document; recognize that teams may call them aspects, principles, rules, or tactics.
- **T08-3** [`machine`] (§08): Select only the concepts that genuinely apply to the system from the arc42 catalog; elaborate only the highest-priority ones in detail.
- **T08-4** [`advisory`] (§08): Explain each concept through a concrete implementation example or real code snippet, not abstract description.
- **T08-5** [`advisory`] (§08): Document business and domain models in §8 because domain elements are referenced across many building blocks and are inherently crosscutting.
- **T08-6** [`advisory`] (§08): Link the §8 domain-model diagram to §12 glossary definitions rather than duplicating term explanations in both sections.
- **T08-7** [`advisory`] (§08): At minimum, create a logical data model for the domain; a full DDD model is preferable but not mandatory.
- **T08-8** [`advisory`] (§08): Illustrate concepts with targeted code excerpts or unit tests; do not manually copy large blocks of code into the documentation.
- **T08-9** [`advisory`] (§08): Document a concept as an architecture decision in §9 when a brief justification suffices, rather than writing a full concept elaboration.
- **T08-10** [`advisory`] (§08): Use the arc42 concept catalog as a completeness checklist to spot crosscutting topics that may need documentation.
- **T08-11** [`advisory`] (§08): Give each important concept a unique name and annotate building blocks in §5 with that name to make concept-to-block traceability explicit.

<!-- §09 Architecture Decisions — 10 tips -->
- **T09-1** [`advisory`] (§09): Record only architecturally significant decisions — those affecting structure, quality attributes, dependencies, interfaces, or construction technique.
- **T09-2** [`advisory`] (§09): Document the evaluation criteria for each decision, with priorities or weights, so the reasoning can be independently reproduced.
- **T09-3** [`advisory`] (§09): Always record the reasoning chain behind an important decision; the "why" carries more long-term value than the "what."
- **T09-4** [`advisory`] (§09): Use mind-maps or tables as lean formats for capturing architecture decisions; choose based on decision size and formality needs.
- **T09-5** [`advisory`] (§09): Write important decisions as Architecture Decision Records with title, context, decision, status, and consequences sections.
- **T09-6** [`advisory`] (§09): Include rejected alternatives and the explicit reasons they were rejected in every decision record.
- **T09-7** [`advisory`] (§09): Publish minor but team-relevant decisions informally (blog, feed) rather than burdening the formal architecture document.
- **T09-8** [`machine`] (§09): Every decision record must include a timestamp indicating when the decision was made.
- **T09-9** [`advisory`] (§09): Each ADR must cover exactly one decision, include rationale, carry timestamps on all entries, and record changes by appending rather than overwriting.
- **T09-10** [`advisory`] (§09): Write ADRs in lightweight Markdown files and use CLI tooling to create and manage them close to the codebase.

<!-- §10 Quality — 8 tips -->
- **T10-1** [`advisory`] (§10): Move all detailed quality scenarios to §10; §1.2 retains only the top handful of priority quality goals.
- **T10-2** [`advisory`] (§10): Present §10 quality requirements through a structured overview (quality tree or table), not a flat unorganized list.
- **T10-3** [`advisory`] (§10): Use a mind-map as the quality-tree format when a more reader-friendly hierarchy is preferred over a formal diagram.
- **T10-4** [`advisory`] (§10): Review the quality tree with stakeholders to spot branches that lack scenarios and determine whether those quality areas are truly out of scope.
- **T10-5** [`advisory`] (§10): Include usage scenarios that specify measurable system behavior (response times, click counts) for end-user interactions.
- **T10-6** [`advisory`] (§10): Include change scenarios that quantify the time or effort required to absorb functional or regulatory modifications.
- **T10-7** [`advisory`] (§10): Include failure scenarios that define what the system must do when hardware, software, or data problems occur.
- **T10-8** [`advisory`] (§10): Apply quality scenarios in structured architecture evaluation (e.g., ATAM) to map each scenario to its solution approach and associated risk.

<!-- §11 Risks and Technical Debt — 6 tips -->
- **T11-1** [`advisory`] (§11): Collect risks from a broad cross-section of stakeholders spanning management, development, operations, hardware experts, and users.
- **T11-2** [`advisory`] (§11): Treat each external interface as a prime candidate for risk; assess it for availability, security, and interface-stability exposure.
- **T11-3** [`advisory`] (§11): Surface risks by systematically comparing quality requirements against the current architecture and implementation approaches.
- **T11-4** [`advisory`] (§11): Examine development, build, release, deployment, and management processes for risks that originate outside the system code.
- **T11-5** [`advisory`] (§11): Investigate data structures, replication, backup, and synchronization mechanisms as potential sources of technical risk.
- **T11-6** [`advisory`] (§11): Apply both static and dynamic code analysis to identify implementation-level risks such as excessive complexity or low test coverage.

<!-- §12 Glossary — 6 tips -->
- **T12-1** [`advisory`] (§12): Maintain a glossary so all participants share a single agreed-upon meaning for the most important business and technical terms.
- **T12-2** [`advisory`] (§12): Format the glossary as an alphabetically sorted table; include recurring domain and architecture terms not defined elsewhere.
- **T12-3** [`advisory`] (§12): Supplement the glossary table with a relationship diagram for key terms to show how they connect to each other.
- **T12-4** [`advisory`] (§12): Add a translation column for each required language when the team or documentation spans multiple language communities.
- **T12-5** [`machine`] (§12): Restrict the glossary to 10–30 system-specific terms; exclude widely known acronyms and generic programming-language names.
- **T12-6** [`advisory`] (§12): Assign explicit ownership of the glossary (product owner or project manager) to ensure it stays current.
