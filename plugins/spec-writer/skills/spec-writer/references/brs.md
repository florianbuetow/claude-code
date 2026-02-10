# Business & Stakeholder Requirements -- Reference Guide

## Table of Contents

- [1. What standards say about BRS, StRS, and SRS](#1-what-standards-say-about-brs-strs-and-srs)
- [2. How to express business requirements (Wiegers's three-level model)](#2-how-to-express-business-requirements-wiegerss-three-level-model)
- [3. Glossary and ubiquitous language](#3-glossary-and-ubiquitous-language)
- [4. Domain modeling techniques appropriate at this level](#4-domain-modeling-techniques-appropriate-at-this-level)
- [5. Stakeholders, personas, user classes, and JTBD](#5-stakeholders-personas-user-classes-and-jtbd)
- [6. Business-level success metrics and acceptance criteria](#6-business-level-success-metrics-and-acceptance-criteria)
- [7. Failure modes specific to this layer](#7-failure-modes-specific-to-this-layer)
- [8. Recommended combined BRS/StRS template for a greenfield project](#8-recommended-combined-brsstrs-template-for-a-greenfield-project)
- [9. Examples: what belongs in BRS/StRS vs SRS](#9-examples-what-belongs-in-brsstrs-vs-srs)
- [10. How this document feeds into and traces to the SRS](#10-how-this-document-feeds-into-and-traces-to-the-srs)
- [11. Empirical evidence: impact of business-requirements quality on outcomes](#11-empirical-evidence-impact-of-business-requirements-quality-on-outcomes)
- [12. Practical guidance / checklist for a greenfield BRS/StRS](#12-practical-guidance-checklist-for-a-greenfield-brsstrs)
- [Additional Research & Evidence](#additional-research-evidence)
- [What this requirements layer is and how standards position it](#what-this-requirements-layer-is-and-how-standards-position-it)
- [What belongs in BRS/StRS versus SRS](#what-belongs-in-brsstrs-versus-srs)
- [Recommended template structure for a combined BRS/StRS in a greenfield project](#recommended-template-structure-for-a-combined-brsstrs-in-a-greenfield-project)
- [Glossary and ubiquitous language at this stage](#glossary-and-ubiquitous-language-at-this-stage)
- [Domain modelling techniques appropriate for BRS/StRS](#domain-modelling-techniques-appropriate-for-brsstrs)
- [Stakeholders, personas, user classes, success metrics, and traceability](#stakeholders-personas-user-classes-success-metrics-and-traceability)

---

This layer is essentially the "why and what" bridge between strategy and system design. Standards like ISO/IEC/IEEE 29148:2018 and IREB explicitly separate:

- Business/mission level: why the organization is doing this at all.  
- Stakeholder level: what stakeholders need to accomplish in their world.  
- System level: what the system must do and how well it must do it.

A solid BRS/StRS captures the first two and feeds them cleanly into an SRS.

***

## 1. What standards say about BRS, StRS, and SRS

### 1.1 ISO/IEC/IEEE 29148:2018

ISO 29148 defines a clear stack of requirements information items and their contents. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

**Business Requirements Specification (BRS)**

Definition (paraphrased from 3.1.4 & 9.3):

> A structured collection of the requirements of the business or mission (problem/opportunity definition, concepts, required conditions of solutions) and its relationship to the external environment. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

Purpose and typical contents (9.3): [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

- Business purpose and scope  
- Business overview and environment  
- Major stakeholders and business structure  
- Mission, goals and objectives  
- Business model and information environment  
- Business processes  
- Business operational **policies and rules**  
- Business operational **constraints**, modes, quality  
- High-level operational concept and scenarios  
- High-level life-cycle concepts, project constraints  

This is explicitly business/mission language, independent of any particular system.

**Stakeholder Requirements Specification (StRS)**

Definition (3.1.29): [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

> A structured collection of stakeholder requirements (characteristics, context, concepts, constraints, priorities) and their relationship to the external environment.

Purpose and contents (9.4): [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

- Stakeholder purpose and scope  
- Stakeholder list and roles  
- Business environment  
- Mission, goals, objectives (from stakeholder viewpoint)  
- Business model and information environment  
- **System processes** and operational **policies/rules**  
- Operational constraints, modes, states, qualities  
- **User requirements** (explicitly part of StRS)  
- Operational concept and scenarios  
- Detailed concepts of proposed system, project constraints  

The StRS is still written in stakeholder language, but it is now talking about the **system-in-context** and what stakeholders expect that system to enable.

**System Requirements Specification (SyRS) and Software Requirements Specification (SRS)**

Definitions and contents (9.5, 9.6): [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

- SyRS: technical system requirements (functions, performance, constraints, interfaces, life‑cycle aspects) – "what the system shall do" as a black box in its environment.
- SRS: software product requirements (functions, interfaces, data, quality attributes, constraints) – the classic IEEE 830/29148 software spec.

The SyRS/SRS introduce:

- Detailed **functional requirements**  
- Non‑functional requirements (performance, usability, security, etc.)  
- Detailed interfaces, data, constraints, verification criteria  

ISO 29148 also stresses traceability:

- Business or mission analysis → BRS (6.2) [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- Stakeholder needs/requirements → StRS (6.3) [cwnp](https://www.cwnp.com/req-eng/)
- System requirements definition → SyRS/SRS (6.4) [cwnp](https://www.cwnp.com/req-eng/)

and expects trace links across these levels. [cwnp](https://www.cwnp.com/req-eng/)

***

### 1.2 IREB CPRE and BABOK positioning

The IREB CPRE Foundation syllabus distinguishes: [mstb](https://www.mstb.org/Downloadfile/cpre_foundationlevel_syllabus_en_v.3.1.pdf)

- **Business requirements**: business goals, objectives, and needs of the organization (why).  
- **Stakeholder requirements**: what each stakeholder needs so those business requirements can be met (bridge between business and solution).  
- **System/solution requirements**: what the socio‑technical solution must do to satisfy stakeholder requirements.

IREB emphasizes:

- **Principle 2 – Stakeholders:** RE is about satisfying stakeholders' desires and needs.  
- **Principle 3 – Shared understanding:** explicit documented requirements + implicit domain knowledge.  
- **Principle 5 – Problem–Requirement–Solution:** problems → requirements → solution, not necessarily in that chronological order. [isqi](https://isqi.org/media/7f/9a/3e/1744288053/cpre_foundationlevel_syllabus_EN_v.3.2.pdf)

BABOK uses a similar hierarchy: business requirements, stakeholder requirements, and solution requirements (functional + non‑functional), with stakeholder requirements acting as the bridge. [techcanvass](https://techcanvass.com/blogs/types-of-requirements-as-per-babok.aspx)

***

### 1.3 Summary: what belongs where

At a high level:

| Level | Document | Focus | Typical content |
|------|----------|-------|-----------------|
| 0 | Strategy, vision | Why the organization exists; long-term strategy | Vision, strategic themes, portfolio OKRs |
| 1a | **BRS** | Why this initiative; how the business must change | Business problem/opportunity, goals, business model, processes, business rules, high-level success metrics |
| 1b | **StRS** | What stakeholders need to achieve in context | Stakeholder map, user classes, user goals, system-in-context processes, policies/rules, stakeholder-level constraints & qualities |
| 2 | **SyRS / SRS** | What the system shall do and how well | Functional requirements, quality attributes, interfaces, data, detailed acceptance criteria |

***

## 2. How to express business requirements (Wiegers's three-level model)

Karl Wiegers has been very consistent across *Software Requirements* (3rd ed.) and later writings:

- **Business requirements** – why the organization is undertaking the project; business objectives and success criteria. [tynerblain](https://tynerblain.com/blog/2006/01/04/foundation-series-structured-requirements/)
- **User requirements** – what users need to be able to do with the solution (goals, tasks, scenarios). [batimes](https://www.batimes.com/articles/user-requirements-and-use-cases/)
- **Functional requirements** – what the software must do to support those user tasks and goals. [users.csc.calpoly](http://users.csc.calpoly.edu/~csturner/courses/300f06/readings/reqtraps.pdf)

He recommends:

- Capturing business requirements in a **vision and scope** document (conceptually equivalent to BRS). [uml.org](http://www.uml.org.cn/rjzl/pdf/1113/reqtraps.pdf)
- Capturing user requirements as **use cases**, scenarios, or user stories linked to user classes and business objectives. [youtube](https://www.youtube.com/watch?v=MwimXkY5G5o)
- Capturing functional requirements in the **SRS**, each traceable back to user and business requirements. [isg.inesc-id](http://isg.inesc-id.pt/REBox/WiegersTemplate@17.aspx?page=1Introduction)

### 2.1 Writing business requirements

Wiegers treats business requirements as:

- **Objectives**: measurable improvements (e.g., "Reduce average claim processing time by 30% within 12 months of deployment"). [youtube](https://www.youtube.com/watch?v=em7L-KzNuRQ)
- **Problem statements**: current pain and its impact.  
- **Solution boundaries**: what is in/out of scope. [youtube](https://www.youtube.com/watch?v=-UgOZhqAzUo)

Characteristics of well-formed business requirements:

- Focus on **outcomes**, not product features.  
- Expressed in business terms, understandable to executives and domain experts.  
- Quantified where possible; Wiegers explicitly recommends defining success metrics for objectives. [youtube](https://www.youtube.com/watch?v=em7L-KzNuRQ)

Example business requirement (Level 1):

> BR‑1: Within 12 months of go‑live, reduce manual processing time per insurance claim by at least 30% while maintaining current claim accuracy rates.

This belongs in the BRS / vision & scope, not in the SRS.

### 2.2 Role of "features" as an intermediate concept

Wiegers defines a **feature** as: [jamasoftware](https://www.jamasoftware.com/blog/2013/07/24/defining-project-scope-feature-levels-and-system-events/)

> "A set of logically related functional requirements that provides a capability to the user and enables the satisfaction of a business objective."

He uses features to:

- Express **high-level capabilities** recognizable to stakeholders.  
- Control **scope** across releases: feature + level (e.g., "basic reporting", "advanced analytics"). [jamasoftware](https://www.jamasoftware.com/blog/2013/07/24/defining-project-scope-feature-levels-and-system-events/)
- Group detailed functional requirements in the SRS.

So you typically get chains like:

> Business objective → User goal → Feature → Functional requirements

In a BRS/StRS, features are often listed at a high level (e.g., "Self-service claim submission"), but the detailed behaviors ("system shall validate policy X…") belong in the SRS.

### 2.3 Where do business rules go?

Wiegers treats **business rules** as a distinct category of knowledge – policies, regulations, calculations, and constraints that shape system behavior but are not themselves requirements. [requirements](https://requirements.com/Content/Articles-Posts/how-to-categorize-customer-requirements)

- Business rules usually **live in the BRS/StRS** (they describe how the business operates), or in a separate Business Rules catalog.  
- Requirements then **reference** those rules (e.g., FR‑23: "The system shall calculate interest according to BR‑7 Interest Calculation Rule"). [requirements](https://requirements.com/Content/Articles-Posts/how-to-categorize-customer-requirements)

ISO 29148 aligns with this by expecting:

- **Business operational policies and rules** in the BRS. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- **System operational policies and rules** in the StRS. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

Best practice at this layer: record rules once, give them IDs, and trace requirements to rules rather than duplicating rule logic in requirements text.

***

## 3. Glossary and ubiquitous language

### 3.1 DDD's ubiquitous language and bounded contexts

Eric Evans's Domain‑Driven Design defines **ubiquitous language** as a shared, rigorous domain language used in all discussions and in the code. [arxiv](https://arxiv.org/html/2310.01905v4)

Key ideas:

- The language is built around the domain model and used by both domain experts and developers.  
- Each **bounded context** has its own internally consistent language; the same term can legitimately mean different things in different contexts. [infoq](https://www.infoq.com/news/2019/06/bounded-context-eric-evans/)
- The boundary of the language is the bounded context: a set of models, terms, rules used consistently within a part of the system. [infoq](https://www.infoq.com/news/2019/06/bounded-context-eric-evans/)

Martin Fowler emphasizes that software doesn't cope well with ambiguity, so the ubiquitous language must be **rigorous**. [martinfowler](https://martinfowler.com/bliki/UbiquitousLanguage.html)

At the BRS/StRS stage, you are essentially defining the **first version** of that ubiquitous language and sketching bounded contexts.

### 3.2 Empirical evidence on terminology and defects

Evidence that terminology issues and ambiguity hurt project outcomes:

- NASA's SATC study of 40+ SRS documents found pervasive defects due to **ambiguity, inaccuracy, and inconsistency** in natural-language requirements. [zolotarev.fd.cvut](https://zolotarev.fd.cvut.cz/sni/ctrl.php?act=show%2Cfile%2C9727)
- NASA's ARM quality model and tools like QuARS use patterns (e.g., vague, optional, or weak terms) to detect ambiguity; ambiguous phrases correlate with defect-prone specs. [ceur-ws](https://ceur-ws.org/Vol-3122/NLP4RE-paper-3.pdf)
- A systematic mapping of empirical research on requirements quality found **ambiguity** to be one of the most studied and problematic quality attributes; many "sub‑types" of ambiguity are terminological. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC9110500/)
- An experiment on **terminological ambiguity in user stories** showed that detecting near‑synonyms and inconsistent terms is hard and time‑consuming, even with tool support, and that terminological ambiguity is a real risk for misimplementation. [research-portal.uu](https://research-portal.uu.nl/en/publications/detecting-terminological-ambiguity-in-user-stories-tool-and-exper)
- Lauesen repeatedly shows that imprecise and open‑ended requirements make it difficult to compare solutions and ensure that business goals are met. [itu](https://www.itu.dk/~slauesen/Papers/GuideSL-07v5-online.pdf)

While there is not a randomized trial of "ubiquitous language vs. no ubiquitous language", the empirical work consistently finds that ambiguous terminology and inconsistent use of terms in requirements introduce defects and rework.

### 3.3 Best practices for glossary structure and maintenance

For a BRS/StRS, treat the **glossary** as a first‑class artifact, not an afterthought:

**Structure**

- One entry per concept:
  - Preferred term  
  - Plain-language definition (domain expert approved)  
  - Synonyms / forbidden terms (e.g., "Don't use 'client' here, use 'customer'")  
  - Notes on context / bounded context membership  
  - Source (regulation, SME, standard)  
- Include:
  - Core domain concepts (Order, Claim, Policy, Account, etc.)  
  - Roles and actors (Agent, Adjuster, Customer, Partner)  
  - Key events (Order Placed, Claim Approved, etc.)  
  - Key metrics (Net Revenue, Churn, SLA Breach)

**Process**

- Establish a **language gatekeeper** role (often the lead BA / product owner): new terms only enter via the glossary.  
- Require every requirement statement at this level to use glossary terms; forbid synonyms.  
- Align glossary with **bounded contexts**:
  - Some terms exist in multiple contexts with different meanings; the glossary should make that explicit.  
- Version the glossary and treat changes as requirements changes (with impact analysis).

**Placement**

- ISO 29148 expects **Definitions, acronyms and abbreviations** as standard front-matter in all these specs. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- For DDD‑heavy projects, add a dedicated "Ubiquitous Language and Domain Terms" section in the combined BRS/StRS, and reference it from the SRS.

***

## 4. Domain modeling techniques appropriate at this level

The BRS/StRS level is about **mental models**, not solution architecture. Good candidates:

### 4.1 Event Storming (Big Picture)

Alberto Brandolini's **Big Picture Event Storming** is a collaborative domain discovery method using domain events on a large wall to uncover processes, hotspots, and organizational friction. [youtube](https://www.youtube.com/watch?v=PEZGOLHGqM8)

- Participants from across the business contribute events; disagreements and "hotspots" are made explicit and captured. [youtube](https://www.youtube.com/watch?v=mLXQIYEwK24)
- The outcome is a shared narrative of how the business actually works, often surfacing unknown constraints and cross‑team dependencies. [youtube](https://www.youtube.com/watch?v=PEZGOLHGqM8)

While there is mostly anecdotal rather than statistical evidence, Brandolini and others report:

- Better cross‑departmental alignment  
- Earlier discovery of process and policy conflicts  
- Stronger "political momentum" because the same workshop discovers problems and gets stakeholder buy‑in to solve them. [youtube](https://www.youtube.com/watch?v=PEZGOLHGqM8)

This is ideal input for:

- BRS sections on **business processes, environment, and structure**. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- StRS sections on **system processes, operational concepts, and scenarios**. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

### 4.2 Conceptual domain models

Conceptual models (often UML class diagrams) describe:

- Core domain entities and value objects  
- Relationships and cardinalities  
- Key attributes (but not database schemas)

An empirical study on domain models used for completeness checking in natural‑language requirements found: [pure.ul](https://pure.ul.ie/en/publications/an-empirical-study-on-the-potential-usefulness-of-domain-models-f/)

- Domain models exhibit **near‑linear sensitivity** to simulated omissions in requirements.  
- They were **>4× more sensitive** to completely unspecified requirements than to under‑specified ones.  

This is strong evidence that early domain modeling helps detect missing and incomplete requirements before they hit design and code. [pure.ul](https://pure.ul.ie/en/publications/an-empirical-study-on-the-potential-usefulness-of-domain-models-f/)

### 4.3 DDD context maps and conceptual integrity

DDD **context maps** document:

- Bounded contexts and their responsibilities  
- Relationships (Conformist, Anti‑corruption Layer, etc.)  
- Upstream/downstream dynamics

Fred Brooks's notion of **conceptual integrity** – a system designed around a coherent set of concepts and principles – is argued to be "the most important consideration in system design". DDD's strategic patterns (bounded contexts, context maps) are pragmatic tools for preserving conceptual integrity as systems grow. [duitdesign](https://duitdesign.com/what-elements-of-design-does-brooks-attribute-to-conceptual-integrity.html)

### 4.4 Model‑based and conceptual modeling evidence

Model‑Based Systems Engineering (MBSE) case studies show that modeling early in the life cycle improves defect detection and reduces rework: [incose](https://www.incose.org/docs/default-source/enchantment/161109-carrolled-howismodel-basedsystemsengineeringjustified-researchreport.pdf)

- Across 11 case studies, MBSE was justified by **cost reductions and schedule improvements** attributed to finding and fixing defects earlier.  
- The capability to find defects early was key; later-phase rework costs were significantly reduced. [incose](https://www.incose.org/docs/default-source/enchantment/161109-carrolled-howismodel-basedsystemsengineeringjustified-researchreport.pdf)

More broadly, conceptual modeling is linked to:

- **Error prevention and correctness support** as major productivity drivers in system development. [sciencedirect](https://www.sciencedirect.com/science/article/pii/S0169023X23001234)

Taken together with the domain model completeness study and NASA's SRS quality work, there is a robust empirical and industrial case that early domain exploration reduces downstream defects and rework. [zolotarev.fd.cvut](https://zolotarev.fd.cvut.cz/sni/ctrl.php?act=show%2Cfile%2C9727)

### 4.5 Recommended domain modeling artifacts in BRS/StRS

At this layer, aim for:

- One or more **Big Picture Event Storming** boards (or documented outputs) for key value streams.  
- A **context diagram** showing system‑of‑interest and neighboring systems.  
- A **conceptual domain model** of core entities and relationships.  
- A **context map** with bounded contexts and their relationships (where DDD is applicable).

These stay technology‑agnostic and focus on "how the business sees the world".

***

## 5. Stakeholders, personas, user classes, and JTBD

### 5.1 Stakeholders vs users

ISO 29148 defines a **stakeholder** broadly as any individual or organization having an interest, right, or claim in the system. Users are a subset of stakeholders. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

IREB emphasizes:

- Identifying and classifying stakeholders.  
- Resolving conflicts between stakeholders' needs. [gasq](https://www.gasq.org/files/content/gasq/downloads/certification/IREB/IREB%20FL/cpre_foundationlevel_handbook_en_v1.0.pdf)

At the BRS/StRS level, you should:

- Map **stakeholder groups** (sponsors, operations, regulators, customers, partners, support, etc.).  
- Identify **user classes** – groups of users with distinct tasks, rights, and expectations. [linkedin](https://www.linkedin.com/pulse/create-personas-design-best-user-experience-pixentia-administrator)

Wiegers uses user classes as the bridge from business to user requirements, and suggests aligning priorities with favored user classes whose satisfaction most closely aligns with business objectives. [linkedin](https://www.linkedin.com/pulse/create-personas-design-best-user-experience-pixentia-administrator)

### 5.2 Personas (Alan Cooper and beyond)

Alan Cooper popularized **personas** as archetypal users representing behavior patterns and goals. [dl.acm](https://dl.acm.org/doi/10.1145/572020.572044)

Empirical findings:

- An ethnographic study of a design team using personas found that, in practice, teams struggled to use personas effectively and often defaulted back to vague notions of "the user". [academia](https://www.academia.edu/4703534/Personas_in_action_ethnography_in_an_interaction_design_team)
- Microsoft's "Personas: Practice and Theory" paper argues personas can be powerful when grounded in data and integrated with other UX methods. [microsoft](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/01/personas-practice-and-theory.pdf)

Common problems:

- "Frankenstein" personas composed of random traits, not grounded in research. [blog.prototypr](https://blog.prototypr.io/the-problem-with-personas-82eb57802114)
- Over‑detailed demographic stories that don't add decision‑making value.

### 5.3 Jobs to Be Done (JTBD) and evidence

JTBD focuses on the **job** the user is trying to accomplish (functional, emotional, social) independent of demographics. [delve](https://www.delve.ai/blog/personas-jobs-to-be-done)

- Persona: who the user is.  
- JTBD: what they are trying to get done and under what circumstances.  

UX and product research (e.g., Nielsen Norman Group) suggests that:

- JTBD is particularly good at surfacing **outcomes and success criteria**.  
- Personas add value by supplying **attitudinal and behavioral context** once jobs are understood. [nngroup](https://www.nngroup.com/articles/personas-jobs-be-done/)

JTBD has largely case‑study and practice‑based rather than experimental evidence, but there is strong practitioner consensus about its usefulness in focusing on user outcomes.

### 5.4 Wiegers's view: user classes, goals, and use cases

Wiegers's recommended flow: [youtube](https://www.youtube.com/watch?v=-UgOZhqAzUo)

- Use business requirements to **identify user classes**.  
- For each user class, elicit **user goals** and tasks ("what do you need to do with the system?" rather than "what features do you want?").  
- Capture user requirements as:
  - **Use cases** – structured scenarios of user–system dialog.  
  - Possibly user stories, but use cases give more structure for traceability and testing. [youtube](https://www.youtube.com/watch?v=MwimXkY5G5o)

He explicitly states: "You don't implement business requirements or user requirements; developers implement **functionality**." The BRS/StRS are about understanding needs; the SRS is about specifying functionality. [youtube](https://www.youtube.com/watch?v=em7L-KzNuRQ)

### 5.5 Recommended approach at the BRS/StRS level

For this layer:

- Maintain a **stakeholder map** with roles, influence, needs.  
- Define **user classes** (primary, secondary, disfavored) based on tasks and responsibilities. [linkedin](https://www.linkedin.com/pulse/create-personas-design-best-user-experience-pixentia-administrator)
- For a few critical user classes, create **lean personas**:
  - Task and goal focused  
  - Minimal demography  
  - Explicit linkage to user class and JTBD  
- For each key user class / persona, define 3–7 **Jobs to Be Done** statements:
  - "When [situation], I want to [job], so I can [outcome]."

Record this in the StRS under **Stakeholders, user requirements, and operational concept**. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

Deep marketing or UX personas (photos, hobbies, quotes) are better deferred to design phases unless they directly drive requirements.

***

## 6. Business-level success metrics and acceptance criteria

### 6.1 Volere "fit criteria"

The Volere template introduces **fit criteria** – quantified measures attached to each requirement. [reqview](https://www.reqview.com/doc/volere-template/)

- Each requirement should have a fit criterion: a way to measure whether a solution satisfies it.  
- If no fit criterion can be found, the requirement is probably ambiguous or poorly understood. [cs.uic](https://www.cs.uic.edu/~i440/VolereMaterials/templateArchive16/c%20Volere%20template16.pdf)

Example:

> Requirement: "The system shall be easy to learn."  
> Fit criterion: "80% of novice users shall be able to complete task X within 10 minutes after 30 minutes of training, with no more than 1 request for help." [cs.uic](https://www.cs.uic.edu/~i440/VolereMaterials/templateArchive16/c%20Volere%20template16.pdf)

At the BRS/StRS level, fit criteria apply to:

- Business objectives ("reduce processing time by 30%").  
- Stakeholder needs ("95% of claims submitted online without agent assistance").  
- Key quality expectations ("customer satisfaction NPS > 40").

### 6.2 OKRs, KPIs, and their relationship to requirements

OKRs (Objectives and Key Results) provide a clean pattern for business success metrics: [ibm](https://www.ibm.com/think/insights/okr-measurement-scoring)

- **Objective** – qualitative, inspiring, aligned to strategy.  
- **Key Results** – specific, measurable, time‑bound indicators of success.

KPIs often serve as the measures underlying KRs. [ibm](https://www.ibm.com/think/insights/okr-measurement-scoring)

Example BRS fragment:

- Objective: "Improve customer satisfaction for claims handling."  
- Key Results:
  - Increase post‑claim CSAT from 3.5 to 4.2 within 12 months.  
  - Reduce average claim resolution time from 15 days to 7 days.  

These KRs are essentially **high-level fit criteria** for the project.

### 6.3 Feeding into SRS acceptance criteria

Linking levels:

- Business KR → Stakeholder needs (e.g., "customer can track claim status online") → Features → Functional requirements → **Acceptance criteria / test cases**.

Volere's fit criteria philosophy and ISO 29148's requirement verifiability characteristic provide the bridge:

- Every SRS requirement should be **verifiable**, usually via tests derived from acceptance criteria and fit criteria. [itu](https://www.itu.dk/~slauesen/Papers/GuideSL-07v5-online.pdf)

In practice:

- In the BRS/StRS, define:
  - Business objectives and OKRs.  
  - High-level fit criteria for major stakeholder needs.  
- In the SRS, refine these into:
  - Detailed acceptance criteria attached to functional and quality requirements.  
  - Test cases in the validation and verification plans.

***

## 7. Failure modes specific to this layer

Empirical and industry data point to recurring pathologies when the business/stakeholder layer is missing or muddled.

### 7.1 CHAOS data: lack of user input and inadequate requirements

Multiple CHAOS reports highlight:

- **Lack of user involvement** and **incomplete/poor requirements** as top contributors to failure. [ohezybus](https://ohezybus.garden/understanding-project-success-and-failure-the-standish-group-chaos-report-2020-highlights/)
- One summary of earlier CHAOS results gives, for "challenged" projects: [bijoor](https://bijoor.me/2005/06/15/making-software-work/)
  - Lack of user input – 12.8%  
  - Incomplete requirements and specifications – 12.3%  
  - Changing requirements and specifications – 11.8%  
  - Unrealistic expectations – 5.9%  
  - Unclear objectives – 5.3%  

Later commentary similarly ranks "lack of user involvement" and "inadequate requirements management" at the top. [linkedin](https://www.linkedin.com/posts/thomas-huang-87b6007_projectmanagement-leadership-agile-activity-7345955262232481792-KKHA)

These issues are exactly what a solid BRS/StRS is intended to address:

- Make objectives clear.  
- Capture stakeholder needs and constraints explicitly.  
- Provide a baseline to control change.

### 7.2 NASA SRS quality study

NASA's SATC study of more than 50 SRS documents found systemic weaknesses: [cw.fel.cvut](https://cw.fel.cvut.cz/b181/_media/courses/a4m33sep/materialy/requirements/writingeffectivesrs.pdf)

- Poor document organization.  
- Ambiguous, inconsistent, and incomplete requirements.  
- Heavy reliance on informal natural language without disciplined patterns.

NASA's response was to define:

- A quality model (including ambiguity, optionality, weak phrases).  
- Tools like ARM to detect problematic wording and structure. [ceur-ws](https://ceur-ws.org/Vol-3122/NLP4RE-paper-3.pdf)

Again, this points to the need for early, disciplined requirements work – including glossary, domain models, and fit criteria – before diving into detailed SRS writing.

### 7.3 Lauesen and later studies

Lauesen, based on extensive industrial case material, emphasizes: [itu](https://www.itu.dk/~slauesen/Papers/ExcerptsSwReqs.pdf)

- Requirements that are too imprecise are not verifiable and cannot be used to compare supplier proposals.  
- Requirements that don't cover important business demands result in systems that technically meet the spec but fail the business.

Recent work on **user story quality** found that practitioners' user story sets covered only about one‑third of the stakeholder issues identified in analysis reports, and many stories were hard to verify or restricted the solution space unnecessarily. This illustrates the danger of jumping straight to low‑level solution requirements without a solid business/stakeholder foundation. [itu](https://www.itu.dk/~slauesen/UserStories/UserStory_Software_2022-2.pdf)

***

## 8. Recommended combined BRS/StRS template for a greenfield project

For a greenfield software product, a **combined Business & Stakeholder Requirements Specification (BStRS)** works well. The outline below is aligned with ISO 29148's BRS and StRS content items. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

1. **Introduction**
   - Purpose of this document (and relationship to strategy and SRS).  
   - Scope: business domain and solution boundaries at a high level.  

2. **Definitions, Acronyms, and Abbreviations**
   - Glossary (ubiquitous language seed).  
   - Acronyms and abbreviations. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

3. **Business Context (BRS‑oriented)**
   1. Business purpose  
   2. Business problem / opportunity  
   3. Business scope (in‑scope / out‑of‑scope areas) [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
   4. Business overview and environment (market, regulations, organizational context)  

4. **Business Goals, Objectives, and Success Metrics**
   - Mission, goals, objectives (with OKR‑style key results where possible). [atlassian](https://www.atlassian.com/agile/agile-at-scale/okr)
   - Project constraints (budget, schedule, regulatory constraints at business level).  

5. **Business Model and Processes**
   - Business model (value propositions, revenue streams, high-level capabilities).  
   - Core business processes (from Event Storming outputs): diagrams + textual descriptions. [youtube](https://www.youtube.com/watch?v=mLXQIYEwK24)
   - Business operational modes and variants (e.g., jurisdictions, product lines).  

6. **Business Rules and Policies**
   - Catalog of business rules (with IDs, sources, short descriptions). [requirements](https://requirements.com/Content/Articles-Posts/how-to-categorize-customer-requirements)
   - Regulatory and policy references.  

7. **Stakeholders and User Classes**
   - Stakeholder map (roles, concerns, influence, and priorities). [mstb](https://www.mstb.org/Downloadfile/cpre_foundationlevel_syllabus_en_v.3.1.pdf)
   - User classes (primary, secondary, disfavored, negative).  
   - For selected key classes: brief personas and JTBD statements. [delve](https://www.delve.ai/blog/personas-jobs-to-be-done)

8. **Domain Model and Contexts**
   - Context diagram (system-of-interest and neighboring systems).  
   - Conceptual domain model (entities, relationships, key attributes). [pure.ul](https://pure.ul.ie/en/publications/an-empirical-study-on-the-potential-usefulness-of-domain-models-f/)
   - Bounded contexts and context map (if doing DDD). [arxiv](https://arxiv.org/html/2310.01905v4)

9. **Stakeholder Needs and User Requirements**
   - For each stakeholder group / user class:
     - Goals and outcomes.  
     - Jobs to Be Done statements.  
     - High-level user tasks (candidate use cases / epics).  
   - Prioritization criteria (business value, risk, frequency, favored classes). [users.csc.calpoly](http://users.csc.calpoly.edu/~csturner/courses/300f06/readings/reqtraps.pdf)

10. **System-in-Context Processes and Operational Concept**
    - System processes (how the future system participates in business workflows). [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
    - Operational concept (Concept of Operations at stakeholder level).  
    - Operational scenarios and storyboards (no UI or technical detail). [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

11. **Stakeholder-Level Constraints and Quality Expectations**
    - Operational constraints (hours of operation, locations, channels). [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
    - Stakeholder-level quality expectations (e.g., usability, availability, security posture), framed as desired outcomes rather than technical targets. [cwnp](https://www.cwnp.com/req-eng/)

12. **Business and Stakeholder-Level Success Metrics**
    - Business objectives with fit criteria / key results.  
    - Stakeholder satisfaction measures (e.g., NPS, CSAT).  

13. **Risks, Assumptions, and Open Issues**
    - Requirements risks specific to the business/stakeholder layer (organizational change, unclear ownership, competing business objectives).  

14. **Traceability and Mapping to SRS**
    - Trace model (business objective → stakeholder need → feature / capability → SRS requirement).  
    - Initial traceability matrix skeleton.

Rationale:

- Sections 3–6 correspond closely to ISO's BRS content. [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- Sections 7–11 cover ISO's StRS content (stakeholders, system processes, policies, constraints, operational concept, user requirements). [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- Sections 12–14 set up success metrics and traceability into the SRS and test artifacts, consistent with Volere and ISO verifiability guidance. [cs.uic](https://www.cs.uic.edu/~i440/VolereMaterials/templateArchive16/c%20Volere%20template16.pdf)

***

## 9. Examples: what belongs in BRS/StRS vs SRS

Assume a greenfield **online loan origination** system.

| Level | Example requirement | Correct placement |
|------|---------------------|-------------------|
| Business objective | "Within two years of deployment, increase the percentage of loans originated via digital channels from 20% to 60%, while maintaining current default rates." | BRS – Goals & Success Metrics |
| Business rule | "For unsecured loans above €20,000, a manual risk review is mandatory before approval." | BRS – Business Rules and Policies |
| Stakeholder need | "Retail customers must be able to apply for a personal loan online without visiting a branch." | StRS – Stakeholder Needs & User Requirements |
| User requirement / goal | "As a prospective borrower, I want to compare monthly payment options for different loan terms so that I can choose an affordable plan." | StRS – User Requirements (often also captured as a use case) |
| System-level functional requirement | "The system shall calculate the monthly installment for a loan given principal P, annual interest rate r, and term n in months using formula F, and display at least three alternative terms (24, 36, 48 months) for comparison." | SyRS/SRS – Functional Requirements |
| System constraint | "The loan application API shall respond within 2 seconds for 95% of requests under normal operating load of up to 200 requests per second." | SyRS/SRS – Performance Requirements |
| Acceptance criterion | "Given a €10,000 loan at 5% APR for 36 months, the system shall calculate a monthly payment between €299.50 and €300.50 and display all three preconfigured terms within 2 seconds." | Test / SRS-level fit criteria |

The BRS/StRS never talks about APIs, response times, formulas, or UI controls. The SRS never talks about "increase digital share to 60%" except as trace links and rationale.

***

## 10. How this document feeds into and traces to the SRS

Standards and practice both stress **traceability** across levels. [users.csc.calpoly](http://users.csc.calpoly.edu/~csturner/courses/300f06/readings/reqtraps.pdf)

A practical trace chain:

1. **Business objective / OKR** (BRS)
   - e.g., "Increase digital loan origination to 60%."

2. **Stakeholder needs & user goals** (StRS)
   - "Prospective borrowers can complete loan applications online without branch visits."
   - "Risk officers can review and override automated decisions."

3. **Features / high-level capabilities**
   - "Online loan application wizard."  
   - "Risk review workbench."

4. **Use cases / epics / user stories**
   - UC‑1: "Submit loan application."  
   - UC‑2: "Review application decision."

5. **SRS requirements**
   - Functional requirements per use case.  
   - Quality attributes derived from stakeholder expectations (e.g., time to complete, availability). [batimes](https://www.batimes.com/articles/user-requirements-and-use-cases/)

6. **Tests and validation**
   - Test cases and acceptance tests verifying each SRS requirement, and indirectly, stakeholder needs and business objectives.

Mechanically:

- Give each business objective, stakeholder need, feature, use case, and requirement a **unique ID**.  
- Maintain trace links in a requirements tool or a set of matrices:
  - Objective ↔ Stakeholder Needs  
  - Stakeholder Needs ↔ Features / Use Cases  
  - Features / Use Cases ↔ SRS Requirements  
  - SRS Requirements ↔ Test Cases  

Wiegers explicitly recommends tracing each functional requirement back to its **origin** (use case, higher-level requirement, business rule) to avoid "requirements traps" like building functionality with no business justification. [users.csc.calpoly](http://users.csc.calpoly.edu/~csturner/courses/300f06/readings/reqtraps.pdf)

ISO 29148 similarly expects traceability from system requirements back to stakeholder and business/mission requirements. [cwnp](https://www.cwnp.com/req-eng/)

***

## 11. Empirical evidence: impact of business-requirements quality on outcomes

Pulling the strands together:

- The CHAOS studies show that **incomplete requirements, lack of user involvement, unclear objectives, and unrealistic expectations** are persistent top causes of IT project failure or challenge. [sga.profnit.org](https://sga.profnit.org.br/index_htm_files/threads/J3DL0R/StandishGroupChaosReport.pdf)
- NASA's SRS quality work demonstrates that natural-language requirements, when not written and structured carefully, contain many defects of ambiguity and incompleteness, leading to downstream problems. [cw.fel.cvut](https://cw.fel.cvut.cz/b181/_media/courses/a4m33sep/materialy/requirements/writingeffectivesrs.pdf)
- Empirical work on **requirements quality** shows that ambiguity, completeness, and consistency are central quality attributes, with significant research effort devoted to improving them. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC9110500/)
- Domain modeling studies provide evidence that conceptual domain models help detect missing requirements, especially completely unspecified ones. [pure.ul](https://pure.ul.ie/en/publications/an-empirical-study-on-the-potential-usefulness-of-domain-models-f/)
- MBSE case studies show that early, model‑based requirements and system definition reduce rework and mitigate schedule and cost risks. [incose](https://www.incose.org/docs/default-source/enchantment/161109-carrolled-howismodel-basedsystemsengineeringjustified-researchreport.pdf)
- Studies on user stories and agile requirements indicate that, without disciplined requirements practices, agile artifacts can miss large portions of stakeholder needs and be hard to verify. [itu](https://www.itu.dk/~slauesen/UserStories/UserStory_Software_2022-2.pdf)

Collectively, the evidence base supports the idea that **investing in a high‑quality BRS/StRS – with clear objectives, stakeholder needs, domain models, and disciplined language – significantly reduces the risk of project failure, rework, and misalignment**.

***

## 12. Practical guidance / checklist for a greenfield BRS/StRS

For a greenfield software project, a good BRS/StRS should:

1. **Anchor in strategy**
   - Explicitly connect business objectives (with OKR‑style metrics) to the initiative. [atlassian](https://www.atlassian.com/agile/agile-at-scale/okr)

2. **Define the domain language**
   - Create a glossary and seed a ubiquitous language; align with bounded contexts. [martinfowler](https://martinfowler.com/bliki/UbiquitousLanguage.html)

3. **Map stakeholders and user classes**
   - Identify stakeholders, user classes, and a few key personas and JTBDs. [mstb](https://www.mstb.org/Downloadfile/cpre_foundationlevel_syllabus_en_v.3.1.pdf)

4. **Model the domain early**
   - Use Event Storming (Big Picture) and conceptual models to surface processes, events, and entities, and to detect omissions. [youtube](https://www.youtube.com/watch?v=mLXQIYEwK24)

5. **Capture business rules separately**
   - Catalog policies, regulations, and business rules with IDs; trace requirements to them. [requirements](https://requirements.com/Content/Articles-Posts/how-to-categorize-customer-requirements)

6. **Express business and stakeholder requirements in outcome terms**
   - Business: objectives and constraints in business language.  
   - Stakeholder: goals, tasks, and operational concepts from stakeholders' viewpoint. [users.csc.calpoly](http://users.csc.calpoly.edu/~csturner/courses/300f06/readings/reqtraps.pdf)

7. **Attach fit criteria / success metrics wherever possible**
   - Apply Volere's fit-criteria idea to both business and stakeholder requirements. [itu](https://www.itu.dk/~slauesen/Papers/GuideSL-07v5-online.pdf)

8. **Keep solution design out**
   - No UI layouts, database schemas, API specs, or detailed algorithms – those belong in the SRS and subsequent design artifacts. [itu](https://www.itu.dk/~slauesen/Papers/ExcerptsSwReqs.pdf)

9. **Set up traceability into SRS and tests**
   - Define IDs and trace model upfront; make SRS writing largely a **refinement** of BRS/StRS rather than a separate fishing expedition. [cwnp](https://www.cwnp.com/req-eng/)

If this layer is done well, the SRS work becomes mainly a technical elaboration and decomposition step; if it is skipped or conflated with SRS, the project is at much higher risk of the very failures the CHAOS reports and NASA studies document.

---

## Additional Research & Evidence

*Supplementary research and evidence from a second research pass.*

# Creating a Business and Stakeholder Requirements Specification for a Greenfield Software Project

## What this requirements layer is and how standards position it

A Business Requirements Specification (BRS) / Stakeholder Requirements Specification (StRS) layer exists to translate a strategic vision into a precise, testable *statement of business needs and stakeholder outcomes*—while staying deliberately *implementation-free* (no solution design, no architecture, no UI design, no technology choices). In , this layer is explicitly described as "business requirements" and "stakeholder requirements" sitting above system/software requirements specifications (SyRS/SRS). The standard defines **business requirements** as a structured collection of information that frames an organisation's *motivation* and the *desired results* at the business-management level, and defines **stakeholder requirements** as the structured collection of requirements that capture stakeholder characteristics, context, concepts, constraints and priorities (and their relationship to the external environment). turn21view0

In the same standard's terminology, the downstream documents have a different intent and content shape: a (software) requirements specification is a structured collection of the essential requirements of the software (functions, performance, design constraints, attributes, and external interfaces), while a system requirements specification similarly focuses on functions, performance and constraints for the system and its operational environments/external interfaces. That is, Level 2 is where the requirements become *system- and software-facing* in a way that engineers can allocate, implement, and verify. turn21view0

The  curriculum also makes the separation of levels explicit. Its  distinguishes requirements such as **stakeholder requirements** (what stakeholders want from their perspective) and **user requirements** (what users want from their perspective) from **system requirements** (what a system shall do), and recommends that large specifications keep different abstraction levels separate—because high-level requirements are refined into lower-level requirements. It also notes that durable work products like business/stakeholder requirements specifications precede system requirements specifications in many contexts (even if, in some settings, they co-evolve). turn5view2

The practical implication for a greenfield project is that the BRS/StRS document should be readable and negotiable by business and domain stakeholders; it should establish the shared vocabulary and the domain boundaries; and it should provide an unambiguous "why/what must be true" foundation that can trace forward into the SyRS/SRS and later verification. turn46view1

## What belongs in BRS/StRS versus SRS

At this layer, the highest-value output is clarity: clarity of purpose, scope, stakeholders, desired outcomes, and the domain language. ISO's normative BRS content makes this concrete: a BRS should include business purpose and scope, major stakeholders, business environment, mission/goals/objectives, business model, information environment, business processes, and a high-level operational concept and scenarios—explicitly "without specifying design details." turn19view2

ISO's StRS example outline shows the stakeholder-facing analogue: stakeholder purpose/scope/overview, stakeholders and business environment, mission/goals/objectives, information environment, system processes, operational policies/rules, operational constraints, operational modes/states, operational quality, user requirements, operational concept, and operational scenarios. turn54view0

By contrast, SRS/SyRS content is where requirements are written in an engineer-verifiable form about functional behaviour, performance, constraints, and interfaces. ISO's SRS definition and SyRS/SRS content illustrate that the SRS becomes a structured collection of essential software requirements (functions, performance, design constraints, attributes, external interfaces), and system specifications include detailed areas such as security requirements and environmental conditions. turn19view3

A simple way to keep the boundary crisp is to treat the BRS/StRS as answering **"Why are we doing this, what outcomes must we achieve, and what must stakeholders be able to accomplish in the domain?"** while the SRS answers **"What must the software do (and how will we know it does it)?"** This framing is consistent with guidance that business requirements are about opportunity/objectives/success criteria/scope boundaries. turn17view1

Concrete examples below show correct placement for the *same* capability:

- **BRS (business outcome / success metric):** "Reduce average time-to-onboard a new customer from 5 working days to 1 working day within 3 months of launch, while maintaining regulatory compliance." (Outcome, measurable, business-facing; no solution details.) turn19view2  
- **StRS (stakeholder/user need, task-oriented):** "Customer Operations staff must be able to complete onboarding for a standard customer in a single session without switching tools, except where external verification is required." (Task and stakeholder perspective.) turn17view2  
- **SRS (software behaviour):** "When a Customer Operations user submits an onboarding case, the software shall validate required data fields, record the submission timestamp, and present a confirmation that includes the case reference." (Software behaviour; testable; still avoids UI specifics beyond what is necessary.) turn19view3

A recurring misplacement is to put technology or UI decisions into the BRS/StRS. Both ISO and Volere-style guidance warn against "solutions posturing as requirements" and against stakeholders expressing requirements in terms of familiar technology; this creates false constraints and prematurely narrows the solution space. turn43view1

## Recommended template structure for a combined BRS/StRS in a greenfield project

For a greenfield initiative, maintaining **one combined "BRS/StRS"** is often more effective than two separate documents—provided the structure preserves the separation between *business-management outcomes* and *stakeholder operational needs*. ISO explicitly allows the organisation and ordering of content to follow project information management policies (i.e., you can restructure and consolidate as long as the normative content is present). turn54view0

A combined template that stays faithful to ISO's BRS and StRS content, and aligns with IREB's "keep abstraction levels separate" guidance, can be organised as follows:

**Document control and vocabulary**
- Identification, revision, approvals, and references; acronyms/abbreviations; and a definitions section for terms with special meaning. (ISO expects these as general content items and explicitly calls for definitions beyond ordinary dictionary meaning.) turn19view1  
- A project glossary (see next section) treated as a controlled artefact, not a casual appendix. turn44view1  

**Business intent and boundaries**
- Business purpose/background (why the organisation is pursuing the change).   
- Business scope and out-of-scope, including the business domain name, the range of business activities included, and explicit exclusions. turn54view0  
- Business overview: major internal divisions and external entities and how they interrelate; ISO recommends a diagram. turn54view0  
- Business environment: relevant external/internal factors (laws/regulations, market dynamics, technology base, and similar). turn54view0  

**Mission, goals, success criteria**
- Mission, goals, objectives: "business results to be obtained through or by the proposed system." turn53view0  
- Success metrics: define measurable "how we judge success" criteria at business level; a useful pattern is to write objectives with measurable key results (OKR-style) so the success definition is explicit and gradeable. turn55view1  

**Stakeholders, user classes, and responsibilities**
- Major stakeholders / classes of stakeholders and how they influence or are impacted. turn54view0  
- User classes (distinct groups of users with different needs/constraints), plus non-user stakeholders (compliance, operations, finance, support, partners). This aligns with ISO's inclusion of "user classes and other involved personnel" in the high-level operational concept and aligns with user-class thinking in requirements practice. turn16view2  

**Domain model and shared mental model**
- Ubiquitous language and glossary ownership rules. turn5view2  
- Domain model (conceptual, not technical): key domain concepts, relationships, and boundaries (bounded contexts/context map where relevant). turn19view2  

**Business processes, scenarios, and rules**
- Business processes (ordered decomposition, named/numbered, diagrammed sequences of activities). turn53view3  
- High-level operational scenarios and operational concept (examples of interaction in context; "without specifying design details"). turn54view0  
- Business rules / operational policies and constraints, uniquely identified and referenced from processes. Business rules are not "software requirements" in themselves; they are directives (policy/regulation/standard) that should serve as origins for functional requirements that enforce or comply with them. turn9view1  

**Traceability and handoff requirements**
- Traceability approach: unique identifiers and a mapping model from business/stakeholder items to downstream requirements and verification. ISO explicitly treats traceability as a single point of accountability and stresses unique identifiers and maintenance of trace links through lifecycle phases. turn21view0  
- Acceptance framing at this level: for each business objective and major stakeholder outcome, define how success will be demonstrated (metrics, thresholds, time windows). Volere calls this the "fit criterion" concept: making requirements measurable prevents inconsistent interpretation across stakeholders, developers, and testers. turn43view1  

This structure intentionally places the glossary and domain model early, because terminology and conceptual alignment influence every later requirement statement and test decision. turn7view2

## Glossary and ubiquitous language at this stage

The strongest case for a glossary at the BRS/StRS layer is that natural language requirements are prone to **ambiguity, inaccuracy and inconsistency**, and that vocabulary itself is a measurable risk surface. NASA's SATC study of more than 50 NASA SRS documents used an automated measurement tool to assess document structure and vocabulary, and explicitly highlighted ambiguity/inaccuracy/inconsistency as severe problems in natural language specifications (and treated vocabulary quality as an assessable dimension). 

Likewise, the IREB syllabus states that RE efforts involving multiple people risk a lack of shared terminology understanding, and recommends recording a shared understanding of relevant terms in a glossary, explicitly addressing synonyms and homonyms and assigning clear ownership and maintenance practices. 

The ubiquitous language concept in Domain-Driven Design strengthens this: within a bounded context, teams are instructed to commit to using the same language consistently in speech, writing, diagrams and code, and to treat language changes as model changes. The DDD reference text also warns that "translation" between dialects (domain jargon vs technical language) blunts communication and can undermine modelling work. turn7view3

Empirical evidence on ambiguity is nuanced: one case study found extremely high ambiguity rates in a requirements document, but root-cause analysis attributed only a small portion of failures directly to ambiguity; instead, teams often invest substantial effort to clarify requirements through other mechanisms. This supports the pragmatic conclusion that ambiguity often produces hidden costs (clarification effort), even if it does not always surface as the *primary* proximate failure cause. 

Best-practice glossary design at this layer therefore focuses on *disambiguation and decision-making*, not just definitions:

- **Entry structure:** term, definition in domain language, usage notes (what it does *not* mean), synonyms (marked), homonyms (avoided or explicitly disambiguated), and at least one contextual example tied to a business process/scenario. turn44view1  
- **Governance:** a single maintained glossary (not duplicates), an explicit owner/small group responsible, and an expectation of stakeholder agreement on terminology. turn7view2  
- **Quality gates:** require that key requirements use glossary terms consistently; Volere explicitly treats "definition of essential terms" and consistent usage as reviewable quality criteria in a requirements gateway.   

## Domain modelling techniques appropriate for BRS/StRS

At this layer, "domain modelling" is not architecture. Its role is to create a *shared mental model* that supports consistent requirements, prioritisation, and later decomposition. ISO implicitly supports this by recommending diagrammatic business overviews and explicitly requiring that business and system processes be represented as diagrams showing sequences of activities. turn53view3

A practical portfolio of techniques that fit the BRS/StRS purpose includes:

- **Big-picture event exploration (EventStorming, Big Picture style):**  describes EventStorming as a workshop format for quickly exploring complex business domains, bringing question-askers and domain experts together to build a model collaboratively; the original description claims it can produce a comprehensive model of a business flow in hours rather than weeks. The mechanics emphasise starting from domain events placed on a timeline and using the workshop to reveal subdomains/bounded contexts, personas, and even key acceptance tests when ambiguities arise. turn25view0  
- **Context maps and bounded contexts:** the DDD reference advises explicitly identifying each model in play, naming each bounded context, making those names part of the ubiquitous language, and describing points of contact and translation between contexts. This is directly relevant to BRS/StRS because it prevents stakeholders and engineers from assuming one meaning for a term across different business areas. turn6view1  
- **Conceptual integrity as a quality driver:**  argued that conceptual integrity is central to system design quality, and that fragmentation of design ideas damages usability and coherence; the practical reading for requirements is that early agreement on the system's core concepts and language (before detailed requirements proliferate) reduces downstream incoherence.   
- **Task and usability-driven early exploration:** an experiment in requirements defect prevention found that emphasising better understanding of user tasks, early UI prototyping, and usability testing eliminated uncertainty about requirements during programming in a follow-on project, improved usability substantially, and correlated with delivery and commercial performance gains in that case context. This supports the broader claim that early domain and usage exploration can reduce rework and improve outcomes. turn49view2  


A pragmatic "definition of done" for the BRS/StRS domain model is not a perfect model; it is a model that is good enough to support: (a) stable vocabulary, (b) clear scope boundaries and external entities, (c) prioritisation of outcomes/features, and (d) traceable refinement into lower-level requirements. turn46view1

## Stakeholders, personas, user classes, success metrics, and traceability

### Stakeholder and persona documentation options and evidence

Three documentation approaches are commonly used at this layer; they are complementary rather than mutually exclusive:

**User classes (requirements-focused segmentation):** user classes group users into subsets that have different needs/constraints; this supports elicitation coverage and prevents the "monolithic user" fallacy. The CPRE syllabus explicitly separates stakeholder, user, and system requirements, and ISO's operational concept content expects identification of user classes and involved personnel at a high level. turn19view2

**Personas (empathy and decision alignment):** personas are often justified as a mechanism for building a shared understanding of users across a multidisciplinary team. A systematic mapping study notes that personas can help developers share a common understanding of users and maintain a unified vision of who end users are (even when disagreements emerge), while also highlighting practical limitations such as how much information is sufficient and representativeness. turn36view0

**Jobs-to-be-Done (outcome and circumstance framing):**  defines Jobs to Be Done as a lens for understanding the circumstances and forces that drive decisions, emphasising functional, social and emotional dimensions; this can be useful at BRS/StRS time because it keeps attention on *outcomes and context* rather than feature lists.   Origin narratives and practitioner implementations vary; the Strategyn history frames JTBD as an innovation discipline grounded in identifying customer "jobs" and attaching measurable outcomes to process steps. 

A practical "right level of detail" rule for BRS/StRS is: document **just enough** persona/user-class detail to clarify materially different goals, constraints, and success measures—without drifting into UI workflow design. This fits both ISO's "high-level scenarios" intent and the warning that feature-centred elicitation can yield fragmented, non-actionable requirements work. turn17view2

### Business success metrics, fit criteria, and the bridge to acceptance criteria

At BRS/StRS level, "acceptance" should be expressed primarily as **business success measures** and **stakeholder outcome measures**, not as software test cases. Two complementary constructs help:

- **OKR-style framing:** Google's guidance emphasises that objectives are ambitious outcomes, while key results are measurable and gradeable (ideally numeric) milestones; key results should describe outcomes rather than activities. This maps well to BRS goals and "success criteria" in business requirements practice. turn55view1  
- **Volere fit criteria:** Volere treats "fit criterion" as the mechanism that makes a requirement measurable and prevents divergent interpretation; it also treats vocabulary definition and consistency checking as explicit specification tests, and provides concrete fit-criterion examples (e.g., weight/size thresholds) to show how to make requirements objectively testable. turn43view1  

The bridge to SRS acceptance criteria then becomes systematic: business objectives and stakeholder outcomes generate measurable targets; these targets constrain and prioritise solution requirements; and the SRS expresses software behaviours and quality constraints that can be verified and traced back. turn46view1

### Traceability and common failure modes at this layer

ISO defines requirements traceability and a requirements traceability matrix as explicit artefacts, and describes traceability as accountability for tracing requirements back to sources and forward through lifecycle work products; it explicitly calls for associating verification methods/information and using unique identifiers. turn46view1

Empirical and industry evidence on requirement-quality impact consistently supports "invest early" logic:

- A NASA flight software-oriented paper notes that inconsistencies and errors in requirements contribute greatly to downstream cost, citing that a large fraction of errors are introduced in requirements/design stages but found later when correction is far more expensive.   
- A cost-escalation synthesis for errors reports steep increases from requirements-phase fix cost to later lifecycle phases (orders-of-magnitude ranges), reinforcing the value of early clarity and early defect finding.   
- A widely cited defect-reduction review reports substantial avoidable rework in software projects and highlights early verification/validation and prototyping as mechanisms to reduce downstream fixes.   
- A project-management synthesis referencing CHAOS findings lists lack of user input and incomplete/changing requirements as leading causes of failed or challenged projects, illustrating a recurring failure mode when teams skip or under-specify the stakeholder-facing layer.   

Observed failure modes specific to the BRS/StRS layer cluster into two patterns:

- **Jumping straight to features**: when elicitation focuses on "what features do you want?", teams risk building unused functionality and releasing products that still require rework because real user tasks were not understood. turn16view1  
- **Conflating 'why' with 'how'**: when stakeholders encode technology and design preferences as requirements, false constraints creep in and reduce solution flexibility; Volere explicitly warns that solution constraints should be only those that are truly non-negotiable, and its requirements tests explicitly flag "solutions posturing as requirements." turn44view1  

A combined BRS/StRS that is explicit about scope, vocabulary, stakeholder classes, business outcomes, operational scenarios, and trace links is therefore not "extra documentation"; it is a targeted control against the most common downstream waste: misbuilt functionality, uncontrolled scope growth, and expensive late clarification. turn46view1
