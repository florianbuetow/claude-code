# Behavioral Specification & Test Verification -- Reference Guide

## Table of Contents

- [1. Mental model: Levels 4–5 in a modern stack](#1-mental-model-levels-45-in-a-modern-stack)
- [2. Specification by Example: workflow, evidence, and failure modes](#2-specification-by-example-workflow-evidence-and-failure-modes)
- [3. BDD as a specification practice (not just a testing style)](#3-bdd-as-a-specification-practice-not-just-a-testing-style)
- [4. Writing acceptance criteria for maximum clarity and testability](#4-writing-acceptance-criteria-for-maximum-clarity-and-testability)
- [5. Test plans, test specifications, and exploratory charters](#5-test-plans-test-specifications-and-exploratory-charters)
- [6. Requirements traceability in practice](#6-requirements-traceability-in-practice)
- [7. Verification methods beyond "test": choosing inspection, analysis, demonstration, test](#7-verification-methods-beyond-test-choosing-inspection-analysis-demonstration-test)
- [8. Living documentation: tools, patterns, and maintenance](#8-living-documentation-tools-patterns-and-maintenance)
- [9. Relationship between unit, integration, and specification‑level tests](#9-relationship-between-unit-integration-and-specificationlevel-tests)
- [10. NFR verification planning (performance, security, accessibility)](#10-nfr-verification-planning-performance-security-accessibility)
- [11. Putting it together: a practical end‑to‑end workflow for a greenfield project](#11-putting-it-together-a-practical-endtoend-workflow-for-a-greenfield-project)
- [Additional Research & Evidence](#additional-research-evidence)
- [How Level four and Level five fit together in modern practice](#how-level-four-and-level-five-fit-together-in-modern-practice)
- [Specification by Example as an evidence-based workflow](#specification-by-example-as-an-evidence-based-workflow)
- [BDD as a specification practice: concepts, tools, and empirical findings](#bdd-as-a-specification-practice-concepts-tools-and-empirical-findings)
- [Writing acceptance criteria for clarity, testability, and edge-case coverage](#writing-acceptance-criteria-for-clarity-testability-and-edge-case-coverage)
- [Formal test plans and test case specifications that balance rigour with agility](#formal-test-plans-and-test-case-specifications-that-balance-rigour-with-agility)
- [Traceability and verification methods that prove requirements are met](#traceability-and-verification-methods-that-prove-requirements-are-met)
- [Living documentation, test strategy integration, and verifying non-functional requirements](#living-documentation-test-strategy-integration-and-verifying-non-functional-requirements)

---

Below is a structured, evidence-based guide that you can directly use as the Level‑4/5 backbone for a greenfield project.

***

## 1. Mental model: Levels 4–5 in a modern stack

Think of the bottom two layers as:

- **Level 4 – Behavioral specification / acceptance criteria**
  - Concrete examples, BDD scenarios, acceptance rules.
  - Primarily human-readable, but *designed to be executable*.
- **Level 5 – Formal verification artefacts**
  - Test plans, test cases, exploratory charters, NFR test specs.
  - Traceability matrices that prove every requirement has a verification method and outcome.

In modern practice, the Level‑4 examples *are* the acceptance tests; Level‑5 artefacts ensure coverage, risk management, and auditability.

***

## 2. Specification by Example: workflow, evidence, and failure modes

### 2.1 What Specification by Example is

Specification by Example (SbE) is a **collaborative** way of defining requirements and business‑oriented functional tests using **realistic examples** instead of abstract statements. Examples are written so they are: [en.wikipedia](https://en.wikipedia.org/wiki/Specification_by_example)

- precise enough to be executable,
- understandable by business stakeholders,
- maintainable as the system evolves.

Adzic's 2011 book distilled patterns from 50+ case studies across a range of organizations. The Agile Alliance summary emphasises four main benefits: living documentation, clear expectations, reduced rework, and confidence that the software built is fit for purpose. [infoq](https://www.infoq.com/articles/specification-by-example-book/)

### 2.2 The canonical SbE workflow

Adzic's process patterns can be summarized as this workflow: [projectmanagementplanet](https://www.projectmanagementplanet.com/specification-by-example/)

1. **Derive scope from goals**
   - Start from business goals (e.g. Volere PAM: Purpose–Advantage–Measurement) rather than a backlog of features. [cs.uic](https://www.cs.uic.edu/~i440/VolereMaterials/templateArchive16/c%20Volere%20template16.pdf)
2. **Specify collaboratively**
   - "Three Amigos" style conversations (business, dev, test) to clarify behavior before implementation.
3. **Illustrate with examples**
   - Capture concrete scenarios that illustrate the rule: normal cases, boundaries, and exceptions.
4. **Refine the specification**
   - Merge/normalize examples into coherent scenarios and tables.
5. **Automate without changing the spec**
   - Wrap automation *around* the agreed examples (step definitions/fixtures), rather than mutating the examples to fit tools. [infoq](https://www.infoq.com/articles/specification-by-example-book/)
6. **Validate frequently**
   - Run the executable specs in CI for every change; treat red examples as broken behavior.
7. **Evolve living documentation**
   - Keep examples and higher‑level views (feature maps, story maps) as the primary description of current system behavior. [blog.avanscoperta](https://blog.avanscoperta.it/2024/01/03/specification-by-example-bridring-the-communication-gap/)

### 2.3 Evidence for SbE

In 2020 Adzic surveyed 514 practitioners, 339 of whom use examples as acceptance criteria. [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

- Teams **using examples as acceptance criteria** self‑reported:
  - *"Great"* product quality ("users almost never experience problems in production"): **22%**.
  - *"Poor"* quality ("users experience serious problems frequently"): **7%**.
- Teams **not using examples**:
  - Great: **8%**.
  - Poor: **14%**.

When you look only at teams who use examples as acceptance criteria and further split by automation:

- With automation of examples:
  - Great: **26%**, Poor: **5%**.
- Without automation:
  - Great: **13%**, Poor: **11%**. [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

There is also strong correlation between using examples and generally "taking testing seriously" (81% of SbE teams using exploratory testing vs 73% overall). [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

Melnik's empirical work on Executable Acceptance Test‑Driven Development (EATDD) found that executable acceptance tests improved cross‑role communication, produced requirements that were unambiguous and verifiable, and provided sufficient traceability for regulated environments—but tool support and maintenance were significant pain points. [seriousxr](https://seriousxr.ca/wp-content/uploads/2022/11/MelnikPhD.pdf)

### 2.4 Success factors

Across Adzic's case studies and later reports, typical success factors include: [blog.avanscoperta](https://blog.avanscoperta.it/2024/01/03/specification-by-example-bridring-the-communication-gap/)

- **Goal‑driven scope**: user stories and features always linked to explicit business goals.
- **Regular collaborative workshops**: examples discovered *in conversation*, not by a BA writing specs alone.
- **Single source of truth per feature**: one canonical set of examples reused as spec, automated acceptance tests, and documentation.
- **Domain‑driven vocabulary**: examples in business terms, not GUI/control language.
- **Automation by the delivery team**: scenario automation owned by developers/testers in the team, not thrown over the wall to a test automation silo.
- **Tight CI integration**: fast feedback from executable specs.
- **Living documentation tooling**: ability to publish/read specs easily (e.g. SpecFlow+ LivingDoc, CucumberStudio, Concordion). [concordion](https://concordion.org/index.html)

### 2.5 Common failure modes

Common failure modes from Adzic's interviews and later surveys: [infoq](https://www.infoq.com/articles/specification-by-example-book/)

- **Tool‑driven "pseudo‑BDD"**  
  Teams jump straight to Gherkin automation without doing the collaborative discovery. Scenarios become thin technical scripts, not shared understanding.
- **Examples written by one role only**  
  A PO or QA writes scenarios alone; developers just "wire them up". You lose most of the value (shared understanding, surfacing unknowns).
- **Using Given/When/Then as a low‑level UI test script language**  
  Over‑detailed interaction steps that are brittle and slow; regression suite ossifies.
- **No ownership or versioning strategy for specs**  
  Feature files change without stakeholders knowing; drift from reality.
- **Treating Jira tickets as the documentation**  
  Adzic's 2020 survey shows that over half of teams consider the task tracker their "source of truth"; only ~12–20% use version‑controlled text specs as primary source, even in SbE teams. This undermines living documentation. [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

***

## 3. BDD as a specification practice (not just a testing style)

### 3.1 Origins and philosophy

Dan North introduced BDD around 2003–2006 as a way to reframe TDD in terms of *behavior* and *examples* rather than "tests". BDD formalized: [todaysoftmag](https://www.todaysoftmag.com/article/3298/behavior-driven-development-dan-north-interview)

- User story template:  
  "As a \<role\> I want \<feature\> so that \<benefit\>". [dannorth](https://dannorth.net/blog/introducing-bdd/)
- Scenario template:  
  **Given** some context, **When** an event occurs, **Then** an observable outcome should happen. [cucumber](https://cucumber.io/docs/bdd/history)

Cucumber's "History of BDD" page traces how JBehave and later Cucumber adopted Given/When/Then to capture acceptance criteria in an executable form, influenced by Domain‑Driven Design's ubiquitous language. [cucumber](https://cucumber.io/docs/bdd/history/)

Liz Keogh, one of the early BDD practitioners, emphasizes that BDD is fundamentally about **conversations**, not tools:

> "Having conversations is more important than capturing conversations is more important than automating conversations." [cucumber](https://cucumber.io/docs/bdd/myths/)

Cucumber's own documentation repeats this hierarchy. [cucumber](https://cucumber.io/blog/bdd/no-collaboration-without-conversation/)

### 3.2 How BDD works as a specification practice

At the analysis/specification level, a healthy BDD flow looks like:

1. **Discovery workshop (Three Amigos)**
   - Walk through stories from the user's perspective.
   - Ask "Can you give me an example?" until rules and boundaries are clear. [infoq](https://www.infoq.com/news/2015/04/experiments-BDD/)
2. **Formulate scenarios**
   - Turn examples into Given/When/Then scenarios, possibly supported by tables.
   - Only capture *what matters* to the business; leave implementation details to devs.
3. **Automate selected scenarios**
   - Map Gherkin steps to automation code (step definitions, fixtures).
   - Choose level (API/service vs UI) for each scenario based on value vs cost.
4. **Evolve**
   - Refactor and consolidate scenarios as behavior and understanding evolve.
   - Use living doc tools to keep specs browsable and trusted. [concordion](https://concordion.org/index.html)

### 3.3 Tools

Mainstream BDD tooling ecosystem:

- **Gherkin‑based**: Cucumber, SpecFlow, Behave, pytest‑bdd, JBehave, etc. [cucumber](https://cucumber.io/docs/bdd/history)
- **Table‑centric**: FitNesse, Robot Framework (keyword‑driven). [fitnesse](https://fitnesse.org/FitNesse/UserGuide.html)
- **HTML‑spec oriented**: Concordion (HTML/Markdown as living doc with embedded checks). [concordion](https://concordion.org)

Adzic's 2020 survey: 71% of SbE users primarily capture examples in Given/When/Then form; tables alone are now <10%. [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

### 3.4 Empirical evidence for BDD

The empirical base is still modest but growing:

- **Systematic mapping study (2006–2020)**  
  A 2023 mapping study identified BDD research trends and highlighted that benefits are mostly reported in terms of better communication, requirements understanding, and support for acceptance testing; quantitative defect‑reduction evidence is still scarce. [arxiv](https://arxiv.org/pdf/2305.05567.pdf)
- **Irshad et al. 2021 – BDD in large‑scale telecom product (Ericsson)**  
  In a multi‑team, multi‑site environment, practitioners reported the following *benefits* of BDD: [diva-portal](https://www.diva-portal.org/smash/get/diva2:1543163/FULLTEXT01.pdf)
  - better understanding of the **business aspect of requirements**,  
  - improved requirements quality,  
  - guidance for system‑level use cases,  
  - reuse of artifacts across teams,  
  - support for organizing testing.  
  Reported *challenges* included: behavior ownership, tool adoption, large‑scale coordination, and versioning of behaviors. [diva-portal](https://www.diva-portal.org/smash/get/diva2:1543163/FULLTEXT01.pdf)
- **Survey of practitioners (Binamungu et al., summarized in Irshad)**  
  Perceived BDD benefits: improved testability of requirements, better documentation, better domain knowledge capture, and better implementation alignment. [diva-portal](https://www.diva-portal.org/smash/get/diva2:1543163/FULLTEXT01.pdf)
- **EATDD (executable acceptance tests)**  
  Melnik's work found that executable acceptance tests were unambiguous, consistent, verifiable from both business and technical perspectives, and provided sufficient traceability for regulated domains. [seriousxr](https://seriousxr.ca/wp-content/uploads/2022/11/MelnikPhD.pdf)

Overall: the empirical story is **strongest** on *communication, requirements quality, and traceability*; quantitative defect data is less mature but consistent with results from TDD and test‑first practices more generally (e.g., 40–90% defect density reductions in Microsoft and IBM case studies of TDD). [microsoft](https://www.microsoft.com/en-us/research/wp-content/uploads/2009/10/Realizing-Quality-Improvement-Through-Test-Driven-Development-Results-and-Experiences-of-Four-Industrial-Teams-nagappan_tdd.pdf)

### 3.5 Challenges specific to BDD

From the industrial evaluations and practitioner reports: [lisihocke](https://www.lisihocke.com/2017/06/our-first-take-on-bdd.html)

- **Specification and ownership of behaviors**  
  Who "owns" a scenario? Product? Team? System? Lack of clear stewardship leads to duplication and rot.
- **Versioning of behaviors**  
  Scenarios crosscut architecture and roadmaps; keeping them in sync with evolving systems is non‑trivial.
- **Tooling & training**  
  Gherkin tools introduce new stacks and build plumbing; training is needed to avoid poor step design.
- **Scale**  
  In large programs, maintaining thousands of scenarios without a domain‑oriented structure is a nightmare.

Designing your artefacts to support *modular, domain‑based organization* (bounded contexts, feature folders, tags) is critical at greenfield time.

***

## 4. Writing acceptance criteria for maximum clarity and testability

You want a small toolkit of forms and choose per requirement. The main patterns:

- Given/When/Then scenarios (BDD style).
- Volere "fit criteria".
- EARS structured requirements.
- Decision / example tables.
- State transition models.

### 4.1 Given/When/Then scenarios

**Use when**: describing discrete user‑visible behaviors and workflows.

**Template**

```gherkin
Scenario: <short business-focused title>
  Given <precondition / starting context>
  And <additional preconditions>
  When <event or action>
  And <additional actions>
  Then <observable outcome>
  And <additional outcomes>
```

**Example (core case + edge)**

```gherkin
Feature: Reset password

  Scenario: Successful password reset via email link
    Given a registered user with email "alice@example.com"
    And the user has not requested a reset in the last 10 minutes
    When the user requests a password reset
    Then a reset email is sent to "alice@example.com"
    And the reset link is valid for 30 minutes
    And the reset link can be used exactly once

  Scenario: Reset link expired
    Given a registered user with email "alice@example.com"
    And the user requested a password reset more than 30 minutes ago
    When the user clicks the reset link
    Then the system rejects the link
    And the user is prompted to request a new password reset
```

Adzic's survey shows Given/When/Then is the dominant format for examples among SbE users. It is especially good for: [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

- capturing **flow** and user intent,
- making acceptance criteria executable via Cucumber/SpecFlow/etc. [cucumber](https://cucumber.io/docs/bdd/history)

### 4.2 Volere fit criteria

Volere's key idea: every requirement must have a **fit criterion**—a measurement that lets you decide if a solution satisfies it. [reqview](https://www.reqview.com/doc/volere-template/)

**Template (functional example)**

> Requirement: The system shall validate password strength.  
> Fit criterion: At least 95% of passwords created in a 6‑month pilot must pass an offline zxcvbn strength score ≥ 3, and fewer than 1% of users must contact support citing password creation difficulty. [cs.uic](https://www.cs.uic.edu/~i440/VolereTemplate.pdf)

Fit criteria are especially effective when:

- you need **measurable, contract‑level** acceptance,
- requirements involve quality attributes (performance, security, usability) that could otherwise stay vague. [cin.ufpe](https://www.cin.ufpe.br/~if716/arquivos20192/04-Volere)

### 4.3 EARS (Easy Approach to Requirements Syntax)

EARS gives structured sentence templates for common requirement patterns: ubiquitous, event‑driven, state‑driven, optional features, and unwanted behaviour. [reqassist](https://reqassist.com/blog/ears-requirements-syntax)

**Patterns** (simplified):

- **Ubiquitous**:  
  "The \<system\> shall \<response\>."
- **Event‑driven**:  
  "When \<trigger\>, the \<system\> shall \<response\>." [edu.qracorp](https://edu.qracorp.com/hubfs/EARSConfigurationsPartTwo.pdf)
- **State‑driven**:  
  "While \<state\>, the \<system\> shall \<response\>." [reqassist](https://reqassist.com/blog/ears-requirements-syntax)
- **Optional feature**:  
  "Where \<feature present\>, the \<system\> shall \<response\>." [reqassist](https://reqassist.com/blog/ears-requirements-syntax)
- **Unwanted behaviour**:  
  "If \<undesired event\>, then the \<system\> shall \<mitigating response\>." [2367473.fs1.hubspotusercontent-na1](https://2367473.fs1.hubspotusercontent-na1.net/hubfs/2367473/EARS%20Configuration%20PDF.pdf)

EARS explicitly calls out **unwanted behaviour** as a major omission risk and recommends a second pass dedicated to it. [ccy05327.github](https://ccy05327.github.io/SDD/08-PDF/Easy%20Approach%20to%20Requirements%20Syntax%20(EARS).pdf)

**Examples**

- Event‑driven:

> When the user presses "Submit order", the system shall validate the shopping cart and calculate final price including taxes and discounts.

- Unwanted behaviour:

> If the payment provider times out, then the system shall mark the order as "Pending payment" and notify the user to retry later.

EARS works well for Level‑2 SRS and also for tightening Level‑4 acceptance criteria, particularly for edge/failure cases.

### 4.4 Decision / example tables

**Use when**: behavior depends on combinations of input conditions.

**Template**

| Condition / Input                         | Case 1 | Case 2 | Case 3 | Case 4 |
|------------------------------------------|--------|--------|--------|--------|
| Customer type = "standard"               | Y      | Y      | N      | N      |
| Cart total ≥ 100 EUR                     | N      | Y      | N      | Y      |
| Voucher is valid and not expired         | N      | N      | Y      | Y      |
| **Expected: discount applied**           | 0%     | 10%    | 15%    | 20%    |

Each column is an example; in Gherkin you can use `Scenario Outline` with an examples table to automate. [altexsoft](https://www.altexsoft.com/blog/acceptance-criteria-purposes-formats-and-best-practices/)

Decision tables:

- force teams to enumerate **boundaries and combinations**,
- are particularly effective for complex pricing, rules, and validation logic.

### 4.5 State transition specifications

**Use when**: behavior depends strongly on lifecycle state and events.

**Simple state table**

| Current state | Event                   | Next state   | Expected outcome                                  |
|---------------|------------------------|-------------|--------------------------------------------------|
| Draft         | Submit for approval    | Pending     | Version locked; approver notified.               |
| Pending       | Approver approves      | Approved    | Item becomes visible to end users.               |
| Pending       | Approver rejects       | Rejected    | Rejection reason recorded; author notified.      |
| Approved      | Author edits content   | Draft       | New version in Draft; old version still Approved |

State models:

- prevent contradictory rules,
- make it easier to design **property‑based** and **mutation tests** around invariants later.

### 4.6 Edge cases, failure modes, and "unwanted behaviour"

Alistair Cockburn notes that the **extension conditions** of a use case (alternate flows and failures) "provide a framework for investigating all the little, niggling things that somehow take up 80% of the development time and budget." EARS' authors likewise identify omissions around unwanted behaviour as a primary defect source. [scalingsoftwareagility.files.wordpress](https://scalingsoftwareagility.files.wordpress.com/2009/11/ch-19-use-cases-draft.pdf)

Practical techniques:

- In each SbE/BDD workshop, dedicate explicit time to:
  - boundary values (0, 1, many),
  - invalid inputs,
  - downstream/system‑failure conditions (timeouts, partial outages),
  - security and abuse cases (misuse stories, adversarial examples). [owasp](https://owasp.org/www-project-web-security-testing-guide/v41/2-Introduction/)
- Use EARS **unwanted behaviour** template and decision tables to capture them systematically.
- For high‑risk areas, complement examples with **properties** (e.g. balances never negative) and use property‑based testing later. [research.tudelft](https://research.tudelft.nl/en/publications/propr-property-based-automatic-program-repair/)

***

## 5. Test plans, test specifications, and exploratory charters

### 5.1 Classical standards vs modern lightweight practice

**IEEE 829** (now subsumed by ISO/IEC/IEEE 29119‑3) defined a detailed structure for test documentation: test plan, test design, test case, test procedure, test log, incident report, summary report. ISO/IEC/IEEE 29119‑2/‑3 generalize this with process definitions and template‑based documentation, while remaining life‑cycle agnostic. [embeddedlinuxtestengineer](http://embeddedlinuxtestengineer.com/IEEE_Standard_829_Test_Plan.html)

Industrial practice tends to use **lighter versions** of these, keeping the *information* while collapsing the number of documents.

### 5.2 Recommended agile test plan structure

For a greenfield system, a single **Test Strategy / Master Test Plan** for the product, plus sprint‑level notes, is usually enough. Based on 829/29119 guidance: [cs.otago.ac](http://www.cs.otago.ac.nz/cosc345/lecs/lec22/testplan.htm)

1. **Test Plan Identifier**
2. **Introduction**
   - System under test, scope, business goals.
3. **Test Items**
   - Services/components, versions, environments.
4. **Features to be tested**
   - Mapped to requirements (IDs) and risk (high/medium/low).
5. **Features not to be tested**
   - And rationale (e.g., out of scope for this release).
6. **Test approach**
   - Overall strategy (risk‑based), test pyramid / trophy stance.
   - Types: unit, integration, contract, E2E, acceptance (BDD), exploratory, performance, security, accessibility, etc. [standards.ieee](https://standards.ieee.org/ieee/29119-2/7498/)
7. **Item pass/fail criteria**
   - What constitutes "done" at each level (e.g., thresholds for NFRs, SbE suite green, mutation score floor).
8. **Suspension/resumption criteria**
   - When to stop a test run/build (e.g., severe incident, environment instability).
9. **Test deliverables**
   - Repos, reports, living documentation, logs, dashboards.
10. **Testing tasks**
    - Backlog of testing‑related tasks (incl. tool setup, data mgmt).
11. **Environmental needs**
    - Test environments, data, tools.
12. **Responsibilities**
    - Who owns what (roles, not necessarily "testers").
13. **Schedule and milestones**
    - Per release / per increment.
14. **Risks and contingencies**
    - Testing‑related risks and mitigations (e.g., flaky E2E env).
15. **Approvals**

Keep this as a **living document** under version control; reference it from the repo README and CI pipeline.

### 5.3 Test case specification (scripted tests)

Even in BDD‑heavy stacks you'll have scripted tests that aren't expressed as Gherkin scenarios (e.g., low‑level API tests, NFR checks). A lean test case spec derived from IEEE 829 looks like: [web.cs.dal](https://web.cs.dal.ca/~arc/teaching/CS3130/Templates/TestingTemplates/Test%20Plan%20Templates/IEEEStandardTestPlans.doc)

- Test Case ID
- Title / objective
- Related requirement ID(s)
- Pre‑conditions
- Test steps (or reference to automated test name)
- Test data
- Expected results / oracle (link to acceptance criteria or property)
- Post‑conditions
- Priority
- Verification method (Inspection / Analysis / Demonstration / Test) [reqview](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/)
- Automation status (manual / automated + path)

### 5.4 Exploratory testing and test charters

ISO/IEC/IEEE 29119 defines exploratory testing as experience‑based testing where the tester designs and executes tests on the fly based on prior knowledge and results. Charters provide just enough structure. [wildart.github](https://wildart.github.io/MISG5020/standards/ISO-IEC-IEEE-29119-2.pdf)

**Charter template (adapted from TMap / session‑based testing)** [tmap](https://www.tmap.net/wp-content/uploads/sites/17/2025/08/Exploratory-Testing-Charter-Explanation-v1.2_0.pdf)

- Charter ID and name.
- **Mission**: one‑sentence goal (e.g., "Explore error handling around payment timeouts on mobile web checkout.")
- Timebox: 60–120 minutes.
- **Scope**
  - Features to cover.
  - Out of scope.
- **Setup**
  - Build, environment, test data, tools.
- **Focus areas / test ideas**
  - Risks, tours, personas, NFRs to pay attention to.
- **Notes**
  - Observations, questions, coverage notes.
- **Anomalies**
  - References to defects raised.
- **Conclusion**
  - Summary of product quality and remaining risks.
- **Recommendation**
  - E.g., "fit for release" / "further exploration recommended".

In regulated or high‑risk contexts, use charters to satisfy ISO 29119's documentation expectations while preserving exploratory flexibility. [csa](https://www.csa.ch/en/blog/testing-non-functional-requirements-a-contradiction)

***

## 6. Requirements traceability in practice

### 6.1 Concepts and types of traceability

Requirements traceability is the ability to link requirements to other artefacts—origins, design, code, tests, defects, and deployed behavior. [en.wikipedia](https://en.wikipedia.org/wiki/Requirements_traceability)

Classic distinctions: [torkar.github](https://torkar.github.io/pdfs/00-SUBMITTED-PAPER.pdf)

- **Pre‑RS traceability** (pre‑requirements specification)
  - Links requirements to their **origins**: interviews, business rules, stakeholder decisions, earlier documents.
  - Helps answer: "Why does this requirement exist? Who asked for it? What problem does it solve?" [dirkriehle](https://dirkriehle.com/wp-content/uploads/2022/06/Krause-etal_2022_REconf_The_Benefits_of_Pre_RS_Traceability.pdf)
- **Post‑RS traceability**
  - Links SRS requirements to design elements, code, test cases, and test results.
- **Forward traceability**
  - From requirements to downstream artefacts (design, code, tests).
- **Backward traceability**
  - From tests/defects/design back to requirements and upstream goals. [en.wikipedia](https://en.wikipedia.org/wiki/Requirements_traceability)

SLRs show that pre‑RS traceability is under‑researched but offers major benefits for change impact analysis, prioritization, and reasoning about rationale. [dirkriehle](https://dirkriehle.com/wp-content/uploads/2024/01/s00766-023-00412-z.pdf)

### 6.2 Requirements Traceability Matrix (RTM) structure

A typical RTM includes at least: requirement IDs, related design elements, test case IDs, and test results. [haisanthanhhang](http://haisanthanhhang.com/upload/files/38681102384.pdf)

For your hierarchy, you can extend to:

| Business Goal | Stakeholder Need | System Requirement | BDD Scenario | Test Case | Verification Method | Test Result |
|---------------|------------------|--------------------|-------------|----------|---------------------|------------|
| BG‑001        | SN‑003           | SR‑017             | SCN‑payment‑happy‑path | TC‑API‑PAY‑001 | Test (automated API) | Pass (build 42) |
| BG‑001        | SN‑003           | SR‑018 (timeout handling) | SCN‑payment‑timeout | TC‑API‑PAY‑004; ET‑CH‑05 | Test + Exploratory | Fail (defect DEF‑231) |
| BG‑002        | SN‑007           | NFR‑PERF‑003       | –           | PERF‑CART‑LAT‑SLO | Analysis + Test (k6) | Pass (p99<1s) |

Jama and others recommend columns like: high‑level requirements (business needs), system requirements, test cases, test results, and defects. [haisanthanhhang](https://haisanthanhhang.com/upload/files/38681102384.pdf)

### 6.3 Tools

- Heavyweight: IBM DOORS, Jama Connect, Polarion, etc.
- Lightweight:
  - Markdown/CSV tables in Git (version‑controlled RTM).
  - Linking in requirements tools like ReqView, which has explicit trace links and verification method fields. [reqview](https://www.reqview.com/blog/2019-02-27-news-volere-requirements-specification-template/)
  - Linking BDD features/scenarios to Jira/Azure DevOps items (SpecSync, Cucumber for Jira, SpecFlow+ integrations). [standards.ieee](https://standards.ieee.org/ieee/29119-3/7499/)

### 6.4 Evidence: benefits and adoption challenges

A systematic review by Torkar et al. highlights: [torkar.github](https://torkar.github.io/pdfs/00-SUBMITTED-PAPER.pdf)

- **Benefits**:
  - better support for change impact analysis,
  - improved coverage assurance,
  - support for compliance and audits.
- **Adoption challenges**:
  - perceived high effort and maintenance cost,
  - lack of training and tool support,
  - informal dev methods,
  - unclear ownership of trace links,
  - role‑dependent benefits (e.g., test leads and safety engineers value it more than individual devs).

A more recent SLR on **pre‑RS traceability** confirms similar themes and stresses that linking to origin artifacts helps answer "why" and "who" questions for requirements, which becomes crucial in long‑lived systems. [dirkriehle](https://dirkriehle.com/wp-content/uploads/2022/06/Krause-etal_2022_REconf_The_Benefits_of_Pre_RS_Traceability.pdf)

Some industrial reports indicate substantial reductions in requirements‑related defects when traceability goals are set and RTM use is explicit (e.g., PMI‑noted teams with explicit RT goals reporting ~30% fewer requirements defects). [kualitee](https://www.kualitee.com/blog/test-management/requirements-traceability-matrix-death-by-excel-or-a-useful-tool/)

***

## 7. Verification methods beyond "test": choosing inspection, analysis, demonstration, test

ISO/IEC/IEEE 29148 defines four standard verification methods for requirements: [drkasbokar](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)

- **Inspection**  
  Structured examination (reviews, inspections, walkthroughs) of artefacts to confirm requirements are well‑formed and correctly implemented.
- **Analysis (or simulation)**  
  Use of models, calculations, static analysis, or prototypes to show requirements are satisfied (e.g., performance modeling, formal proofs).
- **Demonstration**  
  Observing operation under specific conditions, often informal but scripted (e.g., demo to stakeholder).
- **Test**  
  Executing the system with specific inputs and checking observable behavior against expected results.

### 7.1 Evidence for reviews/inspections

Boehm & Basili's "Software Defect Reduction Top 10 List" compiles data showing that **peer reviews catch around 60% of defects on median, with reported ranges from 31% to 93%**. Aggregated data in Code Complete and other sources show: [slideplayer](https://slideplayer.com/slide/16557549/)

- modal defect detection rates:
  - unit tests ~30%,
  - integration tests ~35–40%,
  - formal code inspections ~55–70%. [carver.cs.ua](http://carver.cs.ua.edu/Slides/2019/URSSI-WinterSchool/URSSI-WinterSchool-PeerCodeReview.pdf)

Peer reviews typically cost ~10–15% of project effort but can eliminate a large portion of defects early, yielding large savings in rework (Boehm & Basili estimate 40–50% of current effort is avoidable rework). [cs.umd](https://www.cs.umd.edu/projects/SoftEng/ESEG/papers/82.78.pdf)

### 7.2 Practical framework for per‑requirement verification choice

In your SRS and RTM, add a **"Verification method"** field (29148/ReqView explicitly recommend this). [well-architected-guide](https://www.well-architected-guide.com/documents/iso-iec-ieee-29148-template/)

Guidelines:

- **Purely documentary requirements** (policies, legal constraints, some UI copy)
  - Primary: **Inspection** (document review).
- **Algorithmic correctness / critical business rules**
  - Require: **Analysis + Test**.
  - Examples: desk‑check formulas, property‑based tests, high mutation score. [arxiv](https://arxiv.org/abs/2103.07189)
- **User workflows / UI behavior**
  - Primary: **Test** (automated + exploratory) and **Demonstration**.
- **Safety / high‑criticality requirements**
  - Strong combination: **Inspection (formal review)** + **Analysis** (e.g., FMEA) + **Test**. [csa](https://www.csa.ch/en/blog/testing-non-functional-requirements-a-contradiction)
- **Performance and scalability**
  - Primary: **Analysis** (capacity planning, modeling) + **Test** (load/perf testing with thresholds tied to SLOs). [markosrendell.wordpress](https://markosrendell.wordpress.com/2019/06/05/slis-and-slos-versus-nfrs/)
- **Security requirements**
  - **Analysis** (threat modeling, ASVS/WSTG requirements) + **Test** (penetration testing, automated security scans) + **Inspection** (config/code reviews). [owasp](https://owasp.org/www-community/Threat_Modeling_Process)
- **Accessibility requirements**
  - **Inspection** (WCAG checklists) + **Test** (automated checks, assistive technology tests, user testing). [ucop](https://www.ucop.edu/electronic-accessibility/standards-and-best-practices/levels-of-conformance-a-aa-aaa.html)

At Level‑4/5, codify this as:

- a verification‑method column on each requirement,
- a mapping table in your test strategy explaining how each method is realized in your toolchain.

***

## 8. Living documentation: tools, patterns, and maintenance

### 8.1 Concept

"Living documentation" is documentation that is **kept in sync with the system via automation** and shared artefacts, not written once and left to rot. Cyrille Martraire's book frames it as documentation that "evolves at the same pace as the code" across business goals, domain knowledge, architecture, and deployment. [exmon01.external.cshl](https://exmon01.external.cshl.edu/v/pub/goto/TC/living_documentation.pdf)

Adzic and Evans initially coined the term for executable specifications (SbE) that act as both acceptance tests and reference docs; David Farley extended it to "continuous compliance" for regulated systems. [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

### 8.2 Tools and patterns

Typical patterns:

- **Executable specifications**:
  - Gherkin + Cucumber/SpecFlow: scenarios stored in Git, run in CI, published via CucumberStudio, SpecFlow+ LivingDoc, or similar. [standards.ieee](https://standards.ieee.org/ieee/29119-3/7499/)
  - HTML/Markdown specs with embedded checks: Concordion, which emphasizes "beautiful living documentation" with inline pass/fail status. [concordion](https://concordion.org)
  - Wiki‑based acceptance tests: FitNesse, where wiki pages double as specs and test suites. [fitnesse](https://fitnesse.org/FitNesse/UserGuide.html)
- **Publishing from code repos into collaboration tools**
  - Cucumber for Jira, SpecSync + Azure DevOps, etc. synchronize feature files with work items and present test status in the ALM tool. [standards.ieee](https://standards.ieee.org/ieee/29119-3/7499/)
- **Domain‑oriented organization**
  - Specs organized by bounded context/feature map, not by sprint or ticket; story mapping or feature mapping layered over specs. [reintech](https://reintech.io/blog/introduction-to-test-automation-with-fitnesse-and-concordion)

### 8.3 Evidence and trade‑offs

Adzic's 2020 survey shows that:

- Using examples as acceptance criteria correlates with higher self‑reported quality, and **automating those examples roughly doubles the proportion of teams rating their quality as "great"** relative to non‑automating SbE users (26% vs 13%). [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)
- About one‑third of teams who use examples **do not** automate them; they gain collaboration benefits but miss out on living documentation and regression protection. [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)
- Only ~12–20% of respondents treat version‑controlled feature/spec files as their primary requirements source; most still rely on task trackers (Jira, etc.), limiting the potential of living docs. [gojko](https://gojko.net/2020/03/17/sbe-10-years.html)

Melnik's EATDD work showed that executable acceptance tests can be sufficient evidence for traceability and compliance, but tool immaturity made artefacts hard to maintain and scale. [seriousxr](https://seriousxr.ca/wp-content/uploads/2022/11/MelnikPhD.pdf)

### 8.4 Maintenance practices

To keep living documentation *alive*:

- **Same repo, same lifecycle**
  - Store specs alongside code; refactor them with code changes.
- **Make them the path of least resistance**
  - Scripts to render specs as HTML and publish to the team portal.
  - IDE plugins for Gherkin/Concordion to make editing convenient. [concordion](https://concordion.org/index.html)
- **Treat specs as first‑class code**
  - Code reviews that include scenarios.
  - Use mutation testing/property‑based testing to keep examples and oracles honest. [research.tudelft](https://research.tudelft.nl/en/publications/propr-property-based-automatic-program-repair/)
- **Governance**
  - Conventions for scenario naming, tagging, and structure.
  - Rules for when to delete/merge outdated scenarios (e.g., when a feature is removed).

***

## 9. Relationship between unit, integration, and specification‑level tests

### 9.1 Test pyramid and test trophy

Mike Cohn's original **test pyramid** suggests many fast unit tests at the base, fewer service (API) tests in the middle, and very few UI/E2E tests at the top. The rationale: UI tests are slower and brittler, so prefer lower layers when possible. [ontestautomation](https://www.ontestautomation.com/the-test-automation-pyramid/)

Kent C. Dodds' **testing trophy** revises this: emphasize **static checks and integration tests** more heavily, with a moderate number of unit tests and a small number of E2E tests. [software-engineering-unlocked](https://www.software-engineering-unlocked.com/double-down-integration-tests-kent-dodds/)

Practical synthesis:

- **Static checks**: linters, type checkers, formatters, SAST.
- **Unit tests**: small, local behavior; fast and numerous.
- **Integration tests**: components working together (e.g. service + DB), often black‑box.
- **E2E / system tests**: full stack from user entrypoint.

Specification‑level BDD/SbE tests usually live at the **integration or system level**:

- Ideally at **API/service boundary** (fast, stable, few dependencies).
- Some at **UI level** for critical user journeys.

### 9.2 Where contract, property‑based, and mutation testing fit

- **Contract tests (Pact, CDC)**  
  Consumer‑driven contract tests verify that services adhere to agreed request/response contracts, allowing independent deployment of microservices. [dev](https://dev.to/paulsebastianmanole/consumer-driven-contract-testing-with-pact-the-basics-4fk9)
  - Sit between integration and system levels.
  - Reduce need for brittle cross‑service E2E tests.
- **Property‑based tests (QuickCheck, Hypothesis, etc.)**  
  Define general properties (invariants) and let the tool generate many input cases. [seas.upenn](https://www.seas.upenn.edu/~cis5520/current/lectures/soln/05-quickcheck/QuickCheck.html)
  - Ideal for core algorithms, data transformations, and critical financial/quantitative logic.
  - Empirical studies (including for quantum software and APR) show high mutation scores (0.90–0.92), and in APR, properties lead to faster repairs with lower overfitting than unit tests alone. [arxiv](https://arxiv.org/html/2503.22641v1)
- **Mutation testing**  
  Injects small code changes (mutants) and checks if tests detect them. A large ICSE study on ~15M mutants at Google found that mutation testing encourages developers to write more and better tests, improving suites' effectiveness and correlating mutants with real faults. [homes.cs.washington](https://homes.cs.washington.edu/~rjust/publ/mutation_testing_practices_icse_2021.pdf)

These techniques complement BDD:

- BDD scenarios specify external behavior and key examples.
- Property‑based and mutation tests harden the **lower levels** against corner cases and spec gaps.

### 9.3 Documenting test strategy

In the test plan, include a short **"test strategy matrix"**:

| Layer / Type        | Goal                          | Tools / Tech      | Relation to specs |
|---------------------|-------------------------------|-------------------|-------------------|
| Static checks       | Style, basic correctness      | linters, types    | Preconditions for CI |
| Unit tests          | Local correctness             | xUnit, PBT        | Support SbE by making example cases feasible |
| Integration tests   | Service behavior & contracts  | xUnit, Pact       | Many BDD scenarios live here |
| System / E2E tests  | Critical user journeys        | BDD+UI, Selenium  | Only highest‑value flows |
| NFR tests           | Perf, security, accessibility | k6, OWASP, a11y   | Derived from NFRs in SRS |
| Exploratory         | Unknown risks                 | Charters          | Driven by risk and recent changes |

***

## 10. NFR verification planning (performance, security, accessibility)

### 10.1 General principles

Recent standards (e.g. ISO/IEC 25010, 29148) move away from "non‑functional" as a category and instead treat **quality characteristics** (performance, security, usability, etc.) as requirements with explicit verification methods. [csa](https://www.csa.ch/en/blog/testing-non-functional-requirements-a-contradiction)

Key ideas:

- Express NFRs with **fit criteria** (quantified goals). [cs.uic](https://www.cs.uic.edu/~i440/VolereMaterials/templateArchive16/c%20Volere%20template16.pdf)
- Tie perf/security/accessibility verification back to **SLOs, regulations, and standards** (e.g. WCAG, OWASP ASVS). [owasp](https://owasp.org/www-project-developer-guide/release/security_gap_analysis/guides/asvs/)
- Plan verification as a mix of **analysis + test + inspection**.

### 10.2 Performance and load

Tie performance requirements to **SLIs, SLOs, and thresholds**. [notes.nicolevanderhoeven](https://notes.nicolevanderhoeven.com/Test+criteria)

**Example NFR and verification**

- Requirement NFR‑PERF‑003:

> The checkout API shall respond within 1000 ms for 99% of requests under a sustained load of 100 requests/second, with an error rate <1%.

- Fit criterion:
  - p99 latency ≤ 1000 ms, error rate <1% under defined load profile in a standard test environment. [grafana](https://grafana.com/docs/k6/latest/examples/get-started-with-k6/test-for-performance/)
- Verification:
  - **Analysis**: capacity model using historical traffic and growth projections.
  - **Test**: load tests with k6 or similar, codifying SLOs as thresholds. [deepwiki](https://deepwiki.com/grafana/k6-learn/3.7-setting-test-criteria-with-thresholds)

k6 thresholds make SLOs executable:

```js
export const options = {
  thresholds: {
    http_req_failed: ['rate<0.01'],      // <1% errors
    http_req_duration: ['p(99)<1000'],   // p99 < 1s
  },
};
```

Record each test run in the RTM against NFR‑PERF‑003.

### 10.3 Security

Use two layers:

1. **Specification / requirements**
   - Derive security requirements from:
     - threat modeling (STRIDE, misuse cases), [owaspsamm](https://owaspsamm.org/model/design/threat-assessment/stream-b/)
     - OWASP ASVS requirement catalog for web/app security, [top10proactive.owasp](https://top10proactive.owasp.org/archive/2018/c1-security-requirements/)
     - regulatory obligations.
2. **Verification plan**
   - Map each security requirement to:
     - **Analysis**: threat modeling reviews, architecture reviews. [owasp](https://owasp.org/www-community/Threat_Modeling_Process)
     - **Test**: OWASP Web Security Testing Guide test cases (WSTG), penetration testing, SAST/DAST scans. [owasp.boireau](https://owasp.boireau.io:8443/checklist)
     - **Inspection**: config reviews (TLS, headers, access control).

**Example**

- Requirement SEC‑AUTH‑005:

> After 6 consecutive failed login attempts, the account shall be locked for at least 15 minutes.

- Fit criterion: WSTG authentication tests must confirm lockout; logs show no bypass; ASVS requirement V2.* lockout criteria satisfied. [owasp](https://owasp.org/www-project-developer-guide/release/security_gap_analysis/guides/asvs/)
- Verification:
  - Automated security tests (WSTG‑ATHN‑03 style), manual penetration test attempt, plus code/config review.

### 10.4 Accessibility (WCAG)

WCAG 2.1 defines success criteria at levels A, AA, AAA, with AA usually recommended as the minimum target. [w3](https://www.w3.org/TR/WCAG21/)

**Example requirements**

- ACC‑GEN‑001:

> Public web content shall conform to WCAG 2.1 Level AA.

- Verification:
  - **Inspection**: WCAG checklist review for templates. [levelaccess](https://www.levelaccess.com/resources/must-have-wcag-2-1-checklist/)
  - **Automated tests**: axe, pa11y, etc. integrated into CI.
  - **Manual tests**: keyboard‑only navigation, screen reader checks.
  - **User testing** with assistive tech for critical flows where feasible.

Add WCAG criteria references (e.g. 1.4.3 contrast, 2.1.1 keyboard) in the RTM so each is tied to test cases and outcomes.

***

## 11. Putting it together: a practical end‑to‑end workflow for a greenfield project

Here is a concrete implementation roadmap that ties Levels 4–5 together.

### 11.1 Start from goals and traceability

1. Define **Business Goals (BG‑xxx)** with Volere PAM and fit criteria. [cin.ufpe](https://www.cin.ufpe.br/~if716/arquivos20192/04-Volere)
2. Derive **Stakeholder Needs (SN‑xxx)** and **System Requirements (SR‑/NFR‑xxx)** using EARS and Volere fit criteria; assign verification methods per 29148. [reqview](https://www.reqview.com/doc/iso-iec-ieee-29148-templates/)
3. Initialize an **RTM** in Git (Markdown/CSV) with columns: BG, SN, SR/NFR, Verification Method, Test Artefacts, Status.

### 11.2 Level 4: Behavioral specification via SbE/BDD

For each candidate feature:

1. Run a **Three Amigos workshop**:
   - Clarify goal and scope; link to BG/SR IDs.
   - Mine examples; use decision tables and state tables for rules; explicitly call out unwanted behaviour. [2367473.fs1.hubspotusercontent-na1](https://2367473.fs1.hubspotusercontent-na1.net/hubfs/2367473/EARS%20Configuration%20PDF.pdf)
2. Capture **Given/When/Then scenarios** in feature files:
   - One feature per coherent behavior domain.
   - Tag with requirement IDs for traceability.
3. Review scenarios as **inspection** artefacts:
   - Treat as design reviews for behavior; catch ambiguities before coding.

### 11.3 Level 5: Formal test and verification artefacts

In parallel:

1. **Test Strategy / Plan**
   - Define how unit/integration/acceptance/contract/E2E tests, exploratory charters, and NFR tests work together (pyramid/trophy stance). [martinfowler](https://martinfowler.com/articles/practical-test-pyramid.html)
2. **Test case specifications**
   - For non‑BDD scripted tests, maintain lean specs with IDs and trace links.
3. **Exploratory charters**
   - Plan charters for high‑risk areas; link charter IDs into the RTM as verification artefacts. [tmap](https://www.tmap.net/wp-content/uploads/sites/17/2025/08/Exploratory-Testing-Charter-Explanation-v1.2_0.pdf)
4. **NFR verification plans**
   - For each NFR, define fit criteria and concrete tests (load scripts, security scans, accessibility checks).

### 11.4 Automation and living documentation

1. Implement an **automation layer** under scenarios:
   - Focus on API/service‑level BDD tests where possible; limit UI BDD to essential flows.
   - Use Pact (or equivalent) for contract tests between services. [docs.pact](https://docs.pact.io)
2. Integrate all automated tests into **CI/CD**:
   - Unit, integration, BDD, contract, perf smoke tests, security scans.
   - Use thresholds for perf SLOs. [grafana](https://grafana.com/docs/k6/latest/using-k6/thresholds/)
3. Set up **living documentation publishing**:
   - Cucumber/SpecFlow reports published to a browsable portal.
   - Concordion/FitNesse where more narrative documentation is needed. [fitnesse](https://fitnesse.org/FitNesse/UserGuide.html)
4. Periodically assess **test effectiveness**:
   - Use mutation testing to find weak spots, especially in critical modules. [arxiv](https://arxiv.org/abs/2103.07189)
   - Consider property‑based tests for complex logic. [seas.upenn](https://www.seas.upenn.edu/~cis5520/current/lectures/soln/05-quickcheck/QuickCheck.html)

### 11.5 Governance and evolution

1. **Review cadence**:
   - Regularly review RTM and living docs to prune obsolete requirements and specs.
2. **Metrics**:
   - Track requirement‑related defects, test coverage per requirement, and review defect‑catch rates; empirical work suggests reviews can remove ~60% of defects before testing. [sites.pitt](https://sites.pitt.edu/~ckemerer/PSP_Data.pdf)
3. **Change impact analysis**:
   - Use bi‑directional traceability to see which specs/tests/NFRs are impacted by requirement changes; SLRs show this is one of the strongest benefits of traceability in practice. [webomates](https://www.webomates.com/blog/software-requirement-metrics/9-reasons-why-requirements-traceability-is-important-in-agile/)

***

This overall approach gives you:

- Level‑4 artefacts: **concrete, executable behavioral specs** (SbE/BDD scenarios, tables, states) tightly linked to goals.
- Level‑5 artefacts: **test plans, test cases, charters, NFR test specs, and RTMs** that collectively demonstrate coverage and provide the backbone for compliance, change management, and continuous improvement.

---

## Additional Research & Evidence

*Supplementary research and evidence from a second research pass.*

# Creating behavioural specifications and test verification artefacts for greenfield software projects

## How Level four and Level five fit together in modern practice

In greenfield software delivery, "behavioural specification" (examples, scenarios, acceptance criteria) and "test verification artefacts" (test plans, scripted test cases, traceability, and evidence) are best treated as one connected system because the same artefact can serve multiple roles: it can clarify intent, define acceptance, drive automation, and become durable evidence when linked to requirements and results. This tight coupling is widely reported in agile requirements practice, where detailed requirements are often documented as (and even managed through) test cases, with variants that include behaviour-driven approaches and machine-executable specifications. turn4view0

Two implications follow for Level four–five work on a greenfield project. First, you get the biggest quality and rework benefits when examples are created collaboratively as *the* agreement about behaviour, not as an after-the-fact QA activity. turn5view0 Second, you need just enough formality to achieve coverage, traceability, and auditability for your context; the distinction between Level four and Level five becomes less about separate documents and more about completeness, lifecycle integration, and evidentiary strength. turn10search13turn14search0

## Specification by Example as an evidence-based workflow

Specification by Example (SbE) is a collaborative way of defining requirements and functional tests using realistic examples as the primary tool for shared understanding, with the explicit goal that the examples can be validated frequently (often automatically) and evolve into "living documentation". turn23search1 The modern "workflow" most associated with SbE is documented as a set of process patterns: deriving scope from goals, specifying collaboratively, illustrating with examples, refining the specification, automating validation based on examples, validating frequently, and evolving a documentation system. turn23search9

A core practical reading of that workflow for greenfield projects is:

- **Derive scope from goals**: avoid feature lists detached from outcome; connect behaviour to a measurable goal before investing in detail. turn23search18  
- **Specify collaboratively (all roles)**: use structured conversations to surface business rules, assumptions, and edge cases before code. turn5view0  
- **Illustrate with examples → refine**: move from abstract "shall" statements to representative examples, then expand coverage via tables, variants, states, and exceptions. turn7search0  
- **Automate without changing the meaning**: keep examples business-readable; add a thin automation layer rather than rewriting the specification into code. turn7search20  
- **Validate frequently**: frequent execution is what turns documentation into evidence and exposes drift quickly. turn7search1  
- **Evolve living documentation**: publish the same artefacts (and their latest run results) as the current system contract. turn7search17  

### Evidence from 's 2020 practitioner survey

A frequently-cited empirical signal for SbE comes from 's "Specification by Example, 10 years later" survey (published 17 March 2020). He reports **514 responses**, and (importantly) notes the sampling is biased towards people already interested in the technique, so the results indicate correlations within that community rather than population-wide prevalence or causation. turn6search0

Within that sample, respondents who reported **using examples as acceptance criteria** also reported a higher share of "great" product quality ("users almost never experience problems in production"): **22%** vs **8%** for respondents not using examples as acceptance criteria (with "poor" quality 7% vs 14%). turn6search0 He further reports that among those who use examples as acceptance criteria, those who **automate tests based on those examples** reported "great" quality at **26%**, versus **13%** for those who do not automate, and "poor" quality at **5%** vs **11%** respectively—again explicitly framed as correlation rather than proof of causation. 

### Success factors and common failure modes

A consistent success factor in both SbE and BDD practice is **collaborative ownership of acceptance criteria** rather than treating scenario writing as a specialist QA task. In 's 2020 survey, "collaborative: delivery team together with business representatives" is the most common model for defining acceptance criteria (47%).  In Requirements Engineering research more broadly, peer review and inspections repeatedly show large defect-capture potential;  and  summarise prior evidence in which peer reviews commonly remove a large share of defects (often cited around ~60% in practice, depending on context and execution). turn3search4

Common failure modes are also well documented:

- **Confusing SbE/BDD with "gherkin test automation"**: optimising for executable scripts while skipping the discovery conversations reduces the approach to brittle automation and misses the quality benefits of shared understanding. turn6search1  
- **Scenarios as documentation debt**: if scenarios are not treated as an owned product artefact (reviewed, refactored, versioned), they become costly to maintain and can "freeze" parts of the system because behaviour is hard to locate and change. turn15view1  
- **Tooling and versioning friction**: large-scale BDD studies describe "behaviour ownership" and "versioning of behaviours" as recurring challenges, especially when scaling across many teams and integrations. turn18search18  

## BDD as a specification practice: concepts, tools, and empirical findings

Behaviour-Driven Development (BDD) was introduced by  as a response to limitations he observed in test-driven development communication and framing, shifting emphasis toward behaviour described in a shared language and discovered via examples. turn5view0turn5view0

A widely-quoted prioritisation captures BDD's intent: "having conversations is more important than capturing conversations is more important than automating conversations", attributed to  and repeated in both practitioner writing and official BDD guidance. turn6search1 This is not a rhetorical point: it defines *where the quality comes from*—shared understanding and discovery—while automation is the mechanism that keeps the specification continuously checked and publishable. turn7search3

### Tool ecosystem that supports "executable" specifications

The executable-specification ecosystem typically splits into (a) a **business-readable scenario format** and (b) the **automation "glue" layer**.

On the scenario side, the most common DSL is **Gherkin**, maintained and documented by , which defines keywords like Feature/Scenario/Given/When/Then. turn7search4turn7search32

For .NET ecosystems, a notable recent change is that  reached end-of-life on **31 December 2024**, and the community-driven continuation is , which describes itself as compatible with the SpecFlow v4 beta with minor backward-compatible differences and provides migration guidance. turn8search1turn7search7

### Empirical findings on BDD outcomes and challenges

The strongest empirical signals for BDD in the literature are typically about **communication/collaboration and requirements clarity**, with mixed or context-dependent evidence for direct defect-rate reduction (partly because isolating causality is hard).

- A large-scale/industrial evaluation study on adapting BDD for large-scale systems reports observed benefits including improved understanding of business aspects of requirements, improved quality, guidance to system-level use cases, and reuse of artefacts; it also lists challenges such as behaviour ownership, tool adoption, project scale, and versioning. turn21search25  
- A case study investigating BDD impact in agile teams based on interviews reports many positive impacts (e.g., collaboration and reduction in ambiguities/rework) alongside negative impacts often framed as "not being able to properly use it" and difficulties (e.g., writing meaningful tests in some contexts). turn15view2  
- A survey of BDD practitioners focused on maintenance reports that BDD is used in industry and highlights both perceived benefits (e.g., communication, domain-language specifications, and "living documentation") and substantial maintenance challenges when scenarios scale. turn18search18  
- In a controlled experiment applying BDD as a verification approach for safety-related scenarios (combined with STPA), BDD showed improved outcomes for communication effectiveness compared to standard UAT, while productivity, test thoroughness, and fault detection did not show statistically significant differences in that student-based setting—useful as evidence of where benefits may concentrate.   

A related evidence stream highlights that BDD stories and artefacts can get out of sync: empirical work on parsing BDD stories for consistency assurance notes that other software artefacts can lose synchronisation with stories, leading to inconsistencies—an argument for tight traceability and automated checks rather than relying on prose coherence. 

## Writing acceptance criteria for clarity, testability, and edge-case coverage

Acceptance criteria are the conditions a story/feature must satisfy to be considered complete; practical guidance emphasises that they should be clear, concise, and testable, focused on outcomes rather than implementation details. turn4view0 The persistent problem is that teams under-specify exceptions, boundary conditions, and "unwanted behaviours"—exactly the areas that drive production incidents and rework.

Two research-grounded reminders are especially relevant when you design Level four artefacts:

-  argues (from use-case practice) that handling "extension conditions" (alternatives, exceptions) is often the majority of the effort—he cites a rule of thumb around **~80%** of the writing/analysis work being in extensions rather than the "main success scenario". turn2search0  
- The  EARS case study explicitly notes that omissions—particularly requirements to handle **unwanted behaviour**—are a major source of missing requirements and costly rework, motivating structured templates that force explicit handling of such cases. turn9search4  

### Comparative toolkit: when to use which form

A pragmatic greenfield approach is to pick the smallest format that makes ambiguity and edge cases impossible to ignore—then evolve formality only where risk demands it. turn14search4

**Given/When/Then scenarios (BDD/SbE).** Use when the behaviour is best explained as a flow with a small number of meaningful contexts and outcomes, and when you want a direct path to automation via Gherkin-style tools. turn0search4

**Volere fit criteria.** Use when the requirement is otherwise subjective ("intuitive", "fast", "secure") and needs an explicit measurable test condition. The Volere materials frame a fit criterion as the element that makes a requirement testable; if you can't find one, the requirement is ambiguous or poorly understood. turn9search9

**EARS structured requirements.** Use when you need consistent, auditable natural-language requirement statements with reduced ambiguity and better completeness, especially for systems where review rigor is high. EARS provides a small set of templates (e.g., ubiquitous, event-driven, state-driven, optional, unwanted behaviour) and reports qualitative/quantitative improvements in a certification-related case study. turn9search10

**Decision tables.** Use when behaviour is governed by combinations of conditions ("if A and B but not C…") and you need systematic coverage. Both testing standards and the ISTQB syllabus treat decision table testing as a core black-box technique for complex business rules. turn9search15

**State transition specifications.** Use when behaviour depends on state (status workflows, lifecycle transitions, permissions changing over time). State transition testing is also a core black-box technique in the ISTQB syllabus and ISO guidance. turn9search15

### Templates and concrete examples (Level four artefacts)

**Given/When/Then scenario template (single behaviour).** turn0search4

```gherkin
Feature: <capability / business outcome>

  Scenario: <single behaviour, from a user/business viewpoint>
    Given <context / starting state>
    And <additional context>
    When <triggering action/event>
    Then <observable outcome>
    And <additional outcomes or business rules>
    But <what must not happen>
```

**Volere-style fit criterion template.** turn9search9

```text
Requirement: <statement of need/outcome>
Fit criterion: <measurable condition and threshold>
Measurement method: <how measured, by whom, where, when>
```

**EARS templates (including unwanted behaviour).** turn2search5

```text
Ubiquitous:        The <system> shall <response>.
Event-driven:      When <trigger>, the <system> shall <response>.
State-driven:      While <state>, the <system> shall <response>.
Optional-feature:  Where <feature is included>, the <system> shall <response>.
Unwanted:          If <unwanted condition>, then the <system> shall <response>.
```

**Decision table example (account lockout policy).** Decision tables are explicitly recommended for systematically covering combinations of conditions. turn9search15

| Conditions / Rules | R1 | R2 | R3 | R4 |
|---|---:|---:|---:|---:|
| Failed attempts in last 15 min ≥ 5 | N | Y | Y | Y |
| User has MFA enabled | N | N | Y | Y |
| Account already locked | N | N | N | Y |
| **Action: allow login attempt** | Y | Y | Y | N |
| **Action: require MFA challenge** | N | Y | N | N |
| **Action: lock account** | N | N | Y | N |
| **Action: show "account locked"** | N | N | N | Y |

**State transition specification template.** State-based behaviour is best captured by explicitly listing states, events, guards, and resulting transitions. turn9search8

```text
States: <S1>, <S2>, <S3> ...
Events: <E1>, <E2> ...
Transition table:
  From-State | Event | Guard/Condition | To-State | Outputs/Actions
```


## Formal test plans and test case specifications that balance rigour with agility

### What "formal" looks like in standards terms

's test documentation standard  (2008) defines a **test plan** as describing the *scope, approach, resources, and schedule* of intended test activities and explicitly includes identification of test items, features to be tested, tasks, responsibilities, and risks requiring contingency planning. turn10search26

The newer international baseline is the ISO/IEC/IEEE 29119 family, where ISO/IEC/IEEE 29119-3 defines templates for test documentation produced during test processes. turn9search2 The standard also clarifies that test cases include preconditions such as environment and existing data, which becomes crucial when your "specification" is also your executable test. 

### A recommended test plan structure for greenfield projects

A greenfield project rarely benefits from a heavyweight, static plan; it benefits from a **thin, living test plan** whose primary job is to explain coverage intent and decision-making. That aligns with both the 829 definition (scope/approach/resources/schedule/risks) and modern pipeline-centred planning where the plan is kept in the repository and maintained as delivery evolves. turn10search15

A practical structure (keep as a single Markdown page unless regulation demands more):

```text
Test Plan
- Purpose and quality goals (incl. release criteria)
- Scope and system context (what is in/out for this plan)
- Test strategy (levels, types, and rationale; automation approach)
- Environments and test data strategy
- Risk assessment and risk-based prioritisation
- Roles and responsibilities
- Schedule and cadence (incl. CI triggers and reporting cadence)
- Entry/exit criteria (per stage) and defect management
- Traceability approach (how requirements map to scenarios/cases/results)
- Deliverables and evidence retention (what is stored, for how long)
```

This structure matches the "scope/approach/resources/schedule/risk" emphasis in IEEE definitions and is compatible with ISO-style documentation outputs. turn10search13

### Test case specification: minimal fields that still support traceability and evidence

ISO/IEC/IEEE 29119-3 treats test cases as the lowest level test input and explicitly notes the importance of preconditions (environment, existing data, software/hardware under test). turn10search13 For a greenfield team that wants agility, the "minimum useful" test case specification tends to be:

```text
Test Case
- ID (stable, machine-friendly)
- Title (behaviour-focused)
- Linked requirement(s) and/or scenario(s)
- Preconditions (incl. data, environment, configuration)
- Steps / stimulus (or reference to automation)
- Expected result(s) (oracle)
- Postconditions / clean-up
- Priority / risk tag
- Automation status and location (if automated)
- Latest result + evidence link (CI run, report, logs)
```

This is consistent with standards-oriented expectations while remaining light enough to evolve with continuous delivery. turn10search13turn7search1

### Exploratory testing charters alongside scripted tests

Standards-aligned scripted artefacts do not eliminate the need for exploratory testing; they coexist.  describes exploratory testing as a style where test design and execution happen together, often guided by a **charter** that sets mission and tactics. turn10search0

A practical integration pattern is: keep scripted acceptance tests for stable, business-critical behaviours; run chartered exploratory sessions for new features, risky integrations, and "unknown unknowns", then promote findings into new scenarios, decision tables, or regression tests where appropriate. turn10search4

## Traceability and verification methods that prove requirements are met

### Requirements traceability in practice: what it is and why it's hard

Requirements traceability is commonly framed as the ability to describe and follow a requirement's life and relationships, including links to its origin and downstream artefacts. turn3search31turn3search14turn14search4

Empirical evidence shows both benefits and adoption barriers. A controlled experiment on maintenance tasks found that participants with traceability were **~21% faster** and produced **~60% more correct solutions** on average, suggesting downstream quality and efficiency benefits in maintenance/evolution contexts.  Conversely, practitioners report that **cost** is a major inhibitor, trace links are mainly created **manually**, and automation is scarce and not expected to replace human involvement—evidence that traceability must be designed as "just enough" and integrated into normal work. 

### A traceability matrix template for the full chain of evidence

A practical RTM for SbE/BDD projects should connect goals → needs → requirements → scenarios/cases → results and evidence. This aligns with systems engineering guidance that verification planning (including method selection) should be determined as requirements are developed. turn14search0

**Template (one row per system requirement or per scenario, depending on granularity):**

| Business Goal | Stakeholder Need | System Requirement ID | Verification Method (I/A/D/T) | BDD Scenario / Example ID | Test Case ID | Test Result (latest) | Evidence (run/report link) |
|---|---|---|---|---|---|---|---|
| BG-01 Reduce checkout abandonment by 10% | SN-07 Customers can pay quickly | SR-12 Payment completes < 5s p95 | Test + Analysis | AC-12.3 | TC-458 | Pass (2026-02-10) | CI#1842 + perf report |

The "I/A/D/T" method notation matches the four standard verification methods described in requirements engineering and systems verification guidance. turn14search1

### Tooling: heavyweight and lightweight options

For regulated or complex environments, full requirements management suites support first-class trace links. For example, IBM documentation shows linking requirements and artefacts across development and test domains in DOORS Next/Engineering Lifecycle Management. turn26search26 IBM's test management guidance also describes associating test cases to requirements repositories (a foundational RTM capability).  's Jama Connect help describes coverage and traceability in terms of requirements being "covered" by corresponding test cases and provides navigation from requirements to test artefacts. turn26search4

Lightweight approaches remain common (especially in greenfield software teams) when the goal is coverage and change impact rather than compliance; RTMs are often implemented in spreadsheets or Markdown, with requirement IDs mapped to scenario IDs and CI results. turn26search2 The key success factor is not the tool—it is keeping IDs stable, links easy to update, and the workflow cheap enough that people actually maintain it. turn12view0

### Choosing verification methods beyond testing

Requirements engineering standards and systems engineering practice typically recognise four standard verification methods: **inspection**, **analysis/simulation**, **demonstration**, and **test**. turn14search1 This matters because not every requirement is best verified by an automated test, and planning the method early reduces late surprises.

A practical selection framework (use as an attribute on each requirement):

| Requirement type | Best default verification method | Why | Typical evidence artefact |
|---|---|---|---|
| Text/content, UI copy, static configuration | Inspection | Human examination is the oracle | Review record, screenshot, checklist turn14search1 |
| Pure algorithmic constraints (e.g., "must compute X correctly for range Y") | Analysis + Test | Proof/analysis covers generality; tests sample key cases | Analysis note + automated unit/property tests turn13search3 |
| End-to-end business workflows | Demonstration + Test | Demonstration shows flow; automated acceptance tests guard regression | Demo sign-off + CI acceptance report turn7search3 |
| Safety/security requirements | Analysis + Test (often mandatory) | Threat/risk analysis plus executable checks | Threat model + security test evidence turn14search20 |
| Performance/SLO requirements | Test (load) + Analysis (metrics) | Needs measurement under representative load | Load test report + SLO dashboard extract turn25search3 |

This matches the guidance that verification method selection should be determined as requirements are developed and recorded alongside them. turn14search8

## Living documentation, test strategy integration, and verifying non-functional requirements

### Keeping artefacts "alive" as living documentation

Living documentation is the idea that specifications remain accurate because they are continuously validated against the running system, typically by executing the same scenarios that stakeholders read. turn4view0 The practical mechanism is simple: when documentation is generated from test runs (especially in CI), the displayed specification reflects what the system currently passes, making drift visible quickly. turn7search3

Evidence that this approach produces maintainable documentation is mixed: practitioners report the benefit ("living documentation that evolves with the system over time"), but empirical work also highlights that scenario suites can become costly and parts of systems can become "frozen" if examples are hard to evolve. turn18search18 's survey further adds a meaningful correlation: teams that automate example-based acceptance criteria self-report better product quality than those who do not, suggesting that continuous validation and executable documentation are associated with better outcomes in practice. 

**Maintenance practices that consistently reduce living-doc costs** (evidence-backed themes):

- Treat scenarios as first-class code: refactor, review, and version them; BDD maintenance research explicitly frames maintenance as a central challenge/opportunity. turn15view1  
- Keep a thin automation layer: frameworks describe feature files as the spec with separate step definitions as glue. This separation is what keeps business text stable while implementation details evolve. turn7search20  
- Organise feature files for navigation: tool guidance and practitioner surveys focus on structuring living documentation so people can find behaviours and understand coverage. turn7search3  

### Relationship between unit, integration, and acceptance tests

The "test pyramid" metaphor is commonly used to argue that a test suite should contain many small/fast tests at the base and fewer slow end-to-end UI tests at the top; 's pyramid is summarised as Unit → Service → UI tests. turn13search16

For Level four–five artefacts, the practical integration is:

- **Level four acceptance scenarios** are *contract tests for behaviour* (business-facing), often running at service/API level rather than via brittle UI paths. turn4view0  
- **Unit and component tests** are primarily developer-facing, verifying internal correctness and enabling rapid feedback; they complement acceptance tests rather than replacing them. turn13search16  
- **Contract tests** (e.g., consumer-driven contracts) sit between unit and end-to-end tests for distributed systems; Pact documentation describes generating a contract from consumer tests to verify provider compatibility for the behaviours consumers actually use. turn13search6  
- **Mutation testing** evaluates test-suite effectiveness by seeding faults and checking whether tests "kill" them; PIT's documentation describes this mechanism and how mutation score gauges test quality. turn13search7  

### Verifying non-functional requirements with measurable targets

The essential principle for NFRs is the same as for functional requirements: write them so that a specific verification method and measurable pass/fail criteria exist. turn14search8

**Performance and reliability (SLO-based).** 's SRE guidance argues that insisting on 100% SLO compliance is unrealistic and can harm innovation, motivating explicit **error budgets** derived from SLOs. turn25search4

Concrete NFR verification example:

```text
NFR-PERF-01 (Latency SLO)
Target: p95 API latency < 300ms over 28-day window for "checkout.submit"
Verification: Load test + metrics analysis
Evidence: k6 run thresholds + dashboard snapshot + CI artefact link
```

This aligns with SRE's emphasis on measurable SLOs and operational tracking as evidence. turn25search12

**Security.** OWASP's Application Security Verification Standard (ASVS) is explicitly positioned as a basis for testing application security controls and establishing confidence in the security posture of web applications. turn25search21 For greenfield planning, this means: translate relevant ASVS controls into verifiable requirements (or acceptance criteria), decide verification methods (static review, analysis/threat modelling, automated scanning, penetration tests), and connect them into the RTM so "security" is not a separate, untraceable activity. turn14search0

**Accessibility.** WCAG 2.2 is explicitly structured with testable success criteria and defines three conformance levels (A, AA, AAA), supporting use in design specification, purchasing, regulation, and contractual agreements. turn25search6 For a greenfield product, the key is to treat the target conformance level (commonly AA) as a set of verifiable requirements, with evidence consisting of audits (inspection), automated checks where applicable, and manual testing for criteria that require human judgement. turn25search6

### A practical, end-to-end operating model for greenfield teams

An evidence-based operating model that integrates the above, without producing document bloat, is:

1. Start from goal-linked scope (avoid orphan requirements). turn23search31  
2. Run collaborative example/spec workshops; treat scenarios as the acceptance contract. turn4view0  
3. Choose the right acceptance-criteria form (scenario, decision table, state model, fit criterion, EARS) based on complexity and risk, with explicit unwanted-behaviour handling. turn9search25turn2search5  
4. Automate with a thin glue layer; preserve reading quality; run continuously; publish reports as living documentation. turn7search3  
5. Maintain a lightweight RTM linking goal → requirement → scenario/case → result/evidence; scale tooling only when cost/benefit or compliance requires it. turn11view0turn26search3  
6. Assign verification methods (inspection/analysis/demonstration/test) per requirement at write-time; keep proof artefacts attached. turn14search4
