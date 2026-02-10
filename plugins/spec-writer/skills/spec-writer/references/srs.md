# Software Requirements Specification -- Reference Guide

## Table of Contents

- [1. What the standards mean by "SRS" and how the quality criteria evolved](#1-what-the-standards-mean-by-srs-and-how-the-quality-criteria-evolved)
- [2. Recommended SRS structure for a greenfield project](#2-recommended-srs-structure-for-a-greenfield-project)
- [3. Expressing functional requirements: formats and when to use them](#3-expressing-functional-requirements-formats-and-when-to-use-them)
- [4. Writing measurable NFRs: patterns and examples](#4-writing-measurable-nfrs-patterns-and-examples)
- [5. External interfaces and data contracts](#5-external-interfaces-and-data-contracts)
- [6. Requirement atomicity, identification, attributes, and prioritization](#6-requirement-atomicity-identification-attributes-and-prioritization)
- [7. Managing assumptions, constraints, risks, and TBDs](#7-managing-assumptions-constraints-risks-and-tbds)
- [8. SRS templates and empirical evidence on structure](#8-srs-templates-and-empirical-evidence-on-structure)
- [9. SRS and agile backlogs: a hybrid model](#9-srs-and-agile-backlogs-a-hybrid-model)
- [10. Traceability model: from business goals to tests](#10-traceability-model-from-business-goals-to-tests)
- [11. SRS maintenance, versioning, and review practices](#11-srs-maintenance-versioning-and-review-practices)
- [12. Summary: practical starting point](#12-summary-practical-starting-point)
- [Additional Research & Evidence](#additional-research-evidence)
- [What standards mean by an SRS and what "good" looks like](#what-standards-mean-by-an-srs-and-what-good-looks-like)
- [A recommended lean SRS structure for a greenfield project](#a-recommended-lean-srs-structure-for-a-greenfield-project)
- [Choosing a format for functional requirements and capturing edge cases](#choosing-a-format-for-functional-requirements-and-capturing-edge-cases)
- [Turning non-functional requirements into measurable, verifiable targets](#turning-non-functional-requirements-into-measurable-verifiable-targets)
- [Documenting external interfaces and data contracts without dictating architecture](#documenting-external-interfaces-and-data-contracts-without-dictating-architecture)
- [Atomicity, identifiers, prioritisation, and a traceability model](#atomicity-identifiers-prioritisation-and-a-traceability-model)
- [Managing assumptions, constraints, risks, and "TBD" items—and keeping the SRS alive in agile delivery](#managing-assumptions-constraints-risks-and-tbd-itemsand-keeping-the-srs-alive-in-agile-delivery)

---

Below is a consolidated, evidence-based guide that you can treat as a blueprint for setting up the core SRS practice on a greenfield project.

***

## 1. What the standards mean by "SRS" and how the quality criteria evolved

### 1.1 IEEE 830-1998: classic SRS definition and qualities

IEEE 830-1998 defines the SRS as the document that:

- Describes all essential requirements (functions, performance, design constraints, and quality attributes) and all external interfaces of the software.  
- Defines the scope and boundaries of the software within its environment. [math.uaa.alaska](http://www.math.uaa.alaska.edu/~afkjm/cs401/IEEE830.pdf)

It provides a canonical SRS outline (simplified):

1. Introduction (purpose, scope, definitions, references, overview)  
2. Overall description (product perspective, product functions, user characteristics, constraints, assumptions/dependencies)  
3. Specific requirements  
   - 3.1 External interface requirements  
   - 3.2 Functions  
   - 3.3 Performance requirements  
   - 3.4 Logical database requirements  
   - 3.5 Design constraints  
   - 3.6 Software system quality attributes  
4. Appendices  
5. Index [site.uottawa](https://www.site.uottawa.ca/~bochmann/SEG3101/Notes/SEG3101-ch3-2%20-%20Requirements%20documentation%20standards%20-%20IEEE830.pdf)

IEEE 830 also defines the famous SRS quality criteria: an SRS should be:

- Correct  
- Unambiguous  
- Complete  
- Consistent  
- Ranked for importance and/or stability  
- Verifiable  
- Modifiable  
- Traceable [seng.cankaya.edu](https://seng.cankaya.edu.tr/wp-content/uploads/sites/53/2024/09/IEEE-SRS-830-1998.pdf)

These properties are applied both to individual requirements (e.g., unambiguous, verifiable) and to the SRS as a whole (e.g., complete, consistent, modifiable).

### 1.2 ISO/IEC/IEEE 29148:2018: requirements engineering + SRS content

29148 is broader: it standardizes requirements engineering processes and defines what a "good requirement" looks like, plus content for requirements information items (including an SRS). [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

It reinforces (and slightly extends) the IEEE 830 qualities and explicitly defines characteristics of individual requirements such as:

- Necessary  
- Implementation-free  
- Unambiguous  
- Consistent  
- Complete (within its level)  
- Singular  
- Feasible  
- Traceable  
- Verifiable  
- Bounded (quantified, with clear limits) [cwnp](https://www.cwnp.com/req-eng/)

29148 also defines requirements traceability matrices as structured artifacts linking requirements to higher-level requirements and to lower-level implementation/test artifacts. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

For SRS-like content, 29148 gives example templates for "System Requirements Specification (SyRS)" and software requirements specifications. A typical 29148-based SRS template (see derivative example) echoes IEEE 830 but is explicit about: [well-architected-guide](https://www.well-architected-guide.com/documents/iso-iec-ieee-29148-template/)

- Purpose, scope, stakeholders, and context  
- System overview, boundaries, and modes  
- Functional requirements grouped by capability or feature  
- Quality requirements (often grouped by ISO 25010 characteristics)  
- Interface requirements (user, software, hardware, communication)  
- Constraints, assumptions, and dependencies  
- Verification/validation considerations

### 1.3 INCOSE Guide to Writing Requirements: individual vs set-level qualities

INCOSE's *Guide to Writing Requirements* distinguishes:

- **Individual requirement characteristics**: correct, necessary, appropriate to level, unambiguous, singular, feasible, verifiable, complete enough at that level, etc. [moodle.insa-toulouse](https://moodle.insa-toulouse.fr/pluginfile.php/121422/mod_folder/content/0/INCOSE%20Guide%20for%20Writing%20Requirements.pdf)
- **Set-level characteristics**: complete as a set, consistent as a set, feasible as a whole, comprehensible, and able to be validated. [moodle.insa-toulouse](https://moodle.insa-toulouse.fr/pluginfile.php/121422/mod_folder/content/0/INCOSE%20Guide%20for%20Writing%20Requirements.pdf)

INCOSE explicitly calls out "Singular" (no "and/or" multi-clauses) and "Appropriate" (right level of detail for the system vs subsystem) as critical properties for atomic, well-structured requirements. [incose](https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_products/incose_rwg_gtwr_summary_sheet_2022.pdf)

**Practical implication:**  

- Use IEEE 830/29148 as your document/template and SRS-level quality checklist.  
- Use INCOSE + 29148 as your per-requirement checklist (singular, necessary, bounded, verifiable, traceable).

***

## 2. Recommended SRS structure for a greenfield project

Below is a lean but standards-aligned SRS template tuned for a greenfield system. It intentionally keeps functional detail at a level that plays well with agile backlogs while capturing the "contract" aspects (behavioral, quality, interface, constraints).

For each section, "Include" vs "Defer" guidance is given.

### 2.1 Top-level outline

1. **Introduction and Scope**  
2. **Stakeholders and Business Goals**  
3. **System Context and Overview**  
4. **Functional Capabilities and Behavior**  
5. **Quality and Non-functional Requirements**  
6. **External Interfaces and Data Contracts**  
7. **Constraints, Assumptions, and Dependencies**  
8. **Risks and Open Issues ("TBD" Log)**  
9. **Requirements Attributes and Traceability Model**  
10. **Appendices (Glossary, Models, Reference Material)**

This structure is directly compatible with IEEE 830/Wiegers SRS outlines and with 29148-oriented templates. [duikt.edu](https://duikt.edu.ua/uploads/l_617_29503822.pdf)

### 2.2 Section rationales and what to include vs defer

**1. Introduction and Scope**

- Purpose of the SRS; what product/system it covers, and what it does *not* cover. [duikt.edu](https://duikt.edu.ua/uploads/l_617_29503822.pdf)
- References to business cases, vision docs, and architectural decision records.  

*Why:* The 32-project empirical study (Kamata & Tamai, RE 2007) found that rich Section 1 descriptions (purpose, overview, context) strongly correlated with projects that stayed on cost and schedule, whereas overrun projects tended to have poor Section 1 but detailed functional sections. [research.ibm](https://research.ibm.com/publications/how-does-requirements-quality-relate-to-project-success-or-failure)

**Include:** Concise but explicit purpose, system scope, document scope.  
**Defer to other artifacts:** Detailed business case (kept separate, just referenced).

***

**2. Stakeholders and Business Goals**

- Stakeholder classes and their primary concerns.  
- Top-level business/mission goals and success metrics.  

*Why:* 29148 and INCOSE emphasize traceability from business/mission objectives down to system requirements; this section anchors that. [cwnp](https://www.cwnp.com/req-eng/)

**Include:** Business goals and measurable high-level outcomes (e.g., "Reduce manual processing time by 50% within 12 months").  
**Defer:** Detailed KPIs dashboards – reference your product strategy docs.

***

**3. System Context and Overview**

- System boundary and context diagram(s).  
- High-level capabilities / features (not yet full requirements).  
- External systems and actors.  

IEEE 830 and Wiegers recommend a product perspective and product functions overview, often with dataflow or context diagrams. [site.uottawa](https://www.site.uottawa.ca/~bochmann/SEG3101/Notes/SEG3101-ch3-2%20-%20Requirements%20documentation%20standards%20-%20IEEE830.pdf)

**Include:** Context diagram, list of external systems and contracts that *must* be honored, operating environment.  
**Defer:** Detailed internal architecture; keep this implementation-agnostic as per IEEE 830 (no design in SRS). [math.uaa.alaska](http://www.math.uaa.alaska.edu/~afkjm/cs401/IEEE830.pdf)

***

**4. Functional Capabilities and Behavior**

- Capabilities or features with behavioral requirements expressed in one or more styles:
  - Structured "shall" requirements
  - Use case summaries (and possibly fully-dressed use cases for high-risk flows)
  - User stories + acceptance criteria
  - EARS-style requirement patterns, especially for edge/failure modes
  - Links to Specification by Example scenarios

IEEE 830's "Functions" section is here, but you structure it into feature/capability groupings and reference agile artifacts. [site.uottawa](https://www.site.uottawa.ca/~bochmann/SEG3101/Notes/SEG3101-ch3-2%20-%20Requirements%20documentation%20standards%20-%20IEEE830.pdf)

**Include:**  
- For each capability: high-level goal, main success path behavior, major alternate/error flows.  
- System-level invariants and cross-cutting business rules.  

**Defer to backlog:** Fine-grained stories and detailed example tables; keep them in your product backlog / BDD specs, linked via traceability.

***

**5. Quality and Non-functional Requirements**

- Organized by ISO/IEC 25010:2023 quality characteristics (functional suitability, performance efficiency, compatibility, interaction capability/usability, reliability, security, maintainability, flexibility/portability, safety). [quality.arc42](https://quality.arc42.org/standards/iso-25010)
- Each NFR articulated as a measurable scenario/fit criterion (see Section 4 below).

**Include:** NFRs that shape architecture and system-wide decisions (latency, throughput, availability, data retention, security baselines, regulatory constraints).  
**Defer:** UI micro-usability details; keep those in UX guidelines or design system documentation.

***

**6. External Interfaces and Data Contracts**

- Requirements on:
  - User interfaces (roles, major views, accessibility constraints)
  - Software interfaces (APIs, messages)
  - Hardware interfaces
  - Communication interfaces (protocols, ports, connectivity expectations) [duikt.edu](https://duikt.edu.ua/uploads/l_617_29503822.pdf)

**Include:**  
- Behavioral contracts: accepted inputs, error conditions, response semantics, idempotency, invariants.  
- If you practice API-first: reference specific OpenAPI/AsyncAPI specs as normative artifacts.

**Defer:** Implementation-level API routing details or specific frameworks.

***

**7. Constraints, Assumptions, and Dependencies**

- Design and implementation constraints (e.g., mandated tech stack, regulatory compliance). [cs.uic](https://www.cs.uic.edu/~i440/VolereMaterials/templateArchive16/c%20Volere%20template16.pdf)
- Assumptions about users, third-party systems, and environment (per Wiegers's 2.7 "Assumptions and Dependencies"). [duikt.edu](https://duikt.edu.ua/uploads/l_617_29503822.pdf)
- External dependencies (COTS components, upstream systems).

**Include:** Anything that, if false or changed, would significantly alter scope or design.  
**Defer:** Non-critical preferences (e.g., "prefer PostgreSQL") that are not contractual.

***

**8. Risks and Open Issues ("TBD" Log)**

- Explicit "TBD" list, following Wiegers's Appendix C pattern: every TBD is numbered, explained, and tracked to closure. [wpollock](https://wpollock.com/AJava/srs_template_IEEE.pdf)
- Known risks tied to uncertain or volatile requirements (especially NFRs).

**Include:**  
- Open questions on behavior, NFR thresholds, or external contracts.  
- Risk items where decisions are deferred (with due dates/spikes).

***

**9. Requirements Attributes and Traceability Model**

- Definition of requirement attributes:
  - ID, type (functional/NFR/interface/constraint), priority (e.g., MoSCoW), status, owner, source, rationale, risk, verification method, links to upstream/downstream artifacts. [reqview](https://www.reqview.com/papers/ReqView-Custom_Requirement_Attributes.pdf)
- Description of the traceability scheme (see Section 6 and 8).

**Include:** Attribute definitions and conventions (naming/ID patterns, what "priority" means).  
**Defer:** Tool-specific configuration details (Jira/ReqView/etc.) – reference configuration docs.

***

**10. Appendices**

- Glossary and controlled vocabulary (critical for unambiguity). [duikt.edu](https://duikt.edu.ua/uploads/l_617_29503822.pdf)
- Analysis models (DFDs, statecharts, ERDs) as needed.  
- References to external standards and APIs.

***

## 3. Expressing functional requirements: formats and when to use them

This section compares the main forms you mentioned, focusing on structure, suitability, and edge/failure-mode capture.

### 3.1 Classic "shall" statements

**Structure/template**

A well-formed functional requirement per IEEE/INCOSE looks like:

> *The \<system> shall \<action verb> \<object> \<qualifiers / conditions>.*

Example (with EARS-style condition):

> When the user submits a transfer request, the system shall validate the source and destination accounts and either schedule or reject the transfer with a reason code.

Standards stress: necessary, singular, bounded, implementation-free, verifiable. [cwnp](https://www.cwnp.com/req-eng/)

**Strengths**

- Works well in regulated & contract-heavy contexts; directly traceable to tests.  
- Flexible: can be combined with tables, models, and scenarios. [pnsqc](https://www.pnsqc.org/docs/PNSQC2023RequirementsKarl_Wiegers.pdf)

**Weaknesses**

- Easy to write unreadable "god" requirements (too long, multiple branches). [businessanalystblog.squarespace](https://businessanalystblog.squarespace.com/s/Karl-Wiegers-Writing-High-Quality-Requirements-1-y5vu.pdf)
- Edge cases are often missed ("else" conditions, boundary cases), unless explicitly decomposed or coupled with structured patterns. [businessanalystblog.squarespace](https://businessanalystblog.squarespace.com/s/Karl-Wiegers-Writing-High-Quality-Requirements-1-y5vu.pdf)

**Best use**

- System-level and component-level requirements that must live as a long-term contract.  
- Good in combination with EARS templates (see below) to impose structure on shall-statements.

***

### 3.2 Alistair Cockburn's fully dressed use cases

**Structure**

Cockburn's fully dressed template includes: [cis.bentley](https://cis.bentley.edu/lwaguespack/CS360_Site/Downloads_files/Use%20Case%20Template%20(Cockburn).pdf)

- Name (goal)  
- Scope, level  
- Primary actor, stakeholders and interests  
- Preconditions, minimal guarantees, success guarantees  
- Trigger  
- Main success scenario (numbered steps, actor–system dialogue)  
- Extensions (for each step: condition → alternative steps or separate use case)  
- Special requirements (NFRs tied to this use case)  

Example extension entry:

> 7a. [Step 7] If payment authorization fails, system logs failure and returns error message to user.

**Strengths**

- Forces explicit modeling of **extension conditions** – alternative and failure flows, where a lot of complexity lives. [kurzy.kpi.fei.tuke](https://kurzy.kpi.fei.tuke.sk/zsi/resources/CockburnBookDraft.pdf)
- Naturally actor- and goal-centric; excellent for stakeholder conversations and discovering missing behavior.  

**Weaknesses**

- Heavyweight if used for every small feature; tends to atrophy in fast-moving agile teams.  
- Hard to integrate directly with code-level acceptance tests without extra mapping.

**Best use**

- A handful of **core, high-risk or complex workflows** (e.g., "Submit Claim", "Process Payment") in the SRS or supporting docs.  
- For greenfield systems, use them early to discover edge cases and then degrade details into stories, scenarios, and shall-statements.

***

### 3.3 User stories with acceptance criteria

**Structure**

Canonical user story:

> As a \<type of user>, I want \<goal> so that \<business value>.

Plus acceptance criteria, often in bullet form or Given–When–Then. [blog.logrocket](https://blog.logrocket.com/product-management/writing-meaningful-user-stories-invest-principle/)

Example:

> As a registered customer, I want to reset my password so that I can regain access if I forget it.  
> **Acceptance criteria:**  
> - If the email is registered, a reset link is sent and is valid for 24 hours.  
> - If the email is not registered, the system does not reveal that and shows a generic message.  
> - Reset link can only be used once.

**Strengths**

- Naturally aligns with agile backlogs and team planning.  
- INVEST heuristics (Independent, Negotiable, Valuable, Estimable, Small, Testable) give a good quality checklist. [devagentix](https://www.devagentix.com/blog/invest-criteria-user-stories)

**Weaknesses**

- As a "requirements artifact", stories are weak without strong acceptance criteria; they are deliberately placeholders for conversation.  
- Stories alone are not a good long-term contract; they change frequently and often lack system-wide constraints or invariants.

**Best use**

- Backlog-level functional decomposition.  
- In the SRS, reference epics/stories from higher-level capabilities but don't embed all story details.

***

### 3.4 Specification by Example (SbE, Gojko Adzic)

**Structure**

SbE uses concrete examples/scenarios, typically in Gherkin:

> Given \<preconditions>  
> When \<action>  
> Then \<post-condition>

These examples serve simultaneously as requirements, tests, and documentation. [fraktalio](https://fraktalio.com/blog/specification-by-example.html)

Example (edge and success cases):

- **Success:**  
  - Given an accepted order  
  - When it is marked as prepared  
  - Then the order state is "Prepared".

- **Error:**  
  - Given a placed but not accepted order  
  - When it is marked as prepared  
  - Then the system rejects the action with reason "OrderNotAccepted". [fraktalio](https://fraktalio.com/blog/specification-by-example.html)

**Evidence of effectiveness**

Adzic's work is based on multiple industrial case studies; teams report that SbE improves shared understanding, reduces rework, and is one of the few requirements techniques that works well in short iterations. [goodreads](https://www.goodreads.com/book/show/10288718-specification-by-example)

**Strengths**

- Excellent for covering edge cases and subtle business rules via concrete data combinations.  
- Direct tie-in to automated tests (BDD) and living documentation.

**Weaknesses**

- Can lead to an explosion of scenarios if not curated (requires refactoring of examples).  
- Poor at capturing high-level system scope on its own.

**Best use**

- As the **primary vehicle for detailed functional behavior and regression tests**, referenced from SRS requirements.  
- Especially valuable for domains with rich business rules (pricing, eligibility, workflows).

***

### 3.5 EARS (Easy Approach to Requirements Syntax)

**Structure**

EARS defines patterns for writing structured requirements: [reqassist](https://reqassist.com/blog/ears-requirements-syntax)

- **Ubiquitous:**  
  - The \<system> shall \<response>.  
- **Event-driven:**  
  - When \<trigger>, the \<system> shall \<response>.  
- **State-driven:**  
  - While \<state>, the \<system> shall \<response>.  
- **Optional feature:**  
  - Where \<feature is present>, the \<system> shall \<response>.  
- **Unwanted behavior:**  
  - If \<undesired event / fault>, then the \<system> shall \<response>. [ccy05327.github](https://ccy05327.github.io/SDD/08-PDF/Easy%20Approach%20to%20Requirements%20Syntax%20(EARS).pdf)

The "unwanted behavior" pattern explicitly targets failures, disturbances, deviations, and unexpected interactions. [ccy05327.github](https://ccy05327.github.io/SDD/08-PDF/Easy%20Approach%20to%20Requirements%20Syntax%20(EARS).pdf)

**Evidence**

EARS originated at Rolls-Royce and has been adopted in safety-critical domains; reports (e.g., Mavin et al. and practitioner slide decks) show improved clarity, fewer omissions, and successful industrial adoption at companies like Intel. [slideshare](https://www.slideshare.net/slideshow/ears-the-easy-approach-to-requirements-syntax/51558506)

**Strengths**

- Enforces a consistent shape for requirements; reduces ambiguity.  
- Explicit pattern for unwanted behaviors, which are a major source of rework. [ccy05327.github](https://ccy05327.github.io/SDD/08-PDF/Easy%20Approach%20to%20Requirements%20Syntax%20(EARS).pdf)
- Plays nicely with both "shall" statements and INCOSE/29148 quality rules.

**Weaknesses**

- Requires some training and discipline; teams may initially fight the structure.  
- Does not in itself manage priority or dependencies – you still need attributes.

**Best use**

- As the **default textual requirement pattern** for functional behavior in the SRS.  
- Especially for edge cases and error handling: use the EARS "If … then …" unwanted-behavior pattern.

***

### 3.6 When to use which (summary)

- **SRS-level contract:**  
  - Use **EARS-structured shall-statements** as the backbone.  
  - For a few key workflows, supplement with **fully dressed use cases** for discovery and stakeholder communication.  
- **Agile delivery level:**  
  - Use **user stories + acceptance criteria** to manage work.  
  - Use **Specification by Example** to express acceptance tests and edge cases, referencing SRS requirements.  
- **Safety/critical / interface-heavy areas:**  
  - Prefer **EARS + SbE** and fully dressed use cases with explicit extension conditions.

***

## 4. Writing measurable NFRs: patterns and examples

### 4.1 Completeness checklist via ISO/IEC 25010:2023

ISO/IEC 25010:2023 defines a product quality model with 9 characteristics: functional suitability, performance efficiency, compatibility, interaction capability (usability), reliability, security, maintainability, flexibility (portability), and safety, each with subcharacteristics. [webstore.iec](https://webstore.iec.ch/en/publication/90024)

Use these as a **checklist** to ensure you ask "do we have measurable requirements?" in each relevant area.

### 4.2 Quality Attribute Scenarios (SEI) and SLO/SLI patterns

The SEI's quality attribute scenario template decomposes each NFR into: [people.ece.ubc](https://people.ece.ubc.ca/matei/EECE417/BASS/ch04lev1sec4.html)

1. Source of stimulus (who/what triggers it)  
2. Stimulus (event)  
3. Environment (normal/peak/failure)  
4. Artifact (system/component)  
5. Response (what the system does)  
6. Response measure (how you know it's good enough)

Google's SRE practice formulates SLOs as **numeric targets on SLIs**, with error budgets derived from them (e.g., 99.9% success ratio → 0.1% error budget). [sre](https://sre.google/workbook/implementing-slos/)

Volere's "fit criterion" is essentially the response measure: a precise test that tells you if the requirement is met (e.g., max weight, dimensions, compliance certificate). [modernrequirements](https://www.modernrequirements.com/blogs/volere-requirements-specification-template/)

Wiegers emphasizes that quality requirements must be testable and encourages patterns (e.g., Planguage-like forms) to express measurable constraints. [ptgmedia.pearsoncmg](https://ptgmedia.pearsoncmg.com/images/9780735679665/samplepages/9780735679665.pdf)

### 4.3 Empirical evidence on poor NFRs

- A 2024 study on NFR classification notes that developers frequently overlook NFRs, specify them late, or treat them as secondary due to financial/technical constraints; NFRs are often scattered and subjective, complicating identification and consolidation. [nature](https://www.nature.com/articles/s41598-024-52802-0)
- An XP 2023 empirical study on NFR instability reports that >30% of NFRs were defined **after** delivery of software increments, and about one-third were revised or changed later; the authors conclude that NFRs are uncertain and change frequently, requiring agile approaches. [events.agilealliance](https://events.agilealliance.org/xp2023/session/1449857/an-empirical-study-about-the-instability-and-uncertainty-of-non-functional-requirements)
- Empirical work on NFRs in mobile development shows NFRs significantly impact cost, time, and quality, and argues they must be treated on par with functional requirements for business success. [clc.overdrive](https://clc.overdrive.com/clc-columbus/content/media/5915537)

**Takeaway:** If you do not specify critical NFRs early and measurably, they will surface as expensive architectural rework and operational incidents.

### 4.4 Before/after examples across attributes

Below is a sample of measurable rewrites (pattern: vague → testable scenario/fit criterion).

**Performance / Latency**

1. *Vague*: "The system shall be fast."  
   *Measurable*:  
   - Under normal weekday load (≤ 100 RPS), 95% of `POST /checkout` requests shall complete within 800 ms as measured at the public HTTP endpoint over any 5-minute window. [sre](https://sre.google/workbook/implementing-slos/)

2. *Vague*: "Search results should appear quickly."  
   *Measurable*:  
   - For search queries with result set size ≤ 100 items, 99% of `GET /search` responses shall be returned within 1.2 seconds over a rolling 30-day period.

**Availability / Reliability**

3. *Vague*: "The service shall be highly available."  
   *Measurable*:  
   - The public API shall have at least 99.9% successful responses (2xx) over all 2xx+5xx responses, measured monthly; this implies an availability SLO of 99.9% and an error budget of 0.1%. [sre](https://sre.google/workbook/error-budget-policy/)

4. *Vague*: "The system shall recover quickly from failures."  
   *Measurable*:  
   - For a single application server failure, the system shall restore full API availability (meeting the 99.9% SLO) within 5 minutes, as evidenced by monitoring logs.

**Throughput / Scalability**

5. *Vague*: "The system must scale to many users."  
   *Measurable*:  
   - The system shall sustain at least 500 concurrent logged-in users performing an average of 3 operations/minute each while meeting defined latency SLOs, on the reference production configuration.

**Security**

6. *Vague*: "The system shall be secure."  
   *Measurable*:  
   - All external HTTP endpoints shall enforce TLS 1.2 or higher and reject connections using ciphers not on the approved list.  
   - The system shall pass quarterly third-party penetration tests with no open critical or high-severity findings according to OWASP risk ratings.

**Data Protection / Privacy**

7. *Vague*: "User data shall be protected."  
   *Measurable*:  
   - All user PII fields defined in the data classification policy shall be stored encrypted at rest using AES-256 (or stronger) and transmitted only over TLS; verification via configuration inspection and automated scans.

**Usability / Interaction capability**

8. *Vague*: "The UI should be easy to use."  
   *Measurable*:  
   - In usability tests with at least 10 target users, at least 90% shall be able to complete the "create new order" task within 3 minutes without assistance and with no more than one error per task.

**Maintainability**

9. *Vague*: "The system shall be easy to maintain."  
   *Measurable*:  
   - For 80% of change requests that modify a single business rule, the required code change shall affect at most one module and be deployed to production within 2 working days, given an existing automated test suite.

**Portability / Flexibility**

10. *Vague*: "The system shall be portable."  
    *Measurable*:  
    - The application shall run on both Kubernetes clusters conforming to CNCF-conformant distributions A and B without code changes, with configuration differences limited to Kubernetes resource manifests and environment variables.

**Observability**

11. *Vague*: "The system shall be monitorable."  
    *Measurable*:  
    - All public API endpoints shall emit structured logs containing request ID, user ID (if present), HTTP verb, path, status code, and latency, with at least 99% of requests successfully logged and available in the central log system within 60 seconds.

In your SRS, each NFR should be written as a scenario (SEI pattern) with an explicit measure and threshold; optionally add an SLO+error budget where operationally relevant.

***

## 5. External interfaces and data contracts

### 5.1 What the standards say

IEEE 830 dedicates a "External Interface Requirements" section to: [cse.uaa.alaska](http://www.cse.uaa.alaska.edu/~afkjm/csce401/IEEE830.pdf)

- User interfaces  
- Hardware interfaces  
- Software interfaces  
- Communication interfaces  

Wiegers's SRS template has a similar section 3 (External Interface Requirements). [coursehero](https://www.coursehero.com/file/197704060/Software-Requirements-Specificationdocx/)
29148 likewise expects requirements on interfaces as part of system/software requirements. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

Fundamentally, these are **behavioral contracts** at system boundaries, not implementation details.

### 5.2 What to specify

For each external interface, capture:

- **Purpose**: why the interface exists and what business goal it supports.  
- **Inputs**:
  - Types (including ranges, allowed sets, encoding/format), mandatory vs optional.  
  - Validation rules and invariants.  
- **Outputs**:
  - Types and semantics, including ordering guarantees and idempotency.  
- **Error behavior**:
  - Treatment of invalid input, unavailable dependencies, timeouts.  
  - Fault codes, error response structure, and when they are emitted.  
- **Non-functional constraints** for the interface:
  - Latency SLOs, throughput, rate limits, availability, data retention.  

Keep these **implementation-agnostic** where possible (e.g., "returns an error response with machine-readable code and human-readable message") and delegate exact formats to interface specs like OpenAPI.

### 5.3 Spec-first APIs (OpenAPI/AsyncAPI)

In API-centric teams, it is effective to treat the OpenAPI/AsyncAPI spec as the executable contract: [strapi](https://strapi.io/blog/api-first-development-guide)

- Define endpoints, methods, request/response schemas, authentication, and error schemas *before* implementation.  
- Use code generation and contract testing to ensure code does not drift from the spec.  
- Enforce spec changes in CI (e.g., failing builds on breaking changes).

In the SRS, you can:

- State **requirements on the API** (e.g., required resources, operations, invariants, NFRs).  
- Declare that the OpenAPI spec at `path/to/spec.yaml` is the normative contract for those interfaces and must conform to SRS requirements (e.g., must surface specific error codes, fields, and SLO-related headers).

This avoids prematurely dictating internal architecture or DB schema while still giving a precise, machine-checkable interface contract.

***

## 6. Requirement atomicity, identification, attributes, and prioritization

### 6.1 Atomic, uniquely identified requirements

INCOSE explicitly requires each requirement to be **singular** and uniquely identified. [archive.stmarys-ca](https://archive.stmarys-ca.edu/archive-library-410/incose-guide-for-writing-requirements.pdf)

- **Atomicity / singularity:**  
  - No combining multiple independent behaviors with "and/or" in one statement.  
  - If a condition has multiple outcomes, write multiple requirements or use structured representations (tables, EARS patterns). [incose](https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_products/incose_rwg_gtwr_summary_sheet_2022.pdf)

- **Unique IDs:**  
  - IEEE 830 and Wiegers recommend unique sequence numbers for each requirement. [site.uottawa](https://www.site.uottawa.ca/~bochmann/SEG3101/Notes/SEG3101-ch3-2%20-%20Requirements%20documentation%20standards%20-%20IEEE830.pdf)
  - Common patterns:
    - Hierarchical: `FR-3.4.2` tied to section 3.4.2.  
    - Semantic tags: `PRINT.COPIES.CONFIRM` (Wiegers-style). [businessanalystblog.squarespace](https://businessanalystblog.squarespace.com/s/Karl-Wiegers-Writing-High-Quality-Requirements-1-y5vu.pdf)
    - Hybrid: `REQ-FUNC-001`, `REQ-NFR-AVAIL-003`.

Unique IDs are essential to maintain traceability matrices as required by 29148. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

### 6.2 Requirement attributes

INCOSE's guide lists a minimum attribute set for each requirement: rationale, trace to parent, trace to source, verification method; additional attributes include risk, status, allocation, and modes. [moodle.insa-toulouse](https://moodle.insa-toulouse.fr/pluginfile.php/121422/mod_folder/content/0/INCOSE%20Guide%20for%20Writing%20Requirements.pdf)

ReqView and similar tools show typical attribute sets: ID, description, type, priority, urgency/severity, acceptance criteria, verification method, status, effort, risk, target release. [reqview](https://www.reqview.com/papers/ReqView-Custom_Requirement_Attributes.pdf)

29148 emphasizes attributes that support requirements engineering and assurance, including origin, verification method, and links to business/mission requirements. [standards.ieee](https://standards.ieee.org/ieee/29148/6937/)

**Recommended attributes in your SRS/backlog tooling:**

- ID  
- Short title  
- Statement (the requirement)  
- Type (functional, NFR, interface, constraint, assumption)  
- Priority (e.g., MoSCoW + numeric rank)  
- Source (stakeholder, standard, ADR, incident, regulation)  
- Rationale (why this exists)  
- Status (proposed, approved, implemented, verified, rejected)  
- Owner  
- Risk level (e.g., impact on safety/compliance/architecture)  
- Verification method (test, analysis, inspection, demonstration)  
- Trace links:
  - Parent requirement / business goal  
  - Child requirements / design items  
  - Test cases, SbE scenarios, monitors (SLIs/SLOs)

### 6.3 Prioritization (MoSCoW and beyond)

MoSCoW (Must, Should, Could, Won't) is widely used to categorize requirements into essential, important, desirable, and out-of-scope. [yondar](https://yondar.org/toolkit/moscow-must-or-should-could-or-would/)

Guidelines:

- Limit "Must" items to what is truly critical (often ~60% of effort or less for a release). [productlift](https://www.productlift.dev/blog/moscow-prioritization)
- In an SRS context, a requirement can have a **business priority** (MoSCoW) plus a **safety/regulatory criticality** that may override business preferences.

### 6.4 Evidence that structure and attributes improve outcomes

- Kamata & Tamai's RE 2007 study of 32 projects mapped SRS quality to IEEE 830 sections and found:
  - A relatively small set of SRS items (notably Section 1 context and some specific requirement categories) had strong impact on project success or failure.  
  - "Normal" projects tended to have balanced, high-quality descriptions across sections; overrun projects often had poor Section 1 (purpose/context) even when functional sections were rich. [semanticscholar](https://www.semanticscholar.org/paper/How-Does-Requirements-Quality-Relate-to-Project-or-Kamata-Tamai/888732d31342f47af4cdfb0335f9d6f670b1366f)

- A 2015 paper *"Does Quality of Requirements Specifications matter? Combined Results of Two Empirical Studies"* concluded that:
  - SRS usage and quality impact subsequent activities, especially in safety-critical domains.  
  - Certain pragmatic defects are less harmful, but completeness and clarity where SRS is heavily used are critical. [arxiv](https://arxiv.org/pdf/1702.07656.pdf)

- Work on SRS evaluation and metrics (e.g., Stephen et al., assessing completeness, correctness, preciseness, consistency against IEEE 830) demonstrates that measurable SRS quality can predict project outcomes and that structured templates and boilerplates (e.g., Requirement Boilerplate) help achieve consistency. [ijaseit.insightsociety](https://ijaseit.insightsociety.org/index.php/ijaseit/article/download/10186/pdf_1484/27661)

- Studies on requirements relationships knowledge found significant impacts of understanding requirement relationships on both requirements quality and project success. [ceur-ws](https://ceur-ws.org/Vol-3062/Paper07_QuASoQ.pdf)

In practice: atomic, well-identified requirements with attributes and clear relationships are necessary to maintain traceability and to analyze changes' impacts—especially on NFRs and external contracts.

***

## 7. Managing assumptions, constraints, risks, and TBDs

### 7.1 Explicit assumptions and dependencies

Wiegers's SRS template has a dedicated section 2.7 "Assumptions and Dependencies", with examples like reliance on third-party components, environment constraints, and external systems; he stresses that incorrect or changing assumptions can significantly affect the project. [wpollock](https://wpollock.com/AJava/srs_template_IEEE.pdf)

Best practice:

- Capture each assumption as a structured item:
  - ID, statement, rationale, potential impact if false, owner, review date.  
- Link assumptions to the requirements they influence.

### 7.2 Constraints

Volere treats constraints as atomic requirements using the same shell, with description, rationale, and fit criterion (e.g., "must operate on Windows XP", with fit criterion "approved as XP compliant by MS testing group"). [cs.uic](https://www.cs.uic.edu/~i440/VolereMaterials/templateArchive16/c%20Volere%20template16.pdf)

In the SRS:

- List constraints in a dedicated section but treat each as a requirement with attributes.  
- Be careful to distinguish **true constraints** (mandated by external factors) from preferences or design choices.

### 7.3 TBDs and explicit uncertainty

Wiegers's Appendix C: "To Be Determined List" collects all TBD markers into a numbered list for tracking to closure. [wpollock](https://wpollock.com/AJava/srs_template_IEEE.pdf)

Good practice:

- Use "TBD" as a placeholder **only with an ID or tag**, not as a silent omission.  
- Maintain a log that includes:
  - TBD ID, location in SRS, description, owner, expected resolution date, resolution status.

INCOSE stresses feasibility both at individual and set levels – an incomplete or infeasible set of requirements must be treated as such and addressed; explicit unknowns are part of that. [moodle.insa-toulouse](https://moodle.insa-toulouse.fr/pluginfile.php/121422/mod_folder/content/0/INCOSE%20Guide%20for%20Writing%20Requirements.pdf)

In agile contexts, treat significant TBDs and assumptions as:

- **Spike stories** (investigation tasks) in the backlog.  
- **Risks** in your risk register, with mitigation plans.

This "explicit uncertainty" approach prevents false confidence and supports informed decision-making.

***

## 8. SRS templates and empirical evidence on structure

### 8.1 IEEE 830 / Wiegers template

Wiegers's widely used SRS template follows IEEE 830 closely: [coursehero](https://www.coursehero.com/file/197704060/Software-Requirements-Specificationdocx/)

1. Introduction  
2. Overall Description  
3. External Interface Requirements  
4. System Features (each feature with description, functional requirements)  
5. Other Nonfunctional Requirements  
6. Other Requirements  
Appendices: Glossary, Analysis Models, TBD List

It's light enough to adapt but complete enough for most business systems.

### 8.2 Volere template

Volere defines:

- A **Snow Card** ("atomic requirements shell") per requirement: ID, description, type, rationale, originator, fit criterion, priority, conflicts, supporting materials, history. [scribd](https://www.scribd.com/document/844557196/Snow-Card)
- A structured specification into product goals, functional requirements, constraints, and quality requirements.

The strong emphasis on fit criteria and rationale is particularly useful for NFRs and constraints.

### 8.3 29148-based templates

Public derivative templates show 29148-based SRS structures that are similar but more explicit about:

- Stakeholder requirements vs system/software requirements  
- Modes/states, operational scenarios  
- Verification and validation considerations. [well-architected-guide](https://www.well-architected-guide.com/documents/iso-iec-ieee-29148-template/)

### 8.4 Empirical correlation with project success

Kamata & Tamai's 32-project study is the best-known empirical link between IEEE 830-structured SRS quality and project outcomes: [research.ibm](https://research.ibm.com/publications/how-does-requirements-quality-relate-to-project-success-or-failure)

- Rich and balanced SRS descriptions, especially in Section 1 (purpose, scope, overview), were associated with projects staying within cost and schedule.  
- Overemphasis on detailed functions with weak context/overview correlated with overruns.

Additional work (e.g., Stephen et al. measuring IEEE 830-based SRS quality properties) supports the idea that measurable completeness/correctness/consistency of SRS content can serve as an early predictor of project risk. [ijaseit.insightsociety](https://ijaseit.insightsociety.org/index.php/ijaseit/article/download/10186/pdf_1484/27661)

**Implication for your template:**  
Invest serious effort in **context, goals, and constraints** (Sections 1–3 & 7) rather than only elaborating functional details.

***

## 9. SRS and agile backlogs: a hybrid model

### 9.1 RE@Agile and agile RE guidance

IREB's RE@Agile materials describe a hybrid approach: [compliance-technologies](https://www.compliance-technologies.com/DS/handbook_cpre_al_re@agile_v1.0.pdf)

- Use RE techniques to gain a solid understanding of the product at an appropriate level of abstraction and to seed an initial backlog (epics, high-level use cases).  
- Do **not** aim for a fully detailed upfront SRS; instead, practice continuous refinement (backlog grooming, Definition of Ready, incremental clarification).  
- Use agile iterations and product increments to get feedback and uncover unknown requirements.

### 9.2 Recommended hybrid approach

For a greenfield project:

- Maintain a **lean SRS** (as per Section 2) with:
  - Context, stakeholders, goals.  
  - Boundaries and external interfaces.  
  - Cross-cutting business rules and constraints.  
  - Global NFRs (latency, availability, security, data retention, compliance).  
  - Critical capabilities and invariants.

- Maintain a **backlog** for:
  - Detailed functional stories and tasks.  
  - Specification by Example scenarios and tests.  
  - Spikes to resolve TBDs and validate assumptions.  
  - Architectural experiments (if needed).

Use traceability links from:

- SRS **capabilities / high-level requirements → epics/stories** in the backlog. [re-magazine.ireb](https://re-magazine.ireb.org/articles/an-agile-lifecycle-for-requirements)
- NFRs in the SRS → "non-functional" backlog items and infrastructure/ops work (e.g., reliability stories tied to SLOs). [sastqb.org](https://sastqb.org.za/wp-content/uploads/2021/08/IREB-CPRE-RE@AGILE-PRIME_Syllabus_2020_v1.1.0.pdf)

### 9.3 Scaled frameworks (SAFe, LeSS, etc.)

Though not named explicitly in the sources above, the pattern in scaled frameworks is generally:

- An SRS-equivalent at solution/portfolio level (e.g., **Solution Intent** in SAFe) capturing global constraints, NFRs, and architectural runway.  
- Program/Team backlogs host detailed stories and features.  
- Traceability from solution-level requirements to program features and team stories is maintained.

Use the SRS as your **source of truth for system-wide constraints and quality requirements**, while the backlog is the execution vehicle.

***

## 10. Traceability model: from business goals to tests

Using 29148's traceability matrix concept and INCOSE's attributes for trace-to-parent and trace-to-source, you can define a 4–5 level model: [incose](https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_products/incose_rwg_gtwr_summary_sheet_2022.pdf)

1. **Level 1 – Business/Mission Goals**  
   - E.g., "Reduce average claim processing time by 50% within 12 months."  

2. **Level 2 – Business Requirements / Capabilities**  
   - E.g., "Provide online self-service claim submission and status tracking."

3. **Level 3 – System Requirements (SRS)**  
   - Functional: "When a customer submits a claim, the system shall assign a claim ID and present an estimated processing time."  
   - NFRs: "Under normal load, 95% of claim submissions shall complete within 1s."

4. **Level 4 – Design & Implementation Artifacts**  
   - Components, APIs, messages, DB schemas, configuration items.  
   - ADRs that choose specific patterns/technologies.

5. **Level 5 – Verification & Operational Evidence**  
   - Test cases (unit, integration, system, performance) and SbE scenarios.  
   - Monitoring SLIs/SLOs and reports (e.g., monthly SLO compliance).

**Traceability practices:**

- Maintain a **Requirements Traceability Matrix (RTM)** where each SRS requirement has:
  - Links upward to one or more business goals / capability requirements.  
  - Links downward to tests, code modules, or monitoring checks. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- Use requirement attributes `TraceToParent` and `TraceToSource` as per INCOSE. [incose](https://www.incose.org/docs/default-source/working-groups/requirements-wg/rwg_products/incose_rwg_gtwr_summary_sheet_2022.pdf)
- For NFRs expressed as SLOs, link:
  - NFR → SLO definition → SLIs in monitoring → automated checks. [sre](https://sre.google/workbook/error-budget-policy/)

This makes it possible to ask:

- "Which tests verify that this NFR is met?"  
- "Which user stories and components implement this capability?"  
- "Which business goal will be impacted if we change this requirement?"

***

## 11. SRS maintenance, versioning, and review practices

### 11.1 Maintenance and versioning

- Treat the SRS as a **version-controlled artifact** (Git, etc.), with:
  - Tagged baselines (e.g., v1.0 for initial release, v1.1 for next major increment).  
  - Change history referencing issue IDs, ADRs, and backlog items.

- Change control:
  - For critical requirements (safety, compliance, external interfaces, major NFRs), require a **formal change review** and impact analysis.  
  - For minor or local requirements, allow more lightweight changes but always keep traceability updated.

### 11.2 Reviews and quality checks

Regularly review SRS updates against:

- **IEEE 830/29148 quality criteria** (correct, unambiguous, complete, consistent, ranked, verifiable, modifiable, traceable; singular, bounded, necessary, feasible). [standards.ieee](https://standards.ieee.org/ieee/29148/6937/)
- **INCOSE rules** for individual requirement statements and sets. [moodle.insa-toulouse](https://moodle.insa-toulouse.fr/pluginfile.php/121422/mod_folder/content/0/INCOSE%20Guide%20for%20Writing%20Requirements.pdf)
- **ISO 25010** checklist to ensure NFR coverage. [iso25000](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)

In practice:

- Use checklists in review meetings (requirements reviews, architecture reviews).  
- Apply static checks where possible (e.g., detecting vague terms, "and/or" misuse, boundary mismatches) inspired by IEEE 830, INCOSE, and studies on requirement boilerplates. [ijaseit.insightsociety](https://ijaseit.insightsociety.org/index.php/ijaseit/article/download/10186/pdf_1484/27661)

### 11.3 Synchronizing SRS and backlog

- Establish a **working agreement**:
  - Any new global constraint, interface contract, or NFR discovered during sprints ⇒ must be reflected in the SRS.  
  - Any change in SRS that affects implementation ⇒ must be reflected as backlog items and test changes.

- Periodic synchronization (e.g., once per iteration or release):
  - Confirm that all "Must" SRS requirements for the release have implementing stories and tests.  
  - Confirm that all implemented epics/stories trace back to approved SRS requirements or are explicitly exploratory.

***

## 12. Summary: practical starting point

For a greenfield project:

1. **Adopt a lean 29148/IEEE 830–aligned SRS template** (Section 2), emphasizing context, interfaces, NFRs, and constraints, plus traceability attributes.  
2. **Express functional requirements using EARS-patterned shall-statements** as your textual backbone, augmented with:
   - A few **fully dressed use cases** for core flows.  
   - **User stories + SbE scenarios** in the backlog for detailed behavior and tests.  
3. **Treat NFRs as first-class, measurable scenarios** organized by ISO 25010, using SEI quality attribute scenario structure and SLO/SLI-style measures, with Volere-style fit criteria.  
4. **Document external interfaces as behavioral contracts**, supplemented with spec-first OpenAPI/AsyncAPI artifacts where APIs are central.  
5. **Enforce atomicity, unique IDs, and attributes** per INCOSE/29148 and use MoSCoW (and similar) for prioritization; leverage traceability matrices to connect goals → requirements → tests.  
6. **Make assumptions, constraints, risks, and TBDs explicit**, with a TBD appendix and assumption/risk logs feeding into agile spikes and risks.  
7. **Integrate with agile backlogs** via a hybrid model: SRS = stable system contract; backlog = evolutionary delivery plan, connected by traceability.  
8. **Continuously maintain and review the SRS**, using standards-based checklists and empirical insights (like Kamata & Tamai) to focus on the sections and qualities that most strongly predict project success.

If you want, the next step could be to turn this into a concrete, project-ready SRS skeleton in Markdown (with example requirements for one imaginary system) that you can drop into your repo and evolve.

---

## Additional Research & Evidence

*Supplementary research and evidence from a second research pass.*

# Creating the Core Software Requirements Specification for a Greenfield Project

## What standards mean by an SRS and what "good" looks like

In modern requirements engineering standards, a Software Requirements Specification functions as the authoritative, implementation-agnostic behavioural contract for a specific piece of software: what it must do, what externally observable qualities it must exhibit, and what external interfaces it must expose. ISO/IEC/IEEE 29148:2018 defines a "software requirements specification" as a *structured collection* of essential requirements—functions, performance, design constraints, and attributes—*of the software and its external interfaces*. turn18view2

IEEE 830-1998 (retired) described a similar intent, emphasising that an SRS is a specification for a particular software product in a specific environment; it should define required functionality, external interfaces, performance, attributes, and constraints, while *avoiding embedding design or project-management content*. turn16view0

A key evolution is that ISO/IEC/IEEE 29148:2018 is not "just an SRS outline"; it is a broader, unified requirements engineering standard (process + information items) that explicitly replaced IEEE 830-1998 (and other older IEEE requirements standards). turn18view2

### Document-level quality criteria: IEEE 830-1998

IEEE 830-1998's widely taught SRS quality criteria are eight "-ilities" of the specification itself: **correct, unambiguous, complete, consistent, ranked (importance/stability), verifiable, modifiable, traceable**.  The standard gives operational definitions (e.g., "verifiable" means objectively checkable; it warns that unbounded words like "fast", "easy", "usually" are non-verifiable unless turned into measurable statements). 

### Requirement-statement quality criteria: ISO/IEC/IEEE 29148 and INCOSE

ISO/IEC/IEEE 29148:2018 shifts emphasis from "the document is good" to "each requirement (and the set) is well-formed," commonly summarised as nine essential properties for individual requirements (including being necessary, unambiguous, complete, singular, feasible, verifiable, correct, and conforming). turn18view2

INCOSE's "Guide to Writing Requirements" further operationalises quality at two levels: (1) individual need/requirement statements (e.g., unambiguous, complete, feasible, verifiable, correct, singular) and (2) requirement sets (e.g., complete and consistent as a set). turn10view1 It also argues that "priority/criticality" is often better conveyed via attributes than by weakening modal verbs in the statement itself (i.e., keep the statement declarative, manage "must vs should" structurally). 

Two implications for a greenfield SRS follow.

First, treat "quality" as a **verification-enabling property**: if a requirement cannot be verified, it is either ambiguous, not yet understood, or contains disguised design. IEEE 830 makes this explicit with its "verifiable" guidance; Wiegers and Volere provide pragmatic heuristics ("can we think of a small number of tests?" / "fit criterion"). turn19view4

Second, "traceability" is not a template section; it is a **data model** across requirements artefacts. This is consistent with how requirements traceability is defined in literature surveys (trace a requirement from emergence to fulfilment) and in requirements management handbooks focused on attributes and cross-references. turn20view3

## A recommended lean SRS structure for a greenfield project

A greenfield SRS should be "complete enough to be testable and contract-like," but "lean enough to avoid freezing premature decisions." Practically, that means: include stable context, boundaries, external interfaces, quality targets, and cross-cutting constraints early; defer UI mock fidelity, internal architecture, and data storage design unless they are true constraints. This aligns with both IEEE 830's warning against embedding design and ISO/IEC/IEEE 29148's approach to SRS content: define purpose/scope, product perspective and interfaces, constraints, assumptions/dependencies, and the requirements themselves. turn18view2

The template below is structured so that each requirement can be traced up to business goals and down to tests, while keeping implementation decisions out of the SRS.

### Recommended core SRS template with rationale and "include vs defer"

| SRS section | Why it exists (contract value) | Include now | Defer or move elsewhere |
|---|---|---|---|
| Document control and change history | Enables baselining, controlled evolution, auditability | Version, status (draft/baselined), approvers, change summary | Detailed project plan milestones (belongs outside SRS) turn18view0 |
| Purpose, scope, and non-goals | Prevents "scope creep by interpretation"; anchors traceability | Product name, what it does and does not do, intended audience turn18view2 | Delivery schedule, staffing, tooling (project constraints, not software requirements)  |
| Definitions and data glossary | Eliminates ambiguity and semantic drift | Domain glossary, canonical field names, units, time bases, ID formats, error-code meaning | Full schema design and physical DB layout unless mandated |
| Context and business goals | Strengthens backward traceability; reduces local optimisation | Business objectives/outcomes, success measures, primary risks/assumptions in business terms | Business case financial model detail (separate artefact) |
| Product perspective and system boundary | Prevents hidden integration work; defines "outside world" | System context diagram; externally visible interfaces; operating constraints and environments turn15view0 | Internal component decomposition (architecture doc) |
| Stakeholders and user classes | Unlocks precise functional/UX requirements and access control | User classes, privileges, frequency, safety/security roles  | UI design system specifics (separate UI spec) |
| Assumptions, constraints, dependencies | Makes uncertainty explicit; supports impact analysis | Regulatory/standard constraints, platform constraints, dependency SLAs, open assumptions | "TBD inside baselined requirements" (should be resolved pre-baseline) turn4search1 |
| Functional requirements | Defines behaviour without implementation | Requirements expressed in one (or a small set) of formats; each uniquely identified; edge cases included | Algorithm choices; database indexing; internal caching strategy (unless a declared constraint)  |
| Quality requirements (NFRs / quality attributes) | Prevents late discovery of "cross-cutting" drivers | Measurable targets using scenarios/SLOs/fit criteria mapped to ISO 25010 characteristics turn10view4turn25search3 |
| External interface requirements and data contracts | Enables independent implementation and testing; reduces integration failures | Inputs/outputs, semantics, invariants, error behaviour, versioning rules; API contract references turn10view8 | Internal service mesh topology; DB schema (unless contractually fixed) |
| Verification, acceptance, and traceability hooks | Ensures every requirement can be proven | Verification method per requirement; links to tests/monitoring; trace links to goals turn20view3 | Detailed test scripts (test plan / test cases live elsewhere) |
| Appendices: TBD/issue list, risk log, decision log | Keeps the SRS honest about unknowns | Centralised open issues list; decision placeholders; assumption log turn4search29 | Leaving unresolved items untracked |

Two empirically grounded nuances are worth making explicit. First, in a 32-project industrial study analysing SRS quality against IEEE 830 structure, projects with cost/time overruns were associated with poorer content in the early "context/overview" section—suggesting that *weak section 1 context can predict downstream failure even if functional sections are detailed*. turn10view5 Second, requirements specification defects can propagate into downstream artefacts (e.g., flawed test cases): controlled studies and surveys reported in requirements specification quality research show measurable downstream impact of requirement faults. 

## Choosing a format for functional requirements and capturing edge cases

No single representation dominates across all contexts. ISO/IEC/IEEE 29148 and INCOSE care less about which *format* you use and more that the requirement is unambiguous, singular, feasible, and verifiable, and that the set is complete and consistent. turn0search6 The right choice is therefore a *fit-to-risk* decision: pick a format that most reliably exposes ambiguity, edge cases, and verification criteria for your domain.

### Shall-statements

**Structure.** A disciplined version is: "The system shall \<observable behaviour\> [under \<conditions\>] [within \<measure\>]." IEEE 830 treats "shall meet" as the benchmark for correctness and demands measurability for verifiability. 

**Strengths.** They map cleanly to verification methods and traceability systems because they tend to be atomic and referenceable (one requirement ↔ one test cluster). This aligns with both IEEE 830's document criteria and ISO/IEC/IEEE 29148's emphasis on requirement attributes (verification method, trace links). turn18view1

**Failure modes.** In practice, shall-statements degrade into "shall be user-friendly/fast/secure" unless forced through measurement (see the quality-requirements section). IEEE 830 explicitly warns that vague qualifiers are non-verifiable. 

**Edge cases.** Must be written deliberately as separate requirements or explicit "error behaviours" per interface/feature (invalid input, timeouts, partial failure, retries), otherwise they remain implicit.

### Fully dressed use cases (Cockburn-style)

**Structure.** A fully dressed use case centres on a goal, with a **Main Success Scenario** and an explicit **Extensions** section for alternative paths and errors; guidance includes brainstorming and listing extension conditions exhaustively, then writing handling steps that rejoin the main flow or end in failure. turn2search9

**Strengths.** Use cases excel at surfacing interaction-level edge cases because the format structurally asks "what can go differently here?" The extension mechanism is a direct prompt for exception handling, retries, cancellations, validation failures, and alternative success paths. turn2search17

**Evidence and downstream impact.** Empirical work on requirements specification quality has investigated how defects in use-case specifications influence the quality of derived test cases, demonstrating that factual faults can measurably lead to flawed tests. 

**When to use.** Best when user–system interaction, workflow, and stateful behaviour dominate; also when stakeholders validate scenarios more reliably than isolated atomic requirements.

### User stories with acceptance criteria

**Structure.** Canonical template: "As a \<who\>, I want \<what\> so that \<why\>."  The SRS-relevant part is not the sentence itself; it is the acceptance criteria that makes the story testable without prescribing implementation, consistent with the "outcome-focused" definition of acceptance criteria. turn10view7

**Evidence on effectiveness and risks.** Research on user stories observes that they are widely adopted but often poorly written in practice; the Quality User Story (QUS) framework explicitly targets common defects (including "atomicity") and reports an evaluation on over a thousand stories from multiple companies.  The IREB RE@Agile handbook similarly cautions that the written part of a user story is incomplete until the conversation occurs, i.e., it is a "pointer," not a full specification. 

**When to use.** Best for fast-moving product discovery and backlog management, especially when combined with a lean SRS for stable constraints and cross-cutting requirements (see the agile section).

**Edge cases.** Capture via acceptance criteria and examples. Without explicit acceptance criteria (including negative scenarios), the "story" format systematically under-specifies failure modes. turn19view2

### Specification by Example

**Structure.** Collaborative discovery of examples that become acceptance tests and "living documentation." The method is presented as case-study-driven and oriented toward reducing rework and clarifying expectations. turn2search14

**Evidence base.** Much of the published support is practice- and case-study-oriented (e.g., reported case studies across many projects), rather than controlled comparisons against alternative notations. turn2search14

**When to use.** High value when business rules and data-driven behaviours dominate (pricing, eligibility, policy rules, calculations), because examples naturally encode edge cases and counterexamples.

**Edge cases.** Typically captured as explicit example tables and negative examples (invalid inputs, boundary values, missing data), which translate directly into test cases.

### EARS (Easy Approach to Requirements Syntax)

**Structure.** EARS is a controlled natural language approach with a small set of templates ("ubiquitous," "event-driven," "state-driven," "optional feature," and "unwanted behaviour"). Its "unwanted behaviour" form explicitly specifies how the system shall respond to undesired events using an IF/THEN structure. turn2search16

**Evidence.** The original EARS publication reports that applying the ruleset produced qualitative and quantitative improvements over conventional textual requirements in a case study context. turn2search4

**When to use.** Particularly strong when you need (a) requirements that remain text-based for broad stakeholder readability, but (b) reduced ambiguity and better coverage of triggers/states/errors.

**Edge cases.** EARS' "unwanted behaviour requirements" create an explicit home for error conditions, faults, and invalid inputs—precisely the cases that are often omitted when teams only specify the "happy path." turn19view3

### A pragmatic selection rule for greenfield work

A robust hybrid pattern is: use **(1) a small number of use cases or journeys** to define end-to-end flows and systematically elicit extensions, combined with **(2) EARS/shall-statements** for atomic, testable behavioural requirements, and **(3) examples/acceptance criteria** for detailed business rules. This explicitly aligns with the evidence that requirement quality is less about notation ideology and more about defect prevention, verifiability, and completeness. turn19view2

## Turning non-functional requirements into measurable, verifiable targets

The most common failure mode for NFRs is that they appear as vague adjectives ("fast", "secure", "scalable") and remain untestable until late in delivery—at which point they become expensive architectural rework. IEEE 830 warns that unverifiable statements are effectively defective requirements.  Empirical research on under-documentation of NFRs (treated as an indicator of technical debt) reinforces that NFRs are often treated as second-class relative to functional requirements, and it argues organisations should invest in "adequate documentation of NFRs" because it "will pay off."  Evidence from agile-oriented studies also notes that NFRs are commonly neglected until later stages, and that this neglect can contribute to failure. 

A practically effective approach is to specify quality requirements using three complementary lenses:

### ISO/IEC 25010:2023 as the completeness checklist

ISO/IEC 25010:2023 revises the software product quality model: it adds **Safety** as a ninth quality characteristic, and it renames **Usability → Interaction capability** and **Portability → Flexibility**, among other updates. turn25search3 In a greenfield project, you can use the updated set of top-level characteristics as a "mind-map" to ensure you have deliberately decided what matters and what does not for this product (rather than discovering "oh, we needed scalability" in performance testing).

A widely circulated interpretation of the ISO/IEC 25010:2023 product quality characteristics (reflecting these renamed and added characteristics) is: **functional suitability, performance efficiency, compatibility, interaction capability, reliability, security, maintainability, flexibility, safety**. turn22view2

### SEI quality attribute scenarios for making "quality" actionable

The SEI Quality Attribute Workshop (QAW) is designed to identify key quality attributes derived from business and mission goals *before* architecture exists—precisely the moment when an SRS must define quality drivers without prescribing design. turn1search1

### SLO/SLI language for operationally meaningful quality targets

Google's SRE practice formalises the idea "choose measurable targets users care about" by expressing an SLO as a target value or range for a measurable SLI, often in a simple inequality form (e.g., SLI ≤ target).  The SRE "error budget" concept then turns the SLO into an explicit budget of allowable unreliability over a period, creating an objective governance mechanism for stability vs feature delivery trade-offs. turn19view1

### Wiegers and Volere: tactics for testability

Wiegers' practical guidance emphasises rewriting requirements so they become verifiable and warns against assuming you can create a "perfect" SRS; it provides concrete rewrite patterns for ambiguous statements.  Volere operationalises this via a **fit criterion**: a measurement that determines whether the delivered solution "fits" the requirement—if you cannot define a fit criterion, the requirement is ambiguous or not understood. turn1search3

### Ten examples: from vague NFRs to verifiable specifications

The examples below are intentionally phrased in an implementation-agnostic way, while still being objectively checkable via test/measurement/inspection—consistent with IEEE 830's "verifiable" criterion and Volere's fit criterion philosophy. turn10view4

| Vague statement | Verifiable specification (example rewrite) |
|---|---|
| "The system shall be fast." | For the "Search" operation, **p95 end-to-end latency** shall be ≤ 300 ms and **p99** ≤ 800 ms over a rolling 30-day window, measured at the API boundary under the defined reference workload. |
| "The system shall be scalable." | The system shall support **≥ 10,000 concurrent sessions** while maintaining the latency SLOs and error-rate SLOs, under the defined workload profile and data volume. |
| "The system shall be highly available." | Availability SLO: the service shall achieve **≥ 99.9% successful requests** per calendar month, where "successful" excludes client-caused 4xx responses and includes only defined "good" outcomes. |
| "The system shall be secure." | All network communications carrying authentication credentials or personal data shall be encrypted in transit using an approved protocol version; attempts with invalid or expired credentials shall be rejected with a defined error response and shall generate an audit record. |
| "The system shall be reliable." | Under the reference workload, the system shall maintain a **successful request rate ≥ 99.95%** and shall recover from a single-node failure within **≤ 60 seconds** without data loss beyond the defined RPO. |
| "The UI shall be user-friendly." | In usability testing with the defined user class, **≥ 90%** of participants shall complete Task A within **≤ 2 minutes** without assistance; median satisfaction score on the agreed questionnaire shall be ≥ X (define instrument and threshold). |
| "The system shall be maintainable." | A change that adds a new field to a defined external report shall be implementable and deployed within **≤ N person-days**, without modifying more than **M** modules outside the reporting boundary (use operational definition agreed with stakeholders). |
| "The system shall be observable." | For each externally exposed operation, the system shall emit structured logs with correlation IDs, and export metrics for latency and error rate sufficient to compute the SLOs; missing telemetry shall be treated as an SLO violation. |
| "The system shall be compliant." | The system shall produce evidence artefacts (audit logs, retention reports, access reports) sufficient to demonstrate compliance with the named regulation/standard controls; each control mapped to at least one testable requirement. |
| "The system shall protect against invalid input." | For each external interface, invalid inputs violating declared constraints shall return a defined error response within ≤ 200 ms and shall not mutate state; input validation rules (ranges, formats, invariants) shall be explicitly specified. |

These examples deliberately combine "quality attribute scenario" thinking (stimulus/response/measure) with SLO/SLI framing (measured service-level targets) and fit criteria (explicit pass/fail). turn1search33turn10view3

## Documenting external interfaces and data contracts without dictating architecture

Both IEEE 830-1998 and ISO/IEC/IEEE 29148:2018 treat external interfaces as core SRS content. IEEE 830 explicitly lists "external interfaces" as one of the key issues an SRS must address.  ISO/IEC/IEEE 29148:2018's SRS content includes describing how the software operates within constraints such as system/user/hardware/software/communications interfaces, memory, operations, site adaptation, and interfaces with services; and it directs authors to specify the logical characteristics of user interfaces and identify system interfaces. 

A practical "interface requirement" (for APIs, files, messages, devices) typically needs the following, framed as externally observable behaviour:

- **Contract surface**: operations/endpoints/messages, preconditions, and postconditions.
- **Data semantics**: meaning of fields, units, canonical formats, allowed ranges, precision, and invariants.
- **Validation behaviour**: what happens on invalid input (error codes, messages, non-mutation guarantees).
- **Failure modes**: timeouts, partial failure, retries, idempotency expectations, concurrency conflicts.
- **Versioning and compatibility**: backward compatibility rules; deprecation and migration policy.

For HTTP APIs, the OpenAPI Specification is a widely used way to define a language-agnostic interface description so that humans and machines can understand the service capabilities without access to source code; when properly defined, a consumer can interact with minimal implementation logic.  In "spec-first" teams, the OpenAPI contract can serve as the tractable, testable subset of the SRS' "external interface requirements," while the SRS retains the broader behavioural and quality contract and avoids binding the architecture prematurely.

To avoid prescribing implementation, keep these boundaries:

- Specify **what data means** and **what responses must occur**, not *how data is stored* or *which internal component owns it*.
- Specify **observable constraints** (e.g., payload size limits, idempotency guarantees, response time targets), not internal mechanisms (e.g., "use Redis caching").
- Treat schemas as interface contracts, but document the *semantics and invariants* alongside the schema; otherwise schemas become syntactic contracts that still allow semantic ambiguity.

This approach is consistent with IEEE 830's guidance to avoid embedding design and ISO/IEC/IEEE 29148's emphasis on logical interface characteristics and external interfaces. turn18view2

## Atomicity, identifiers, prioritisation, and a traceability model

### Atomicity and unique identification

Atomicity is a practical prerequisite for traceability: a requirement that bundles multiple behaviours is difficult to implement, verify, and change safely. User story research explicitly labels "atomic" as a quality criterion and notes that merging multiple requirements into one degrades estimation accuracy.  This aligns with the "singular" requirement property emphasised in requirement-writing standards and guides. turn0search27

Unique identifiers are the mechanical enabler of traceability and modifiability. Wiegers' SRS template guidance explicitly calls for each requirement to be uniquely identified (sequence number or meaningful tag) and to describe responses to anticipated error conditions. turn4search1

In practice, two ID patterns dominate:

- **Sequential with type prefix**: `REQ-FUNC-001`, `REQ-API-014`, `REQ-SEC-003`. This is easy to automate and stable under reordering.
- **Hierarchical semantic tags**: e.g., `PRINT.COPIES.CONFIRM` (Wiegers-style hierarchical textual tags) which encode functional decomposition but can become brittle if taxonomy changes. 

A pragmatic compromise is: stable sequential IDs for tools and trace matrices, plus optional semantic grouping fields (feature/component/domain) as attributes.

### Prioritisation with explicit semantics

MoSCoW prioritisation gives meaning to priority buckets (Must/Should/Could/Won't) and provides a decision test ("what happens if this is not met?") that helps avoid the "everything is high priority" failure mode.  INCOSE guidance also suggests conveying priority/criticality via requirement attributes rather than weakening the normative force of the statement language. 

### Traceability model from goals to tests

A useful traceability model for an SRS-centric project is "layered," ensuring every requirement is justified (backward traceability) and testable (forward traceability). Literature reviews define requirements traceability as tracing a requirement from emergence to fulfilment; requirements management handbooks emphasise attributes and cross-references to implement this in practice. turn20view3

Below is a practical 5-level model that matches your "Level 1 → Level 4/5" framing:

**Level 1: Business goals and outcomes**  
Business objective IDs (e.g., `GOAL-03 Reduce onboarding drop-off by 20%`), success metrics, and rationale.

**Level 2: Stakeholder needs / capabilities**  
High-level capabilities or stakeholder requirements that operationalise goals (e.g., "Enable self-serve onboarding for SMEs").

**Level 3: Software requirements (the SRS core)**  
Functional + quality + interface requirements, each with: ID, statement, rationale, source, priority, verification method, and trace links. ISO/IEC/IEEE 29148 explicitly calls out these kinds of attributes (rationale, priority, traceability to test cases, verification methods, baselines, risk). turn20view3

**Level 4: Verification artefacts**  
Test cases, automated checks, model checks, inspection checklists, and monitoring definitions (SLIs/SLOs) linked to requirements.

**Level 5: Evidence and results**  
Test runs, monitoring dashboards, audit evidence, and acceptance sign-off per baseline.

A minimal "trace record" per requirement can look like:

- **Upward**: `REQ-FUNC-032 → CAP-ONBOARD-04 → GOAL-03`
- **Downward**: `REQ-FUNC-032 → AC-032.{a,b,c} → TST-API-144 → RUN-2026-02-09`

This operationalises the idea that the SRS is traced forward to tests and backward to goals, and it reflects both standards' emphasis on traceability and verification. turn18view1turn0search22

## Managing assumptions, constraints, risks, and "TBD" items—and keeping the SRS alive in agile delivery

### Explicit uncertainty as a controlled artefact

Greenfield reality is that some requirements will be uncertain early. The failure mode is not uncertainty; it is *implicit uncertainty presented as certainty*. Wiegers' template explicitly recommends using "TBD" as a placeholder when information is not yet available and tracking those items (e.g., via a TBD list/appendix). turn4search4

INCOSE, however, is explicit that **baselined requirement statements should not contain TBD/TBS/TBR except under exceptional circumstances**, because unresolved clauses are incompatible with contractual baselines; such placeholders are appropriate *during analysis* but should be resolved before final baselining. turn10view1 The practical best practice is therefore:

- Maintain an **Issue/TBD register** during elicitation and drafting (transparent uncertainty).
- Define a **baseline gate** where all TBx items are either resolved, explicitly deferred (out of scope), or converted into an approved experiment/spike with acceptance criteria.

### SRS maintenance and review practices

Three practices are consistently supported by standards-oriented guidance and by empirical findings about downstream defect propagation.

- **Structured reviews against quality criteria.** Review requirements for unambiguity, verifiability, completeness, and consistency; these are explicit IEEE 830 criteria and are also central in later standards/guides. turn0search6
- **Baselining and controlled change.** ISO/IEC/IEEE 29148 positions requirements specifications as managed information items across configuration baselines. turn18view2
- **Quality assurance attention proportional to downstream coupling.** Empirical evidence shows factual faults can lead to flawed test cases in a substantial fraction of cases, meaning requirements quality is not merely "documentation quality" but a defect-prevention lever. 

A pragmatic operating model in modern teams is: store the SRS in version control, treat changes as reviewed proposals (pull requests), and require (a) updated trace links and (b) updated verification hooks for any requirement change.

### Aligning the SRS with agile backlogs

In agile delivery, the product backlog is often treated as a functional requirements container; the IREB RE@Agile handbook notes that while the backlog can be thought of as replacing a traditional requirements document, the written part of a user story is incomplete until discussion occurs—so it is better viewed as a pointer to a more precise representation.  This aligns with the evidence that user stories are often low quality without explicit quality frameworks and tooling. 

A workable hybrid for greenfield projects is:

- Keep a **lean SRS** for stable, cross-cutting, and high-risk content: boundaries, external interfaces, data semantics, regulatory constraints, quality requirements (SLOs/scenarios), and any truly non-negotiable constraints.
- Use the **product backlog** for evolving functional scope, discovery, and sequencing, with acceptance criteria/examples as the day-to-day "specification surface."

Scaled frameworks largely mirror this split in spirit.

- SAFe treats Nonfunctional Requirements as persistent qualities/constraints that influence multiple backlogs and are revisited as part of Definition of Done, emphasising that under- or over-specification both carry risk. turn8search2
- LeSS distinguishes Definition of Done (uniform criteria for every backlog item) from item-specific acceptance criteria, reinforcing that global quality constraints belong in shared agreements, not scattered per story. turn9search2

In other words: the SRS remains valuable in agile, but as a **stable contract for the hard-to-change truths** (interfaces, quality targets, constraints, and definitions), while the backlog remains the container for negotiable scope and incremental delivery.

### Empirical signals on what predicts success

The most directly relevant empirical result for SRS structure selection is the 32-project industrial study that mapped SRS quality to IEEE 830 sections and found that a relatively small subset of SRS items had strong impact on project success/failure; notably, richer "Section 1" context content correlated with "normal" projects, while poor context with detailed functionality correlated with cost overruns. turn10view5 Complementary research on requirements specification quality shows that the impact of SRS quality is context-dependent (e.g., safety-criticality, how the SRS is used for communication), but it does empirically connect requirement defects to downstream artefact defects (tests).  Finally, systematic mapping research highlights that while many improvement techniques are studied, there is comparatively less empirical consensus on evidence-based definitions/evaluations of quality attributes—supporting the pragmatic stance that teams must operationalise quality through verification hooks, not adjectives. 
