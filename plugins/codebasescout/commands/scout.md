---
description: Scout a codebase and produce a ranked map from codebase to tasks, each tagged with a recommended model. Identifies work; does not fix it.
argument-hint: "[objective and/or path, e.g. \"tech debt in src/\"]"
---

Run the **codebasescout** pipeline on the target below.

Target / objective:
"""
$ARGUMENTS
"""

Launch the **scout-router** agent, which orchestrates the team: it guards the target, gates scan-vs-skip, sweeps and scores files by Impact x Opportunity with cheap models, ranks them, groups recurring classes, writes concrete tasks, and tags each task with a recommended model. The deliverable is `.codebasescout/run/tasks.md` -- a ranked map from codebase to tasks with model recommendations.

Hard rule: codebasescout **only identifies work and recommends a model per task. It must not fix, edit, refactor, or modify any code.** If the objective is unclear, infer the most likely one and state your assumption. When the map is ready, present it inline.
