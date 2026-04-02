# Claude Code Source Leak Findings

Seven structural bottlenecks discovered in the Claude Code source code leak (March 31, 2026).
Original analysis by [@fakeguru](https://x.com/iamfakeguru) based on reverse-engineering
the leaked source against real agent logs.

Source: [x.com/iamfakeguru/status/2038965567269249484](https://x.com/iamfakeguru/status/2038965567269249484)

---

## Finding 1: Employee-Only Verification Gate

**Source location:** `services/tools/toolExecution.ts`

**The problem:** The agent's success metric for a file write is: did the write operation
complete? Not "does the code compile." Not "did I introduce type errors." Just: did bytes
hit disk?

The source contains explicit instructions telling the agent to verify its work before
reporting success -- checking that tests pass, running the script, confirming output.
Those instructions are gated behind `process.env.USER_TYPE === 'ant'`.

Anthropic employees get post-edit verification. External users don't. Internal comments
document a **29-30% false-claims rate** on the current model.

**What to check in CLAUDE.md:**
- Does it mandate running the project's type-checker/compiler after edits?
- Does it mandate running linters after edits?
- Does it mandate running the test suite before claiming success?
- Does it forbid reporting "Done!" without verification?
- Does it require stating explicitly when no verification tools are configured?

**The override:** Force a verification loop: after every file modification, run the
project's type-checker, linter, and test suite before reporting success.

---

## Finding 2: Context Death Spiral

**Source location:** `services/compact/autoCompact.ts`

**The problem:** Auto-compaction fires when context pressure crosses ~167,000 tokens. It
keeps 5 files (capped at 5K tokens each), compresses everything else into a single
50,000-token summary, and throws away every file read, every reasoning chain, every
intermediate decision.

Dirty, sloppy codebases accelerate this. Dead imports, unused exports, orphaned props
eat tokens that contribute nothing to the task but everything to triggering compaction.

**What to check in CLAUDE.md:**
- Does it mandate dead code cleanup before structural refactors?
- Does it enforce phased execution (max 5 files per phase)?
- Does it require explicit phase approval before proceeding?
- Does it mention context compaction awareness?
- Does it suggest proactive `/compact` usage?

**The override:** Step 0 of any refactor must be deletion -- strip dead props, unused
exports, orphaned imports, debug logs. Commit cleanup separately. Keep each phase under
5 files.

---

## Finding 3: The Brevity Mandate

**Source location:** `constants/prompts.ts`

**The problem:** The system prompt contains directives that actively fight user intent:
- "Try the simplest approach first."
- "Don't refactor code beyond what was asked."
- "Three similar lines of code is better than a premature abstraction."

These are system-level instructions that define what "done" means. The user's prompt says
"fix the architecture" but the system prompt says "do the minimum work." System prompt
wins unless overridden.

**What to check in CLAUDE.md:**
- Does it explicitly override the "simplest approach" and "don't refactor" defaults?
- Does it reframe what constitutes acceptable quality?
- Does it reference a senior/staff engineer review standard?
- Does it encourage structural fixes when architecture is flawed?

**The override:** Override what "minimum" and "simple" mean by reframing quality
expectations: "What would a senior, experienced, perfectionist dev reject in code
review? Fix all of it."

---

## Finding 4: The Agent Swarm Nobody Told You About

**Source location:** `utils/agentContext.ts`

**The problem:** Each sub-agent runs in its own isolated AsyncLocalStorage -- own memory,
own compaction cycle, own token budget. There is no hardcoded MAX_WORKERS limit. Anthropic
built a multi-agent orchestration system with no ceiling and left users running one agent
like it's 2023.

One agent = ~167K tokens. Five parallel agents = 835K tokens of working memory. For any
task spanning >5 independent files, sequential processing voluntarily handicaps throughput.

**What to check in CLAUDE.md:**
- Does it mandate sub-agent deployment for large tasks (>5 files)?
- Does it specify batch sizes (5-8 files per agent)?
- Does it mention the execution models (fork, worktree, /batch)?
- Does it recommend `run_in_background` for long-running tasks?
- Does it warn against polling background agent output mid-run?

**The override:** Force sub-agent deployment. Batch files into groups of 5-8, launch in
parallel. Each gets its own context window.

---

## Finding 5: The 2,000-Line Blind Spot

**Source location:** `tools/FileReadTool/limits.ts`

**The problem:** Each file read is hard-capped at 2,000 lines / 25,000 tokens. Everything
past that is silently truncated. The agent doesn't know what it didn't see. It doesn't
warn. It hallucinates the rest and keeps going.

**What to check in CLAUDE.md:**
- Does it state the 2,000-line read cap?
- Does it mandate chunked reads with offset/limit for files >500 LOC?
- Does it warn against assuming a single read captured the full file?

**The override:** Any file over 500 LOC gets read in chunks using offset and limit
parameters. Never assume a single read captured the full file.

---

## Finding 6: Tool Result Blindness

**Source location:** `utils/toolResultStorage.ts`

**The problem:** Tool results exceeding 50,000 characters get persisted to disk and
replaced with a 2,000-byte preview. The agent works from the preview. It doesn't know
results were truncated. A codebase-wide grep returning "3 results" may actually have 47 --
only 3 fit in the preview window.

**What to check in CLAUDE.md:**
- Does it state the 50,000-char / 2,000-byte truncation thresholds?
- Does it mandate narrow scoping for searches?
- Does it require re-running when results look suspiciously small?
- Does it require stating when truncation is suspected?

**The override:** Scope narrowly. If results look suspiciously small, re-run directory by
directory. Assume truncation happened and say so.

---

## Finding 7: grep Is Not an AST

**Source location:** GrepTool implementation

**The problem:** Claude Code has no semantic code understanding. GrepTool is raw text
pattern matching. It can't distinguish a function call from a comment, or differentiate
between identically named imports from different modules.

A rename that greps for callers, updates 8 files, and misses 4 that use dynamic imports,
re-exports, or string references will compile in the files it touched and break everywhere
else.

**What to check in CLAUDE.md:**
- Does it acknowledge the lack of AST/semantic search?
- Does it mandate separate searches for each reference type?
  - Direct calls and references
  - Type-level references (interfaces, generics)
  - String literals containing the name
  - Dynamic imports and require() calls
  - Re-exports and barrel file entries
  - Test files and mocks
- Does it warn against assuming a single grep caught everything?

**The override:** On any rename or signature change, force separate searches for each
category. Assume grep missed something.
