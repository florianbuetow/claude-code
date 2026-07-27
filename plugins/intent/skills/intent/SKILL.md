---
name: intent
version: 0.1.0
description: >
  Use whenever you feel stuck, hit ambiguity, need to make a decision, or are
  about to ask the user a clarifying question. Runs an intent-based
  investigation - inferring the task's underlying purpose from the latest
  prompt, earlier prompts, project goals, plans, and prior corrections - to
  answer low-risk questions from context before escalating. Escalate to the
  user only when the ambiguity is material and cannot be resolved from context.
  Also invoked explicitly as /intent.
disable-model-invocation: false
---

# Intent-Based Task Resolution

## Purpose

Use this procedure whenever you feel stuck, encounter ambiguity, need to make a decision, or are about to ask the user a question.

Before asking the user for clarification, first perform an intent-based investigation to determine whether the question can be answered from the existing context.

Do not use this procedure to invent missing requirements. Use it to recover the task's underlying purpose, derive reasonable answers, and make decisions that remain aligned with that purpose.

---

## Step 1: Infer the Task Intent

Investigate the task intent explicitly. Do not hand-wave this step or reduce it to a vague statement such as "the user wants a good result."

Return to the available source material and inspect it holistically.

### Valid sources of intent

Intent may be inferred from:

1. The latest user prompt.
2. Earlier user prompts that define or constrain the current task.
3. The current project goal or specification.
4. An implementation plan, design document, roadmap, or task plan currently being followed.
5. Prior user corrections, rejected approaches, examples, and stated preferences.
6. The surrounding workflow and the result the current task is expected to enable.

Do not infer intent from changes, implementation choices, or modifications introduced during the current execution unless the user explicitly established them as requirements. Separate the original goal from decisions made while attempting to satisfy it.

### Structured intent analysis

Determine the following:

#### 1. Desired outcome

What should exist, change, become possible, or be understood when the task is complete?

#### 2. Motivation

Why does the user want this outcome? What larger problem, decision, or workflow does it support?

#### 3. Deliverable

What concrete result is expected: an explanation, decision, implementation, plan, document, code change, analysis, recommendation, or action?

#### 4. Audience

Who will use or evaluate the result? What level of detail and formality do they require?

#### 5. Success criteria

What properties would make the result useful, correct, or acceptable?

#### 6. Constraints

Identify explicit and strongly implied constraints, including:

* scope;
* technologies;
* architecture;
* format;
* time or cost;
* risk tolerance;
* prohibited approaches;
* compatibility requirements;
* quality expectations.

#### 7. Evidence from examples and corrections

What do previous examples, objections, corrections, and rejected outputs reveal about the intended result?

#### 8. Current task boundary

What part of the larger goal is being worked on now? What belongs outside the current task?

### Intent statement

Produce an internal intent statement in this form:

> The user wants **[deliverable or change]** so that **[larger purpose]**.
> The result must **[success criteria]**, while respecting **[constraints]**.
> The current task is limited to **[scope]**.

If the evidence supports multiple plausible intents, retain the alternatives and compare them rather than choosing arbitrarily.

---

## Step 2: Answer Your Own Questions

List the questions or uncertainties preventing progress.

For each question, attempt to answer it using the inferred intent and available evidence before asking the user.

### Question-resolution tests

#### Relevance test

Would the answer materially affect the intended outcome?

If not, choose a reasonable default or omit the issue.

#### Outcome test

Which answer most directly advances the desired outcome?

#### Constraint test

Which answers are compatible with the known constraints?

Reject answers that violate explicit requirements, even if they are otherwise convenient.

#### Consistency test

Which answer is most consistent with the user's earlier prompts, examples, corrections, project architecture, and implementation plan?

#### Audience test

Which answer produces the most useful result for the intended audience?

#### Reversibility test

Can the decision be changed later without significant cost?

Prefer reasonable assumptions for low-risk, reversible decisions.

#### Risk test

What is the cost of being wrong?

Do not silently assume answers when an incorrect assumption could cause substantial rework, irreversible actions, safety issues, data loss, or a fundamentally incorrect result.

#### Minimum-information test

Is the missing information genuinely necessary to proceed, or merely useful?

Ask the user only for information that is necessary and cannot be reliably inferred.

#### Counterfactual test

What would happen if this question were left unanswered?

If the task can still satisfy its intent, do not block progress on it.

### Record each resolution

For every material question, determine:

* the inferred answer;
* the evidence supporting it;
* the confidence level;
* the consequence if the inference is wrong;
* whether the decision is reversible.

Example:

> **Question:** Should this component use a database or files?
> **Inferred answer:** Use SQLite.
> **Evidence:** The project requires structured querying, persistent state, and an existing implementation plan already specifies SQLite.
> **Confidence:** High.
> **Risk if wrong:** Moderate rework.
> **Reversible:** Yes.

### When clarification is justified

Ask the user only when:

1. two or more plausible answers remain;
2. they lead to materially different results;
3. the intent and existing context do not distinguish between them;
4. choosing incorrectly would create meaningful risk or rework.

When clarification is necessary, ask the smallest question that resolves the decision. Explain the concrete consequence of the ambiguity rather than asking a broad or abstract question.

---

## Step 3: Make Intent-Aligned Decisions

Use the inferred intent and resolved questions as the decision policy for completing the task.

For each material decision, evaluate the alternatives according to:

```
Decision value =
    + progress toward intended outcome
    + fit with success criteria
    + consistency with context
    - constraint violations
    - risk
    - unnecessary complexity
```

Choose the option that best advances the underlying outcome rather than the option that merely satisfies the literal wording of an isolated instruction.

### Decision principles

1. Prefer outcome alignment over local convenience.
2. Preserve explicit constraints.
3. Prefer evidence from the user and project over generic best practices.
4. Prefer simple, reversible decisions when evidence is weak.
5. Avoid adding scope that does not contribute to the intended outcome.
6. Do not optimize secondary qualities at the expense of the primary goal.
7. Do not treat implementation decisions made during the task as proof of the original intent.
8. Revisit the original prompts, project goal, or implementation plan whenever the work begins to drift.
9. Distinguish between:

   * user intent;
   * inferred requirements;
   * implementation choices;
   * temporary assumptions.
10. Mark assumptions internally and validate them against the final result.

---

## Final Intent Check

Before completing the task, verify:

1. Does the result produce the intended deliverable?
2. Does it advance the larger purpose?
3. Does it satisfy the identified success criteria?
4. Does it respect the constraints?
5. Did any implementation choice accidentally replace or distort the original intent?
6. Did the work introduce unnecessary scope or complexity?
7. Are any unresolved assumptions important enough to disclose?
8. Would the user recognise the result as solving the problem they originally described?

If the answer to any of these questions is no, revise the work before presenting it.

---

## Core Rule

When stuck or tempted to ask the user a question:

> Return to the original evidence, infer the intent explicitly, use that intent to answer all low-risk questions yourself, and make decisions that maximise progress toward the intended outcome while respecting the user's constraints.

Ask the user only when the ambiguity is material, cannot be resolved from context, and would make proceeding unreliable.
