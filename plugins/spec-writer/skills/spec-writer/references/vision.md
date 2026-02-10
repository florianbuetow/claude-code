# Vision & Strategic Alignment -- Reference Guide

## Table of Contents

- [1. Comparative analysis of product‑vision / alignment frameworks](#1-comparative-analysis-of-productvision-alignment-frameworks)
- [2. Empirical evidence: why vision/alignment matters](#2-empirical-evidence-why-visionalignment-matters)
- [3. What a vision/alignment document should contain](#3-what-a-visionalignment-document-should-contain)
- [4. Where this doc sits in the specification hierarchy](#4-where-this-doc-sits-in-the-specification-hierarchy)
- [5. Failure modes when the vision doc is absent, weak, or ignored](#5-failure-modes-when-the-vision-doc-is-absent-weak-or-ignored)
- [6. Keeping the vision document alive](#6-keeping-the-vision-document-alive)
- [7. Real-world examples & case studies](#7-real-world-examples-case-studies)
- [8. Recommended template for a greenfield software project](#8-recommended-template-for-a-greenfield-software-project)
- [Additional Research & Evidence](#additional-research-evidence)
- [Purpose and scope of the first alignment artefact](#purpose-and-scope-of-the-first-alignment-artefact)
- [Frameworks and formats for expressing vision and alignment](#frameworks-and-formats-for-expressing-vision-and-alignment)
- [Empirical evidence linking vision/alignment clarity to project outcomes](#empirical-evidence-linking-visionalignment-clarity-to-project-outcomes)
- [Recommended template structure for a greenfield alignment document](#recommended-template-structure-for-a-greenfield-alignment-document)
- [Position in the specification hierarchy and traceability expectations](#position-in-the-specification-hierarchy-and-traceability-expectations)
- [Failure modes when the document is missing, weak, or ignored](#failure-modes-when-the-document-is-missing-weak-or-ignored)
- [Best practices for keeping the document alive](#best-practices-for-keeping-the-document-alive)

---

Below is a consolidated "researcher's briefing" you can treat as a design input for your own template and practice. It's organized so you can (a) choose a framework, (b) design the content of your vision doc, and (c) wire it into your requirements stack and agile cadence.

***

## 1. Comparative analysis of product‑vision / alignment frameworks

### 1.1 Overview table

| Framework | Core structure | Intended audience & typical length | Best suited project types | Strengths | Limitations |
| --- | --- | --- | --- | --- | --- |
| **Impact Mapping (Gojko Adzic)** | Goal (Why) → Actors (Who) → Impacts (How behavior must change) → Deliverables (What we'll build) [draft](https://draft.io/example/impact-mapping) | Product + tech leadership, architects, stakeholders. Usually a 1–2 page diagram plus short narrative. | Medium–large initiatives where feature bloat and misalignment are risks; anything where behavior change and business outcomes matter more than raw output. [blog.octo](https://blog.octo.com/impact-mapping-business-success-in-software-development) | Forces explicit link from deliverables to behavioral impacts and to a measurable business goal; visually exposes assumptions and alternatives; good for prioritization and "less software, more impact". [agileleanhouse](https://www.agileleanhouse.com/lib/lib/People/GojkoAdzic/impact_mapping_20121001_sample.pdf) | Not a full narrative spec (no deep problem description, UX, or constraints by default); needs complementary artefacts (personas, KPIs, risks). |
| **Lean Canvas (Ash Maurya)** | One-page with 9 blocks: Problem, Customer Segments, Unique Value Proposition, Solution, Unfair Advantage, Channels, Revenue Streams, Cost Structure, Key Metrics. [icanpreneur](https://www.icanpreneur.com/blog/10-lean-canvas-examples) | Founders, product leaders, early investors. Exactly one page by design. | Greenfield products with high market/business-model risk (startups, new lines of business). | Extremely compact; surfaces key assumptions; centers on problem/solution fit and business viability, not just features; treated as a living hypothesis. [canva](https://www.canva.com/online-whiteboard/lean-canvas/) | Optimized for business model, not technical/operational concept; weak on non-goals, constraints, and traceability to later detailed requirements. |
| **Amazon Working Backwards PR/FAQ** | Internal **Press Release** (customer-facing story) + **FAQ** (problem, solution, customer value, edge cases, risks, success measures). [workingbackwards](https://workingbackwards.com/concepts/working-backwards-pr-faq-process/) | Senior leadership, cross-functional teams (eng, design, marketing, ops). Typically 1–2 pages PR + 3–6 pages FAQ. | Customer-facing products or major features where customer value and launch story must be crystal-clear; large organizations where leadership alignment is hard. [workingbackwards](https://workingbackwards.com/concepts/working-backwards-pr-faq-process/) | Brutally customer-centric; if you can't write a compelling PR, you probably shouldn't build it; FAQ forces confronting hard questions (risks, metrics, go-to-market). [workingbackwards](https://workingbackwards.com/resources/working-backwards-pr-faq/) | Assumes strong narrative skills; can under-specify internal constraints, technical context, and explicit non-goals unless you add them. |
| **Roman Pichler's Product Vision Board** | 5 sections: **Vision**, **Target Group**, **Needs**, **Product (key features)**, **Business Goals**. [linkedin](https://www.linkedin.com/pulse/product-vision-board-checklist-roman-pichler) | Product team + stakeholders. Fits on one board; often created in a 60–90 minute workshop. [ludi](https://ludi.co/templates/simple-product-vision-board-template-for-strategy-planning) | New or evolving products where you need shared understanding of *who*, *what problem*, *what product*, and *why for the business*; especially good in agile environments. | Nicely balances user-centric (Needs, Target Group) and business-centric (Business Goals) with a clear Vision statement; intentionally concise, avoids premature detail. [linkedin](https://www.linkedin.com/pulse/product-vision-board-checklist-roman-pichler) | Lightweight: you must add your own sections for metrics, non-goals, constraints, and traceability if you want something specification‑grade. |
| **Geoffrey Moore Elevator Pitch template** | "For [target customers] who are dissatisfied with [current alternative], our product is a [new product category] that provides [key benefit]. Unlike [alternative], our product [differentiator]." [elevatorpitchessentials](https://www.elevatorpitchessentials.com/essays/CrossingTheChasmElevatorPitchTemplate.html) | Executives, investors, internal stakeholders. One paragraph. | Any product; especially useful when entering/creating a category or when messaging is confused. | Forces brutal clarity on *who*, *what problem*, *what category*, and *why we're different*; very easy to remember and reuse in other artefacts. [elevatorpitchessentials](https://www.elevatorpitchessentials.com/essays/CrossingTheChasmElevatorPitchTemplate.html) | Way too thin as a standalone vision/alignment doc; it's a sharpening tool that should sit *inside* your broader document, not replace it. [wall-skills](https://wall-skills.com/2015/elevator-pitch-template/) |
| **Google‑style Design Doc "Goals & Non‑Goals"** | Section in a design doc: short bullet list of **Goals** and **Non-goals** (things that could reasonably be goals but are explicitly not). [industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google/) | Mainly engineers + tech leads; often reviewed by PM/architects. Goals/non-goals section is ~0.5–1 page inside a multi‑page doc. | Technical designs and internal systems once you're close to implementation; also makes sense in a high-level vision doc to bound scope. | Non-goals clarify scope boundaries and design trade-offs (e.g., "ACID compliance is *not* a goal"); helps avoid later disputes and feature creep. [industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google/) | Not a full product vision; assumes problem, users, and value proposition are defined elsewhere. |

### 1.2 Fit criteria and how to combine them

In practice, high-performing orgs often **layer** these frameworks:

- Use **Moore's elevator pitch** and a **Vision statement** (from Pichler) as the distilled "headline".
- Use a **Lean Canvas** to capture the *business model* risks early.
- Use a **PR/FAQ** to force customer-value clarity and leadership alignment before large investments.
- Use an **Impact Map** to connect vision and outcomes to deliverables and to structure epics/backlog.
- Capture **Goals and Non-goals** explicitly in the vision doc and later in design docs to bound scope. [industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google/)

For a greenfield software initiative in a tech organization, an effective initial strategic alignment artefact typically:

- borrows **structure** from Product Vision Board and Impact Mapping,
- embeds a **Moore-style pitch**,
- expresses success as **measurable outcomes** (OKRs/KPIs) per Torres/Cagan, [userpilot](https://userpilot.com/blog/continuous-discovery-framework-teresa-torres/)
- adopts **PR/FAQ questions** to pressure-test the idea.

***

## 2. Empirical evidence: why vision/alignment matters

There is no RCT that says "writing a product vision doc increases success by X%," but multiple empirical streams converge:

### 2.1 Standish CHAOS reports & project success factors

Analyses of thousands of IT projects by the Standish Group consistently rank **clear objectives and executive support** among the top success factors:

- Across CHAOS reports (1994–2010+), "User Involvement", "Executive Management Support", and "Clear Vision and Objectives / Clear Business Objectives" recur at or near the top of the success-factor list. [cafe-encounter](https://www.cafe-encounter.net/p1183/it-success-and-failure-the-chaos-report-factors)
- The CHAOS Manifesto 2012 identifies **executive sponsorship** as the #1 factor, assigning it 19 success points; it explicitly states that the executive sponsor sets the goals and that projects need a "central point of attention on a clear objective." [cs.calvin](https://cs.calvin.edu/courses/cs/262/kvlinden/resources/CHAOSManifesto2012.pdf)
- More recent CHAOS summaries (e.g., 2024) still highlight **strong executive sponsorship** and **clear requirements and scope definition** as key correlates of project success. [brynamics](https://www.brynamics.com/default.aspx/Resources/fgnhvb/Standish-Group-Chaos-Report-2024.pdf)

A high-quality vision/alignment document is one of the primary mechanisms to make "clear business objectives" + "executive sponsorship" concrete and shared.

### 2.2 Requirements engineering & Capers Jones

A widely cited paper on requirements engineering as a success factor notes that **deficient requirements are the single biggest cause of software project failure** and cites Capers Jones' finding that RE is deficient in more than 75% of organizations. The same work identifies good RE practices (clear scope, stakeholder agreement, validation) as clearly contributing to project success. [ics.uci](https://www.ics.uci.edu/~wscacchi/Software-Process/Readings/Req-Engr-SuccessFactors-Software-July01.pdf)

While that research focuses on RE broadly, **business/vision-level clarity** is the first link in the chain that RE depends on. Without a crisp statement of "why, for whom, and what success looks like," requirements quickly become inconsistent and untestable.

### 2.3 PMI / Johnson (CHAOS-based) analyses

A PMI paper summarizing CHAOS data lists 10 major success factors for projects, including:

1. User involvement  
2. Executive support  
3. **Clear business objectives**  
4. Scope optimization  
5. Agile processes  
… [pmi](https://www.pmi.org/learning/library/delivering-successful-projects-requirements-management-7020)

The author explicitly recommends:

- implementing requirements management processes in collaboration with stakeholders, and
- formal methodologies and tools to consistently manage those requirements. [pmi](https://www.pmi.org/learning/library/delivering-successful-projects-requirements-management-7020)

A well-structured vision doc is the first stable artefact those processes can hinge on.

### 2.4 ISO/IEC/IEEE 29148 and IREB

The **requirements engineering standard ISO/IEC/IEEE 29148:2018** defines a **business requirements specification** as a structured collection of the business problem or opportunity, concepts, required conditions of solutions, and their relation to the external environment. It also defines **concept of operations / operational concept** as broad, often long‑range statements of intentions and assumptions that "bound the operating space" and provide the basis for system capabilities, constraints, and scenarios. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

The **IREB CPRE syllabus** explicitly says that when high-level business or stakeholder requirements are expressed in durable work products—such as **business requirements specifications, stakeholder requirements specifications, or vision documents**—they **precede** the specification of system requirements. It stresses that these higher-level artefacts must be validated early to reduce the risk of unsatisfied stakeholders. [mstb](https://www.mstb.org/Downloadfile/cpre_foundationlevel_syllabus_en_v.3.1.pdf)

In other words, formal standards treat a vision/business-requirements artefact as a *first-class* prerequisite for robust downstream requirements.

### 2.5 Failure data: unclear goals and vague requirements

Multiple sources tie project failure to lack of clear vision/objectives and weak requirements:

- A software-project failure survey lists **"Unclear Software Requirements"** and **"Lack of User Involvement"** among the top reasons projects fail, arguing that without a clear vision of what and why, problems usually appear late and are costly to fix. [orientsoftware](https://www.orientsoftware.com/blog/software-project-failure/)
- A consultancy whitepaper on failed projects notes that **too many new-product projects move from idea straight into development with little or no up-front homework**, and that "solid pre-development processes drive up new software product success rates significantly." It explicitly recommends defining a **product vision** and broad-strokes plan instead of only detailed specs. [atlascode](https://www.atlascode.com/wp-content/uploads/2018/10/Why-software-projects-fail.pdf)
- A LinkedIn article on ICT project failures argues that the main root cause is a **poorly defined outcome or vision**: it leads to miscommunication, scope creep, inability to measure success, and integration problems, and it points to upper management's role in setting and communicating a clear vision tied to organizational goals. [linkedin](https://www.linkedin.com/pulse/why-do-ict-projects-fail-answer-lies-vision-leadership-trevor-weir-zcipc)
- Another practitioner piece on requirements gathering shows how **inadequate requirements** (incomplete, ambiguous, unvalidated, unprioritized) and lack of stakeholder input drove a help-desk system to incur 30% cost overrun in rework and poor adoption. [linkedin](https://www.linkedin.com/posts/darren-rinaldi-9621b11_what-happens-when-you-have-inadequate-requirements-activity-7377027846076227584-LQzk)

Taken together, the empirical picture is:

- Clear business/mission objectives and executive sponsorship are **strongly correlated** with project success. [cs.calvin](https://cs.calvin.edu/courses/cs/262/kvlinden/resources/CHAOSManifesto2012.pdf)
- Deficient requirements—of which unclear goals and scope are the root—are the **single biggest cause** of software project failure. [orientsoftware](https://www.orientsoftware.com/blog/software-project-failure/)
- Standards and syllabi explicitly call for **early, durable vision/business requirements artefacts** as the foundation for later specifications. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

The "initial strategic alignment doc" you're asking about is exactly the artefact that instantiates those factors.

***

## 3. What a vision/alignment document should contain

Below is an evidence-backed content model, with each section mapped to specific sources/frameworks.

### 3.1 Vision & elevator pitch

**Purpose:** state the future you aim to create and encapsulate the product in one sentence.

- Pichler defines product vision as the "overarching goal, the ultimate reason for creating the product, the positive change you want to bring about," expressed in a brief, inspiring statement. [linkedin](https://www.linkedin.com/pulse/product-vision-board-checklist-roman-pichler)
- Marty Cagan describes product vision as "the future we are trying to create," a vivid picture rather than a detailed map; it should act as a "North Star" aligning teams and stakeholders. [mindtheproduct](https://www.mindtheproduct.com/deep-dive-crafting-your-product-vision-and-mission/)
- Moore's elevator-pitch template gives a concrete pattern to articulate target customer, problem, category, key benefit, and differentiator. [wall-skills](https://wall-skills.com/2015/elevator-pitch-template/)

**Recommended content:**

- 1–2 sentence **Vision** (Pichler style).
- 1 paragraph **Elevator Pitch** using Moore's template, tuned to your domain.

### 3.2 Problem statement & business context

**Purpose:** satisfy ISO/IREB's notion of the "business or mission problem or opportunity" and external environment. [isqi](https://isqi.org/media/bb/49/c6/1710758065/cpre_foundationlevel_syllabus_EN_v.3.1.1.pdf)

Include:

- Concise description of the **business problem/opportunity**, referencing organizational goals.
- Why now? Market, regulatory, competitive, or internal drivers.
- High-level business constraints (e.g., time-to-market window, compliance regimes).

This corresponds to the **"Problem"** block in Lean Canvas and the **business/mission problem** part of a Business Requirements Specification. [icanpreneur](https://www.icanpreneur.com/blog/10-lean-canvas-examples)

### 3.3 Target users/customers (Target Group)

**Purpose:** clearly delimit who the product is for.

- Product Vision Board uses **Target Group** to describe the market or segment, users, and customers; recommends choosing a clear-cut segment, particularly for new products. [romanpichler](https://www.romanpichler.com/downloads/tools/Product-Vision-Board-with-Checklist.pdf)
- Lean Canvas "Customer Segments" plays the same role. [icanpreneur](https://www.icanpreneur.com/blog/10-lean-canvas-examples)

Include:

- Defined primary user group(s) and customers, including "non-users" you deliberately ignore for now (ties to non-goals).
- Any critical personas used internally.

### 3.4 Needs / value proposition

**Purpose:** describe user/customer needs and why they'll care.

- Pichler's **Needs** section captures the main problem or primary benefit, framed in outcome terms. [linkedin](https://www.linkedin.com/pulse/product-vision-board-checklist-roman-pichler)
- Lean Canvas emphasizes a **Problem–Solution** and **Unique Value Proposition**, including "why we win" vs alternatives. [canva](https://www.canva.com/online-whiteboard/lean-canvas/)
- Amazon PR/FAQ PR text answers: *what does it do, for whom, and why it matters*, from the customer's point of view. [onassemble](https://www.onassemble.com/blog/working-backwards-amazon-s-pr-faq-template)

Include:

- Top 1–3 user/customer needs or jobs-to-be-done, in plain language.
- Short **value proposition**: how you address those needs better than current alternatives (implicitly or explicitly referencing Moore's "unlike [alternative]…"). [elevatorpitchessentials](https://www.elevatorpitchessentials.com/essays/CrossingTheChasmElevatorPitchTemplate.html)

### 3.5 Desired outcomes & success metrics

**Purpose:** make "clear business objectives" and "clear vision and objectives" testable and traceable. [cafe-encounter](https://www.cafe-encounter.net/p1183/it-success-and-failure-the-chaos-report-factors)

Sources:

- Teresa Torres frames good product discovery as starting from a **clear outcome specified with a metric**, where a "product outcome" measures how well the product supports a given business outcome. [maze](https://maze.co/guides/product-discovery/continuous/)
- Pichler's **Business Goals** section is outcome-based, asking for desired business benefits (e.g., revenue, cost savings) with rough targets and prioritization. [romanpichler](https://www.romanpichler.com/downloads/tools/Product-Vision-Board-with-Checklist.pdf)
- CHAOS lists "Clear Business Objectives" as a top success factor; PMI notes that success requires measurable objectives. [pmi](https://www.pmi.org/learning/library/delivering-successful-projects-requirements-management-7020)

Include:

- 1–3 top-level **Business Outcomes** (e.g., OKR objectives) and 2–4 **Key Results / KPIs** each (conversion, retention, cycle time, NPS, cost reductions).
- 1–3 **Product Outcomes**: customer behavior metrics directly influenced by the product (e.g., "% of users who…"), aligned with Torres's outcome framing. [youtube](https://www.youtube.com/watch?v=1szy8q1EWSg)

### 3.6 Strategic constraints

**Purpose:** define the guardrails and non-functional constraints that shape possible solutions.

Examples:

- Regulatory regimes (GDPR, HIPAA).
- Platform constraints (must run on existing stack X).
- Time/cost caps (MVP must ship within N months, with max team size).
- Policy constraints (must not introduce new PII classes, etc.).

These are often missing from lightweight canvases but are essential for technically credible vision in enterprise settings; they also map to ISO 29148's notion of high-level conditions and environment. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

### 3.7 Scope: Goals, Non-goals, and Anti-scope

This is the **critical** piece you called out.

#### 3.7.1 Goals

- In design docs, Google recommends a short list of bullet-point **Goals** describing what the system should achieve. [notion](https://www.notion.so/Design-Docs-at-Google-289829908f354b5eae0a4c0c3cba596a)
- These should map directly to the outcomes and needs you've stated.

#### 3.7.2 Non-goals / anti-scope

Two complementary streams here:

- **Google's definition:** non-goals are not "the system shouldn't crash", but **things that could reasonably be goals, but are explicitly chosen not to be goals**—e.g., ACID compliance for a particular database. [blog.kjslab](https://blog.kjslab.com/211)
- **Joel Spolsky's spec guidance:** have a **"nongoals"** section listing features you won't have, use cases you won't support, or aspects you don't optimize, as a way to cull pet features and control scope. He emphasizes that limiting scope and stating what you won't do is crucial to avoid infinite timelines and cost. [dein](https://www.dein.fr/posts/articles-from-joel-spolsky-about-functional-specifications)

Hacker News/Beeminder's spec checklist (drawing on Joel) also insists that you "state at least one feature you won't include… or something more general like not caring about performance" in a Nongoals section. [blog.beeminder](https://blog.beeminder.com/speclist/)

**Recommended practice:**

- Separate **Goals** and **Non-goals** sections early in the vision doc.
- Non-goals should include:
  - Features or user segments explicitly **out of scope** for this initiative.
  - Performance/quality attributes you will **not** optimize in this phase (e.g., "not optimizing for on-prem deployment").
  - Business objectives you explicitly decline (e.g., "this project will not reduce infra spend; we accept short-term COGS increase to validate value").

This reduces hidden assumptions and later conflict about "but I thought we'd also…".

### 3.8 Stakeholders, sponsorship, and governance

Tie directly into CHAOS success factors:

- Identify **executive sponsor**, product leader, key stakeholder groups, and their responsibilities.
- Make clear who owns the vision document and who must agree before it changes.

Given evidence that **executive sponsorship** and **user involvement** are top success factors, this section is not bureaucracy—it's risk mitigation. [cs.calvin](https://cs.calvin.edu/courses/cs/262/kvlinden/resources/CHAOSManifesto2012.pdf)

### 3.9 Operational concept & high-level scenarios

**Purpose:** align with ISO 29148's **operational concept** and **high-level operational scenarios** as part of the business requirements layer. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

Include:

- A short **Concept of Operations**: how the organization intends to employ the system in its environment (who uses it, at what frequency, in what workflows).
- 2–5 **high-level scenarios** (not full use cases) covering key value moments and edge cases (happy path onboarding, failure/exception scenario, critical operational workflows).

This provides the "overall picture of operations" from users' and operators' perspectives, which ISO says is necessary to bound capabilities, interfaces, and environment. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

### 3.10 Risks, assumptions, and open questions

Borrowing from PR/FAQ:

- Amazon's FAQs include tough questions about **risks, dependencies, and how success will be measured**, explicitly to force teams to think deeply before building. [workingbackwards](https://workingbackwards.com/concepts/working-backwards-pr-faq-process/)
- Good specs and design docs also include **open questions** and assumptions so that unknowns are visible and can drive discovery and spikes. [notion](https://www.notion.so/Design-Docs-at-Google-289829908f354b5eae0a4c0c3cba596a)

Include:

- Top 5–10 assumptions (market, tech, org).
- Top N known risks and mitigations.
- Explicit "Open Questions" requiring research or decisions.

***

## 4. Where this doc sits in the specification hierarchy

### 4.1 Standards view (ISO 29148 + IREB + MBSE practice)

A simplified hierarchy consistent with ISO 29148, IREB, and MBSE practice is:

1. **Business Requirements / Vision**  
   - Expressed in a **Business Requirements Specification**, **Vision Document**, or **Operational Concept Document**. [mstb](https://www.mstb.org/Downloadfile/cpre_foundationlevel_syllabus_en_v.3.1.pdf)
   - Content: business/mission problem/opportunity, high-level goals, external environment, operational concept, high-level scenarios. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

2. **Stakeholder / User Requirements**  
   - Captures needs and constraints of specific stakeholder groups and users. [forum.mbse-capella](https://forum.mbse-capella.org/t/arcadia-iso-iec-ieee-29148-requirements-engineering/2979)
   - May be in a Stakeholder Requirements Specification or similar.

3. **System Requirements**  
   - Functional and non-functional requirements for the system as a black box; often in a System Requirements Specification. [forum.mbse-capella](https://forum.mbse-capella.org/t/arcadia-iso-iec-ieee-29148-requirements-engineering/2979)

4. **Design / Architecture artefacts**  
   - Detailed design docs, interfaces, data models, etc.

5. **Implementation & Test artefacts**  
   - Code, tests, procedures.

IREB explicitly notes that when high-level business/stakeholder requirements are documented in durable artefacts like **vision documents**, they **precede** and guide system requirements—even though, in practice, some co-evolution occurs. [mstb](https://www.mstb.org/Downloadfile/cpre_foundationlevel_syllabus_en_v.3.1.pdf)

MBSE practitioners (e.g., the Capella/Arcadia method) similarly distinguish:

- An **Operational Concept Document (OCD)** arising from Operational Analysis (stakeholders, environment, business goals, operational scenarios…), often including user requirements; and
- A **System Needs/Requirements Analysis**, producing system requirements, each traced back to user requirements for justification. [forum.mbse-capella](https://forum.mbse-capella.org/t/arcadia-iso-iec-ieee-29148-requirements-engineering/2979)

### 4.2 Traceability expectations

IREB's Requirements Management syllabus emphasizes **traceability** questions such as:

- "Which (sub-)system requirement belongs to which stakeholder requirement?"  
- "Which requirements version was implemented in the system?" [cockpit.ireb](https://cockpit.ireb.org/media/pages/downloads/cpre-requirements-management-syllabus/720d572054-1733311670/syllabus-requirements-management-en-v2.1.pdf)

This implies:

- Each goal in your vision doc should be traceable to:
  - one or more stakeholder requirements;
  - one or more system requirements/features (at later stages);
  - one or more test cases.

Impact Mapping gives a very practical way to *visualize* some of this traceability chain—Goal → Actors → Impacts → Deliverables—and ISO/IREB ask you to carry that further into formal requirements and architecture elements. [agileleanhouse](https://www.agileleanhouse.com/lib/lib/People/GojkoAdzic/impact_mapping_20121001_sample.pdf)

A pragmatic pattern:

- Tag each **Goal/Outcome** with an identifier (e.g., G-1, G-2).
- In epics/requirements, include references back to these IDs.
- Maintain a simple traceability view (spreadsheet or tool) mapping:
  - Goal/Outcome → Epics/Features → Key metrics → Tests.

***

## 5. Failure modes when the vision doc is absent, weak, or ignored

Empirical and practitioner sources converge on several recurring failure patterns:

1. **Scope creep and thrash**

   - When the initial "why" is vague, features proliferate based on stakeholder wishlist rather than impact; a failure analysis piece highlights **scope creep** as a leading cause of software project failure and traces it to **poor communication and undefined requirements**. [revstarconsulting](https://revstarconsulting.com/blog/7-common-reasons-software-projects-fail-and-how-to-avoid-them)
   - Without clearly documented objectives and non-goals, "everything is in scope," making trade-offs impossible.

2. **Misaligned expectations across stakeholders**

   - LinkedIn and consulting analyses show that poorly defined vision leads to **miscommunication between clients, developers, and management**, each with different mental models of the project, causing friction and rework. [linkedin](https://www.linkedin.com/pulse/why-do-ict-projects-fail-answer-lies-vision-leadership-trevor-weir-zcipc)
   - Joel Spolsky points out that without a spec, communication still happens but **ad hoc** and repeatedly, interrupting developers and leading QA to test the program "against the program rather than against the design." [joelonsoftware](https://www.joelonsoftware.com/2000/10/02/painless-functional-specifications-part-1-why-bother/)

3. **Unclear success criteria**

   - Without explicit outcomes and metrics, teams can't say if they've succeeded; Gina Consulting notes that starting a project without clear objectives is "one way to almost guarantee project failure," because "there's no way to know whether you've succeeded when you aren't completely sure what you're trying to accomplish." [ginaconsulting](https://ginaconsulting.com/2021/05/27/4-reasons-why-projects-fail-unclear-goals-and-objectives-of-the-project/)

4. **Late discovery of irreconcilable constraints**

   - Requirements engineering studies and practitioner stories consistently show that vague, incomplete, or unvalidated requirements yield **late surprises** and rework; the help-desk case shows 30% extra cost due to missing and ambiguous requirements. [ics.uci](https://www.ics.uci.edu/~wscacchi/Software-Process/Readings/Req-Engr-SuccessFactors-Software-July01.pdf)
   - An early Operational Concept plus constraints section in the vision doc flushes these out earlier.

5. **Feature factory behavior (output over outcomes)**

   - Marty Cagan and Teresa Torres both criticize teams that ship features without clear product outcomes; they argue that empowered teams should be given problems/outcomes, not feature lists. When the vision doc is only a feature bucket and not an outcome document, this feature-factory behavior is institutionalized. [techleadjournal](https://techleadjournal.dev/episodes/102/)

6. **Lack of user input and discovery**

   - CHAOS and multiple practitioner accounts cite **lack of user involvement** as a top failure factor. [orientsoftware](https://www.orientsoftware.com/blog/software-project-failure/)
   - Vision docs produced without real user input can give a false sense of alignment while still being detached from reality.

In practice, these failure modes often appear together: no clear vision → muddled requirements → scope creep, misalignment, and late defects.

***

## 6. Keeping the vision document alive

### 6.1 Time horizon and cadence

From Cagan and others:

- **Vision**: multi-year (3–5+ years), relatively stable; describes the future state. [age-of-product](https://age-of-product.com/marty-cagan-product-operating-model/)
- **Strategy**: updated more frequently (Cagan suggests quarterly) to adapt to learnings and market changes while still aligned to the vision. [age-of-product](https://age-of-product.com/marty-cagan-product-operating-model/)
- **Roadmap and backlog**: updated continuously; express the near-term bets to advance toward the vision. [atlassian](https://www.atlassian.com/agile/product-management/product-roadmaps)

**Recommendation:**

- Treat the vision/alignment doc as stable but not sacred.
  - Full, deep review: **annually** or when making a major strategic pivot.
  - Light check-in: each **quarter**, alongside product strategy/OKR resets.

### 6.2 Integration with agile ceremonies

You want the document to be *used*, not just written.

- **Roadmap planning:**  
  - Atlassian and Product School stress that roadmaps should show *why* as well as *what*, linking items clearly to product strategy and goals. [productschool](https://productschool.com/blog/product-strategy/what-is-a-product-roadmap)
  - Use the vision doc's outcomes and goals as the explicit "why" behind roadmap initiatives; if an initiative can't be traced to a goal, challenge it.

- **Sprint reviews:**  
  - Guidance on aligning sprint review outcomes with product vision/roadmap suggests using reviews to validate assumptions and ensure outcomes are consistent with long-term goals. [linkedin](https://www.linkedin.com/advice/1/how-do-you-align-your-sprint-review-outcomes)
  - In your sprint review agenda, add a slide that maps completed work to vision goals/outcomes; discuss whether observed metrics/feedback move the needles described in the doc.

- **Continuous discovery:**  
  - Teresa Torres's continuous discovery framework recommends starting with a clear outcome metric, mapping opportunities, and then solutions; this is exactly how the vision document's outcomes should feed a living **opportunity solution tree**. [hike](https://hike.one/topic/continuous-discovery)

### 6.3 Governance: ownership, versioning, and change management

- **Ownership:**  
  - Typically the **Product Manager/Owner** is primary author and steward, in partnership with design and engineering leadership; executive sponsor signs off.
- **Versioning & traceability:**  
  - Requirements management guidance recommends tracking versions, sources, and changes for downstream traceability and impact analysis. [gasq](https://www.gasq.org/files/content/gasq/downloads/certification/IREB/syllabus-requirements-management-en-v2.1.pdf)
  - At minimum include: version, date, author, approvers, and a short changelog.

- **Change policy:**  
  - Minor clarifications: can be batched and announced via release notes, with no change to version major number.
  - Material changes to goals, outcomes, or non-goals: treat as **major version** changes; run a structured review, then update roadmaps and OKRs accordingly.

- **Living document mindset:**  
  - Product-roadmap practice emphasizes treating roadmap as a living document, updated regularly with team and stakeholder input. Apply the same to the vision doc: it should be referenced often enough that staleness becomes obvious. [youtube](https://www.youtube.com/watch?v=8RPJYWWmV2M)

***

## 7. Real-world examples & case studies

### 7.1 Amazon's PR/FAQ for Kindle/AWS/Alexa (effective)

Multiple sources note that Amazon's **Working Backwards** method and PR/FAQ process were used to create major products like Kindle, AWS, and Alexa. The process: [larksuite](https://www.larksuite.com/en_us/blog/amazon-working-backwards)

- Starts with a fictional press release describing the product's benefits and customer story as if already launched.
- Accompanies it with an FAQ that probes **customer problem, proposed solution, differentiation, risks, and success measures**. [workingbackwards](https://workingbackwards.com/resources/working-backwards-pr-faq/)

This combination:

- forced teams to articulate clear **customer value and positioning** before building;
- created a **single alignment artefact** for executives and cross-functional teams; and
- served as a constant reference as implementation and discovery uncovered constraints.

The repeatable success of this pattern across multiple groundbreaking products is strong practice-level evidence of the effectiveness of a well-structured vision artefact.

### 7.2 Roman Pichler's Product Vision Board for a software product (effective)

Pichler describes using a Product Vision Board when exploring a software-based version of his Product Canvas tool, capturing assumptions about users/customers, needs, key features, and business value in a concise form. [romanpichler](https://www.romanpichler.com/blog/the-product-vision-board/)

He reports:

- The board helped him **think through the idea**, share it with his team and development partner, and
- focus on testing the **greatest risks** first. [romanpichler](https://www.romanpichler.com/blog/the-product-vision-board/)

He now uses the board for most new ideas (books, courses, tools), indicating it has proven to be a generalizable alignment tool. [ludi](https://ludi.co/templates/simple-product-vision-board-template-for-strategy-planning)

### 7.3 Lean Canvas in successful startups (effective)

Articles analyzing Lean Canvas usage detail how companies like Dropbox, Airbnb, Slack, and others used Lean Canvas early to clarify:

- core customer problems,
- their unique value propositions, and
- revenue and cost models. [bodhicreativecollective](https://bodhicreativecollective.com/lean-canvas-examples/)

For example, Dropbox's Lean Canvas emphasized "effortless file synchronization" as the unique value proposition and a freemium model for rapid adoption. These concise canvases: [bodhicreativecollective](https://bodhicreativecollective.com/lean-canvas-examples/)

- allowed founders to **validate assumptions quickly**,
- communicate the business model to investors and teams, and
- serve as a **living blueprint** as they iterated. [canva](https://www.canva.com/online-whiteboard/lean-canvas/)

While not the only factor, there's a consistent pattern that early, explicit articulation of problem, value proposition, and key metrics correlates with coherent execution.

### 7.4 Sainsbury's supply-chain management fiasco (ineffective/absent vision)

A case study on Sainsbury's failed supply-chain management project (a collaboration with Accenture) highlights multiple issues: lack of sponsor buy-in, weak outsourcing governance, poor planning, and political infighting. The analysis notes that: [atlascode](https://www.atlascode.com/wp-content/uploads/2018/10/Why-software-projects-fail.pdf)

- fundamental project strategies were missing, and
- later advice in the same document stresses defining **product vision** and **solid pre-development processes** as key to preventing similar debacles. [atlascode](https://www.atlascode.com/wp-content/uploads/2018/10/Why-software-projects-fail.pdf)

The failure illustrates how large-scale initiatives without clear vision, governance, and success measures can collapse under their own complexity.

### 7.5 Help-desk ticketing system with inadequate requirements (ineffective / weak vision)

The LinkedIn case of a new help-desk ticketing system shows:

- limited stakeholder involvement (only IT consulted, not HR/Finance/Operations),
- vague requirements like "system should be easy to use" with no usability metrics, and
- missing functional requirements (mobile access, integrations, SLA reporting). [linkedin](https://www.linkedin.com/posts/darren-rinaldi-9621b11_what-happens-when-you-have-inadequate-requirements-activity-7377027846076227584-LQzk)

Results:

- the system was delivered on time but lacked key features,
- rework increased costs by ~30%, and
- user satisfaction and adoption were poor. [linkedin](https://www.linkedin.com/posts/darren-rinaldi-9621b11_what-happens-when-you-have-inadequate-requirements-activity-7377027846076227584-LQzk)

A concise vision/alignment document capturing stakeholders, needs, outcomes (e.g., SLA tracking), and non-goals would likely have prevented some of these gaps.

***

## 8. Recommended template for a greenfield software project

Here is a concrete template synthesizing the above evidence, tuned for the very first artefact before detailed requirements.

### 8.1 Structure

Aim for **3–6 pages** of prose plus optional 1-page visual (Lean Canvas, Vision Board, or Impact Map). For an internal project:

1. **Document metadata**
   - Title, version, date, author(s), approvers, status (Draft/Approved).
   - Links to related artefacts (Lean Canvas, Impact Map, PR/FAQ, etc.).

2. **Vision & Elevator Pitch**
   - 1–2 sentence Vision (Pichler/Cagan style). [mindtheproduct](https://www.mindtheproduct.com/deep-dive-crafting-your-product-vision-and-mission/)
   - One-paragraph Elevator Pitch using Moore's template. [elevatorpitchessentials](https://www.elevatorpitchessentials.com/essays/CrossingTheChasmElevatorPitchTemplate.html)

3. **Problem & Business Context**
   - Business/mission problem or opportunity.
   - Why now? External/internal drivers.
   - Alignment with organizational strategies/OKRs.

4. **Target Users & Customers (Target Group)**
   - Primary user groups and customers.
   - Notable excluded segments (foreshadowing non-goals).

5. **User Needs & Value Proposition**
   - Top 1–3 user/customer needs.
   - Value proposition and key differentiators ("unlike [alternative] our product…"). [elevatorpitchessentials](https://www.elevatorpitchessentials.com/essays/CrossingTheChasmElevatorPitchTemplate.html)

6. **Desired Outcomes & Success Metrics**
   - Business Outcomes (OKR objectives + key results; Pichler Business Goals). [userpilot](https://userpilot.com/blog/continuous-discovery-framework-teresa-torres/)
   - Product Outcomes (behavioral product metrics). [youtube](https://www.youtube.com/watch?v=1szy8q1EWSg)

7. **Strategic Constraints**
   - Regulatory, platform, budget/time, and organizational constraints.

8. **Goals and Non-goals (Scope / Anti-scope)**
   - Bullet list of Goals.
   - Bullet list of Non-goals as per Google and Spolsky: reasonable goals explicitly excluded; specific features/segments intentionally not addressed now. [industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google/)

9. **Operational Concept & High-Level Scenarios**
   - Short Concept of Operations: how the system will be used in the organization, from user/operator perspective. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
   - 2–5 key scenarios that illustrate value and boundaries.

10. **Stakeholders, Sponsorship, and Governance**
    - Executive sponsor, product lead, major stakeholder groups.
    - Decision-making model for changes to this document.

11. **Traceability & Alignment Notes**
    - Table mapping:
      - Goals/Outcomes → high-level initiatives/epics → key metrics.
    - Notes on how this will feed business/stakeholder/system requirements (e.g., referencing ISO 29148 and organization's RE process). [cockpit.ireb](https://cockpit.ireb.org/media/pages/downloads/cpre-requirements-management-syllabus/720d572054-1733311670/syllabus-requirements-management-en-v2.1.pdf)

12. **Risks, Assumptions, and Open Questions**
    - Top assumptions.
    - Major risks (product, tech, org) with rough mitigations.
    - Open questions requiring discovery (user research, tech spikes) – feeding continuous discovery. [hike](https://hike.one/topic/continuous-discovery)

### 8.2 Authorship, length, cadence, and versioning guidance

- **Authorship**
  - Primary: Product Manager/Owner or equivalent.
  - Co-authors: engineering lead, design/UX lead; optionally architect.
  - Executive sponsor: reviews and explicitly approves objectives, scope, and non-goals.

- **Length**
  - For a single greenfield product: **3–6 pages** prose + 1 hidden "canvas" page is usually enough.
  - For a multi-team platform: 6–10 pages may be warranted, but keep the core sections (vision, problem, outcomes, goals/non-goals) in the first 2–3 pages.

- **Creation process**
  - Run a **90–120 minute workshop** to draft Vision, Target Group, Needs, Business Goals (Product Vision Board style), and optionally a Lean Canvas. [ludi](https://ludi.co/templates/simple-product-vision-board-template-for-strategy-planning)
  - Follow up with a smaller authoring group to write the full doc, PR/FAQ, and Impact Map.

- **Review cadence**
  - Initial approval: before significant engineering spend, as a **go/no-go** gate.
  - Quarterly: quick review against outcomes and adjust strategy/roadmap; update doc only if goals or constraints meaningfully change. [atlassian](https://www.atlassian.com/agile/product-management/product-roadmaps)
  - Annually or on pivot: full reconsideration of vision if market or strategy shifts.

- **Versioning**
  - Use semantic-like versioning:
    - Major (1.0 → 2.0) when goals, target users, or core value proposition change.
    - Minor (1.1 → 1.2) for constraints, metrics, and clarified wording.
  - Keep a brief change log at the top; record who changed what and when, aligning with IREB's emphasis on versioning and traceability. [gasq](https://www.gasq.org/files/content/gasq/downloads/certification/IREB/syllabus-requirements-management-en-v2.1.pdf)

***

### 9. How to choose and position frameworks in your context

For a greenfield software project in a modern tech org, a pragmatic recipe is:

- **Front page**: Vision + Elevator Pitch + one-sentence problem and target user.
- **Body**: Sections 3–12 above.
- **Attached canvases**:
  - Product Vision Board (Vision, Target Group, Needs, Product, Business Goals). [draft](https://draft.io/example/product-vision-board)
  - Lean Canvas if business-model risk is high. [icanpreneur](https://www.icanpreneur.com/blog/10-lean-canvas-examples)
  - Impact Map to tie goals → actors → impacts → deliverables, feeding backlog and traceability. [iborn](https://iborn.net/blog/impact-mapping-making-big-impact-software-products-and-projects)
  - Optional PR/FAQ if you need to convince senior leadership or external stakeholders in narrative form. [onassemble](https://www.onassemble.com/blog/working-backwards-amazon-s-pr-faq-template)

Treat the resulting artefact as both:

- your **business requirements specification / operational concept** in the sense of ISO 29148, and [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- the **alignment backbone** for roadmaps, sprints, discovery, and design docs, in line with Cagan, Torres, and agile best practice. [techleadjournal](https://techleadjournal.dev/episodes/102/)

From there, you can define the rest of your specification hierarchy and tooling around a single, explicit answer to: **"Why are we building this, for whom, and how will we know we've succeeded?"**

---

## Additional Research & Evidence

*Supplementary research and evidence from a second research pass.*

# Creating the initial strategic alignment document for a greenfield software project

## Purpose and scope of the first alignment artefact

The initial strategic alignment document (often labelled "Product Vision", "Impact Map", or "Project Charter") exists to prevent teams from starting with a shopping list of features, and instead to make the "why / for whom / how will we know" explicit before writing requirements. This intent is strongly echoed across outcome-driven planning approaches: Impact Mapping explicitly argues that feature lists without mapped justification make it hard to decide what should **not** be built and encourage scope creep, whereas a goal→impact→deliverable chain exposes assumptions and clarifies investment decisions. turn24view0

In requirements-engineering terms, this artefact typically sits **above** system requirements. The  (CPRE) materials describe "vision documents" and "business requirements specifications" as durable work products that can precede system requirements; they are used to express high-level business or stakeholder needs at an appropriate abstraction level before refined requirements are specified. turn17view1

A practical way to draw the boundary is: the document should be detailed enough to (a) align stakeholders, (b) constrain solution-space and scope, and (c) define measurable success—yet intentionally *not* detailed enough to be a requirements specification or implementation plan. turn47view0

## Frameworks and formats for expressing vision and alignment

The frameworks below represent a spectrum—from ultra-concise "positioning statements" (good for aligning language) to narrative "working backwards" documents (good for forcing customer-value clarity) to requirements-engineering-aligned charters/specs (good for governance and traceability). The comparison synthesises the primary descriptions and templates from the method authors and standards bodies. turn29view0turn26view0turn47view0


| Approach | Structure (what it contains) | Intended audience | Typical length / form | Best fit (project types) | Strengths | Limitations / failure risks |
|---|---|---|---|---|---|---|
| Impact Mapping (popularised by ) | A mind-map built around **Goal (Why)** → **Actors (Who)** → **Impacts (How behaviour changes)** → **Deliverables (What)**, explicitly connecting deliverables to desired outcomes and assumptions. turn24view0 | Usually a single visual (mind map) or hierarchical outline; frequently created in workshops and kept as an evolving artefact. turn24view0 | Greenfield or restart initiatives where stakeholders are tempted to prescribe solutions; also re-framing stalled initiatives and prioritising large backlogs.  | Strong at preventing "feature shopping lists" and at creating measurable outcomes (you can measure actor behaviour/impact after shipping). turn24view0 | Can degrade into a deliverables list if teams skip impacts; benefits depend on facilitation quality and stakeholder engagement.  |
| Lean Canvas (created by ) | One-page canvas capturing Problem, Solution, Unique Value Proposition, Customer Segments/Early Adopters, Channels, Key Metrics, Revenue Streams, Cost Structure, Unfair Advantage, plus "Existing Alternatives / High-level concept" prompts. turn29view0 | New products with high uncertainty where desirability/viability assumptions and go-to-market hypotheses are central. turn28view0 | Risk of being treated as a box-filling exercise; can under-specify operational constraints, governance, and non-goals unless explicitly added.  |
| Amazon-style PR/FAQ ("Working Backwards") (documented by ) | Two parts: (1) a **Press Release** written from the customer's viewpoint (customer, problem, solution, differentiation), and (2) **FAQs** split into external customer questions and internal "how will we build/run it" questions; written iteratively to reach clarity.  | Senior leadership, product teams, cross-functional stakeholders (finance, legal, ops, support) who must commit resources and align on value. turn7view0 | Strong forcing function for customer value clarity (writing a press release compels customer-centric framing) and for surfacing cross-functional risks early. turn7view0 | If written as a "sales pitch" instead of truth-seeking, it can hide risks; also heavier-weight than canvases and may feel slow without disciplined iteration.  |
| Product Vision Board (by ) | Five sections: Vision, Target Group, Needs, Product (3–5 standout capabilities), Business Goals; with explicit checks for being shared, outcome-based, prioritised, and connected to outcomes/roadmap. turn26view1 | Product leaders and stakeholders needing a lightweight "vision + strategy on a page" summary; useful for aligning teams and decision-makers. turn26view2 | Products where a stable mid/long-term direction exists but scope and outcomes need recurring alignment; especially good for portfolio contexts.  | Very high signal-to-noise; naturally includes "who" (target group), "why" (vision), "value" (needs), and business outcomes. turn26view2 | Can be too high-level for complex operational constraints unless supplemented; needs validation discipline or it can remain hypothesis-heavy.  |
| Elevator-pitch / positioning template (from  by ) | A fill-in template to state: target customer, compelling reason to buy, category, key benefit, differentiation, and explicit competitor comparison.  | Teams needing a shared internal language for value proposition and differentiation (product + marketing + leadership).  | Very short (often a paragraph or a few sentences); can be embedded into other docs as the "vision statement / positioning".  | Early alignment when teams struggle to articulate differentiation; useful as a "header" for any longer vision/charter doc.  | Forces clarity on positioning and alternatives, which reduces vague "for everyone" thinking.  | Too thin on governance, constraints, delivery scope, and success metrics unless paired with a richer artefact.  |
| Project Charter (PMI / PMBOK tradition, articulated by ) | A document that **formally authorises** the project and grants authority to use organisational resources; should include (directly or by reference) requirements, business needs, summary schedule, assumptions/constraints, and business case/ROI.  | Sponsors, portfolio governance, and project leadership; used to secure legitimacy, funding, and decision rights.  | PMI emphasises early charters should be short (often a few pages or even less), and can be informal in format so long as authorisation is clear.  | Regulated environments, multi-team programmes, vendor/contract contexts, or any environment needing explicit authority and governance clarity.  | Strong for clarifying authority, ownership, and constraints early—often the missing ingredient in "product vision only" documents.  | Can become bureaucratic or prematurely detailed; if treated as a one-off sign-off, it can go stale and lose alignment value.  |

## Empirical evidence linking vision/alignment clarity to project outcomes

Evidence is strongest when "vision documents" are treated as part of **requirements engineering / early planning quality**, because many datasets operationalise success factors as clear objectives, user involvement, executive support, and requirements clarity rather than "a specific document type". Three evidence streams are particularly relevant: Standish CHAOS datasets, empirical RE field studies, and large-project benchmarking analyses. turn40view0

The  CHAOS findings consistently rank clarity and sponsorship factors among the strongest differentiators of success. In the (widely circulated) CHAOS report text, the top cited success factors include user involvement, executive management support, and a clear statement of requirements; "clear vision & objectives" also appears as a success factor, while "unclear objectives" appears among factors that challenge projects.  In the CHAOS Manifesto 2013 slide deck, the "10 factors of success" for small projects assign the highest weight to executive management support and user involvement, and explicitly include "clear business objectives"; the deck further notes that clear business objectives require a concise vision/problem statement and emphasises being concise and focused. turn33view1

In peer-reviewed software engineering research, Hofmann and Lehner's IEEE Software field study of 15 requirements engineering teams argues that requirements engineering practices measurably contribute to project performance and identifies stakeholder feedback as decisive in successful RE projects. The paper reports better performance for teams combining prototyping and model-based approaches, and shows that "top performers" balance knowledge, resources, and process over time—an empirical reinforcement of keeping alignment artefacts alive rather than treating them as a one-off deliverable. turn40view1

Large-project benchmarking analyses also link early definition and control to outcomes.  reports an analysis of ~250 large projects (≥10,000 function points) examined between 1995–2004, contrasting successful projects against those with major overruns or termination; he identifies systematic differences concentrated in planning, estimating, measurement, milestone tracking, change control, and quality control. Importantly for vision/alignment, his discussion of milestone practices includes "requirements review" and emphasises measuring the volume/rate of requirements changes, signalling that early clarity plus active control of scope change correlate with better outcomes. turn38view1

Standards and professional curricula provide an additional (normative) signal: they institutionalise the idea that it is valuable to represent business purpose, scope, mission/goals, stakeholders, operational scenarios, and constraints *before* detailed requirements are written. The table-of-contents preview for  lists Business Requirements Specification content such as business purpose, business scope, mission/goals/objectives, business processes, operational policies/rules, operational constraints, scenarios, and project constraints—elements that strongly overlap with "vision/alignment document" sections. 

## Recommended template structure for a greenfield alignment document

A useful template is one that can be read quickly by executives and delivery teams, yet is structured enough to support traceability and anti-scope. PMI explicitly notes that a charter can be informal in format but must answer authority and authorisation questions; Impact Mapping and PR/FAQ methods emphasise forcing clarity on goals, customers, and measurable outcomes; and both  and "Google design doc" practices stress that *non-goals* are essential to avoid endless scope growth. turn24view2turn6view0

A pragmatic, evidence-aligned structure (typically 2–5 pages, plus optional appendices) is:

**Document header and ownership**
- **Title, status, owner, reviewers, last-updated, version**. Single-point ownership reduces diffusion of responsibility; Spolsky argues for one named spec owner and for keeping the document updated as the product evolves.   
- **Decision authority / sponsorship** (who authorises spend and scope decisions). This is the core PMBOK "charter" function: formal authorisation and authority to apply resources.   

**Problem, users, and value**
- **Problem statement / opportunity** framed in user terms (what is painful, for whom, and why now). The PR/FAQ approach treats the "problem paragraph" as customer-point-of-view writing and positions it as requiring deep understanding.   
- **Target users / actors / segments**. Impact Mapping makes actors a first-class element (who can help or obstruct success), and the Product Vision Board demands a clear target group. turn26view0  
- **Value proposition and differentiation**. The elevator pitch template is an effective compression mechanism: it forces an explicit "best buy for this situation" framing and competitor comparison.   

**Objectives and success measures**
- **Business objective(s)** expressed as outcome(s), not outputs, and prioritised when multiple objectives exist. The Product Vision Board explicitly requires outcome-based business goals and prioritisation.   
- **Success metrics** (preferably a small set) that define "how we'll know": OKRs and measurable outcomes are explicitly recommended in the AWS prescriptive guidance as tools to capture objectives and key results during vision formulation, and Impact Mapping encourages capturing metrics for goals/impacts (even if refined later). turn24view1  
- **Leading indicators / input metrics (optional)**. A useful interpretation is: outcomes are lagging; define 1–3 leading signals you can inspect during delivery to decide whether to pivot or persevere. This is consistent with outcome-driven roadmapping thinking (OKRs/outcomes) and PR/FAQ's insistence on defining what must be true for success. turn11view0  

**Scope and anti-scope**
- **In-scope boundaries** stated at a "capability" level (not user stories yet).  
- **Non-goals / exclusions (anti-scope)** as explicit first-class content. Spolsky calls a "nongoals" section one of the most important ways to cull pet features early, and the Google design-doc structure highlights that non-goals are often more important than goals, while clarifying that non-goals are not trivial negations but plausible goals intentionally excluded. turn42view0  
- **Assumptions and constraints** (strategic, regulatory, technical, delivery, budget/time). PMI lists assumptions/constraints as charter content; ISO 29148 BRS content explicitly includes "project constraints" and operational constraints/policies. turn22view0  

**High-level approach and risks**
- **Solution approach at "concept" level only** (what kind of product/service and what the first release must enable), avoiding implementation detail. The Product Vision Board constrains "Product" to 3–5 coarse-grained capabilities.   
- **Key risks / open questions** phrased as assumptions to validate (market, usability, feasibility, compliance), plus how/when they will be tested. PR/FAQ's internal FAQ is explicitly meant to surface cross-functional risks and the conditions for success/failure.   

**Immediate next artefacts**
- A short "handover" section mapping this document to next steps (personas, customer journey, impact map refinement, epics, discovery plan). AWS prescriptive guidance explicitly sequences vision statement → personas/journey maps → PR/FAQ → epics/user stories/roadmap.   

**Length guidance (what is "enough")**
- If you need a *one-page* artefact, Lean Canvas or the Product Vision Board are designed for that constraint. turn26view0  
- If the initiative is high-stakes and cross-functional, PR/FAQ is intentionally longer and iterative; it is designed to be rewritten until clarity is reached and can take substantial time for major bets.   
- If governance authorisation is the bottleneck, PMI notes that an early charter can be "a few pages" or even less so long as authority and key references are clear.   

## Position in the specification hierarchy and traceability expectations

In a standards-aligned hierarchy, the initial vision/alignment artefact is best treated as either (a) a precursor to, or (b) a lightweight form of, business/stakeholder requirements documentation—explicitly above system requirements. The CPRE syllabus explains that requirements exist at multiple abstraction levels and warns against mixing levels; it states that high-level business or stakeholder requirements expressed in durable work products (business requirements specs, stakeholder requirements specs, or vision documents) precede system requirements, though in some settings they may co-evolve. 

Traceability expectations follow naturally from that hierarchy. The CPRE syllabus defines traceability as the ability to trace a requirement back to its origin (stakeholders, documents, justifications) and forward to subsequent work products (e.g., test cases), implemented by maintaining dependencies across work products and abstraction levels.  This definition provides a practical interpretation for the alignment document: it should create stable "anchors" (goals, outcomes, non-goals, constraints) that downstream requirements can trace to. turn20view0

A concrete, low-friction traceability scheme that fits greenfield work:

1. **Give every goal/outcome a stable identifier** (e.g., OBJ-1, OBJ-2).  
2. **Link each epic / major capability to one or more outcomes** (impact-mapping style: deliverable → impact → objective).   
3. **Maintain a "non-goals register"** where deferred/excluded items map to a rationale (cost, strategy, risk). This mirrors Spolsky's "nongoals" practice and reduces re-litigation of scope.   
4. **Ensure roadmap/sprint review discussions reference the outcome IDs**, not feature names, consistent with outcome-based roadmap framing and with Impact Mapping's emphasis on measuring behaviour change against goals. turn24view0  

If your organisation needs a more formal outline, ISO 29148's Business Requirements Specification content list (purpose, scope, mission/goals/objectives, scenarios, policies/rules, constraints) can be used as a "menu" of sections to tailor down to the minimum effective set for a greenfield software initiative. 

## Failure modes when the document is missing, weak, or ignored

The most common failure mode is replacing strategy with a feature list: teams start building "what we can think of" rather than "what will move the objective." Impact Mapping explicitly calls out that plans and requirements documents often become shopping lists without context, which makes it difficult to argue investment priorities and leads to scope creep as stakeholders add pet features. 

Empirical failure-factor data reinforces that missing alignment manifests as unclear objectives, insufficient user input, and unstable requirements. In the CHAOS report text, challenged projects are associated with lack of user input, incomplete requirements/specifications, changing requirements/specifications, lack of executive support, and unclear objectives.  This failure pattern is also consistent with PMI's observation that projects cannot progress legitimately without authorisation and clarity on business need and constraints; when authorisation is implicit or fragmented, governance and alignment become unstable. 

Three instructive real-world cases illustrate how these failure modes surface:

**Working Backwards as an effective alignment mechanism (AWS case)**  
The PR/FAQ method is presented as a forcing function to keep teams focused on customer needs, and the Working Backwards authors claim that for the earliest AWS foundational services, key leaders invested extensive upfront time debating and refining what problems were being solved and for whom, before building.  As an external validation of AWS's subsequent scale and trajectory, the 2015 shareholder letter filed with the U.S. SEC includes the statement that AWS had become larger than Amazon.com at 10 years old and was growing faster—evidence consistent with the claim that the initiative achieved substantial business outcomes. 

**FBI Virtual Case File as an example of weak alignment and control**  
GAO reporting on FBI modernisation efforts documents that the "Virtual Case File" segment of the Trilogy programme was delayed and required a new schedule, and later GAO testimony describes Trilogy as plagued with missed milestones and escalating costs, while not succeeding in upgrading investigative applications as intended. turn45view1

**NHS National Programme for IT as an example of top-down vision without sufficient end-user alignment**  
A peer-reviewed retrospective summarises that the programme's failure was driven by, among other factors, lack of adequate end-user engagement, absence of phased change management, and underestimating project scale.  Earlier NAO reporting also highlights the organisational challenge of delivering systems that meet NHS needs and *winning support of staff and the public*, underscoring that aligning stakeholders and users is a non-negotiable condition for success in socio-technical systems of this scale. 

## Best practices for keeping the document alive

The core pattern across practitioner guidance is: the initial alignment artefact should be stable in intent but actively maintained in detail, and it should be used repeatedly as a decision tool—not archived after kickoff. turn26view2turn47view0

Cadence and revision practices are unusually explicit in several sources. Spolsky argues that specs must "stay alive," updated frequently to reflect the team's best understanding, and suggests maintaining an up-to-date version accessible to the team and using milestone-based revision marking rather than constant reprinting.  The Product Vision Board checklist recommends regular review and adjustment at least once every three months as a rule of thumb, and also demands that the board be connected systematically to more specific outcomes and (preferably) an outcome-based roadmap.  Impact Mapping, when used for focusing delivery, advises capturing metrics and using the map to review those metrics frequently during delivery so stakeholders can change priorities based on observed impacts. turn24view0

A practical governance model (lightweight but robust) that matches the evidence:

- **Authorship:** one accountable owner (typically product lead or product manager), with explicit sponsor sign-off on goals, constraints, and non-goals. This combines Spolsky's "one author" accountability with PMI's focus on sponsor authorisation and authority. turn47view0  
- **Review moments:** (a) kickoff (initial baseline), (b) quarterly (strategy refresh), and (c) any time an outcome metric or strategic constraint materially changes. This is directly aligned with Pichler's "at least every three months" and with outcome/metrics-driven approaches. turn24view0  
- **Sprint reviews / roadmap planning:** explicitly reference outcomes and non-goals, not just shipped features; this matches outcome-based roadmap guidance that outcomes need product vision context. turn33view1  
- **Versioning:** treat the artefact as a controlled but living document: change log, stable IDs for objectives, and explicit deprecations of non-goals if/when they become goals. This aligns with CPRE's distinction between evolving and durable work products and its emphasis on traceability and change handling. turn20view1  

Finally, modern product practice emphasises maintaining alignment through continuous discovery mechanisms. 's opportunity solution trees start with a desired outcome, branch through opportunities (customer needs) and solutions, and are positioned explicitly as a way to externalise and visualise shared thinking so teams can align around what to do when; they also provide guidance on sharing the right level of detail with stakeholders to maintain buy-in.  Complementing this,  (via ) argues that empowered teams need deep context starting with product vision and strategy, and that outcomes (including OKRs) need the "bigger picture" of a comprehensive product vision to be actionable and coherent. turn41view1
