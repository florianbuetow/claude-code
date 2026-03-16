# Collaboration Antipatterns — Common Developer-AI Pitfalls

> "The patterns that waste the most time are the ones neither side notices."

## Core Idea

Developer-AI collaboration has recurring failure modes that transcend individual tasks.
These antipatterns emerge from the interaction dynamics between human and AI — neither
side is "wrong," but the combination produces suboptimal results. Recognizing these
patterns in session logs allows structural fixes (skills, hooks, settings, process
changes) rather than trying to "be better" each time.

These antipatterns are drawn from common patterns observed across many developer-AI
workflows and publicly documented by teams using AI coding tools at scale.

## Detection Heuristics

What to look for in session logs to identify collaboration antipatterns:

### Communication Patterns
- **Vague requests followed by corrections**: Short user messages → long correction
  sequences
- **Over-specified requests**: User writes a paragraph when a sentence would do
- **Missing constraints**: No mention of what NOT to do, leading to scope creep
- **Assumed context**: User assumes Claude remembers previous sessions

### Execution Patterns
- **Premature implementation**: Claude starts coding before reading enough context
- **One-shot attempts**: Complex tasks attempted in a single response
- **Gold plating**: Claude adds features, docs, or improvements not requested
- **Copy-paste development**: Claude generates similar code repeatedly instead of
  creating abstractions

### Emotional Dynamics
- **Frustration escalation**: User messages become shorter, blunter, or more emphatic
  across a turn sequence — a sign that correction attempts aren't converging
- **Silent abandonment**: User drops a task without completing it and moves on — the
  highest-cost failure because it's invisible to correction-count metrics
- **Resignation acceptance**: User accepts a suboptimal result ("fine", "close enough")
  rather than continuing to correct — signals exhaustion, not satisfaction
- **Enthusiasm decay**: User starts a session engaged and detailed but becomes terse
  later — a specific interaction broke the momentum

### Session Management
- **Marathon sessions**: Sessions running 50+ turns where quality degrades
- **Micro-sessions**: Many 1-2 turn sessions with repeated context loading
- **No checkpointing**: Long work without git commits, risking loss
- **Context overload**: Reading too many files into context, degrading performance

### Cognitive Biases in Developer-AI Collaboration
These biases affect both the developer and the AI, and compound when neither side
notices them:
- **Anchoring**: The first approach attempted locks in the direction. If Claude starts
  with approach A, both parties tend to iterate on approach A rather than reconsidering
  whether approach B would be better — even after multiple corrections
- **Sunk cost**: The more turns invested in an approach, the harder it is to abandon it.
  Long correction spirals persist because "we've already put 8 turns into this"
- **Automation bias**: The developer accepts Claude's output because it came from an AI
  tool, with less scrutiny than they'd apply to a human colleague's code
- **Status quo bias**: Both parties gravitate toward existing solutions and familiar
  tools even when the task calls for something different

## Antipattern Catalog

### 1. The Vague Prompt Trap
**Pattern**: Developer gives a vague request → Claude guesses wrong → developer
corrects → Claude guesses differently → repeat until frustrated or correct.

**Evidence in logs**: Short user messages (< 20 words) for non-trivial tasks, followed
by 3+ correction messages. User messages containing "no", "that's not what I meant."

**Root cause**: Under-specification. The developer knows what they want but doesn't
communicate the constraints that disambiguate between interpretations.

**Structural fix**:
- CLAUDE.md instruction: "For non-trivial tasks, confirm your understanding before
  implementing"
- Skill that includes a "clarifying questions" step before execution
- Template prompts for common task types

### 2. The Kitchen Sink Session
**Pattern**: Developer keeps adding tasks to a single session until context overflows,
quality degrades, and Claude starts "forgetting" earlier instructions.

**Evidence in logs**: Session with 30+ turns, later messages showing Claude repeating
mistakes it handled correctly earlier. User saying "I already told you" or "we
discussed this."

**Root cause**: Context window pressure. As the session grows, earlier context gets
compressed or lost. Combined with the sunk-cost fallacy of not wanting to start a
new session.

**Structural fix**:
- After completing a logical unit of work, commit and consider a fresh session
- Use session-bridging artifacts (progress files) for multi-session work
- CLAUDE.md instruction: "After N turns, suggest checkpointing and fresh start"

### 3. The Premature Implementation
**Pattern**: Claude dives into coding immediately without reading enough context,
producing code that doesn't fit the existing architecture.

**Evidence in logs**: Write/Edit tool calls happening before Read/Grep/Glob calls.
User corrections about architecture, patterns, or conventions that Claude should have
discovered by reading existing code first.

**Root cause**: AI's bias toward action. Also, user not specifying that understanding
should precede implementation.

**Structural fix**:
- CLAUDE.md instruction: "Always read related existing code before writing new code"
- Planning skill that separates research/design from implementation
- Hook that warns when edits happen without prior reads in the same file area

### 4. The Gold Plating Problem
**Pattern**: Claude adds comments, docstrings, type annotations, error handling, or
refactoring to code the user didn't ask about. User has to say "revert that" or
"I only asked for X."

**Evidence in logs**: Edit tool calls to files/functions not mentioned in user request.
User messages containing "only", "just", "don't change", "revert."

**Root cause**: AI's training to be "helpful" includes proactive improvements. Without
explicit scope constraints, it defaults to maximum helpfulness.

**Structural fix**:
- CLAUDE.md instruction: "Only modify what is explicitly requested. Do not add
  docstrings, comments, or refactoring unless asked"
- Strict scope in task prompts: "Change ONLY function X in file Y"

### 5. The Approval Fatigue Trap
**Pattern**: Claude asks permission for so many operations that the developer starts
approving everything blindly, defeating the purpose of the permission system.

**Evidence in logs**: Rapid succession of tool approvals (< 2 seconds between approvals)
with no user messages between them. Or user switches to a more permissive mode
mid-session.

**Root cause**: Permission configuration too granular for the developer's actual
risk tolerance.

**Structural fix**:
- Tune settings to auto-allow genuinely safe operations
- Use hooks for the few truly dangerous operations instead of blanket ask-for-everything
- CLAUDE.md with explicit safe/unsafe operation lists

### 6. The Retry Without Understanding
**Pattern**: Claude's approach fails → instead of analyzing why, Claude retries the
same approach slightly differently → fails again → cycle repeats.

**Evidence in logs**: Same tool called 3+ times with similar inputs, each returning
errors. No Read/Grep calls between retries to understand the error.

**Root cause**: Agent's tendency to iterate rather than step back and reason about
the failure.

**Structural fix**:
- CLAUDE.md instruction: "If an approach fails twice, stop and analyze the root cause
  before retrying"
- User intervention pattern: interrupt retry loops early with "stop, let's think
  about why this isn't working"

### 7. The Context-Free Restart
**Pattern**: New session starts with no context from the previous session. Developer
has to re-explain everything or Claude re-discovers the project from scratch.

**Evidence in logs**: First messages of new sessions contain lengthy context dumps.
Or Claude's first actions are reading files it read in the previous session.

**Root cause**: No session-bridging artifacts. No CLAUDE.md with accumulated context.
No memory files.

**Structural fix**:
- Maintain CLAUDE.md with project conventions and current state
- Use memory files for session-to-session context
- Session-bridging artifacts (progress files, feature checklists)
- End-of-session habit: update CLAUDE.md with learnings

### 8. The Wrong Division of Labor
**Pattern**: Developer does work the AI should handle (manual file searching, writing
boilerplate) or AI does work the developer should own (architectural decisions, naming
choices, priority calls).

**Evidence in logs**: Developer pasting file contents instead of letting Claude read
them. Or Claude making subjective decisions (naming, architecture) without asking.

**Root cause**: Unclear roles. Neither side knows what the other is best at.

**Structural fix**:
- Explicit role definition in CLAUDE.md: "You handle X, ask me about Y"
- Skills that enforce the right division (AI explores, presents options, human decides)

### 9. The Emotional Escalation
**Pattern**: Interaction starts collaborative, but after 2-3 failed corrections the
developer's tone shifts — messages become shorter, blunter, more emphatic. The AI
doesn't notice the shift and continues its normal approach, widening the gap.

**Evidence in logs**: Message length decreasing across a turn sequence. Tone markers:
ALL CAPS appearing, exclamation marks increasing, "just" and "only" appearing more
frequently ("just do X", "I only want Y"). Followed by either resignation ("fine") or
abandonment (topic switch without completion).

**Root cause**: The AI lacks awareness of conversational dynamics. It treats the 10th
correction the same as the 1st. The developer escalates because repeated corrections
aren't producing convergence — which usually means the root problem is misunderstood,
not that the execution needs tweaking.

**Structural fix**:
- CLAUDE.md instruction: "If the user has corrected you twice on the same task, stop
  and restate your understanding of the goal before trying again"
- This is also a signal to check whether the underlying approach (not just the current
  edit) is wrong — often the fix is to start over with a different strategy rather than
  continuing to patch the current one

### 10. The Anchored Approach
**Pattern**: Claude's first attempt at a task establishes an approach. All subsequent
attempts iterate on that same approach even when corrections suggest a fundamentally
different direction is needed. Neither party steps back to reconsider.

**Evidence in logs**: Multiple correction cycles where each Claude response modifies
the same code/approach rather than proposing an alternative. User corrections that
imply a different approach ("no, I mean something completely different", "start over")
appearing late in the sequence after many incremental fixes.

**Root cause**: Anchoring bias. The first solution framing becomes the default. The AI
iterates within that frame because most corrections are incremental ("change X to Y")
rather than strategic ("try a completely different approach"). The developer contributes
by providing incremental corrections when they should say "stop, let's rethink."

**Structural fix**:
- After 3 corrections on the same task, explicitly consider whether the approach itself
  is wrong — not just the details
- CLAUDE.md instruction: "If a task requires more than 3 corrections, pause and ask
  whether a different approach would be better"
- Developer habit: learn to say "wrong direction" early rather than attempting to steer
  incrementally

## How to Present Antipattern Findings

For each antipattern detected, provide paragraph-level evidence with severity
assessment — not a metric bullet list.

**Expected depth per finding:**

### Over-Asking / Unnecessary Confirmation
- **Sessions:** `9fdb4b4c`, `870ef05c`, `ba6c3984`, `80afdd3b`
- **Frequency:** 4+ sessions | **Cost:** ~30+ turns | **Fix effort:** LOW
- **Evidence:** Session `9fdb4b4c` (2026-03-02, 912 lines) had 16 `AskUserQuestion` tool calls — far more than any other session. The user explicitly corrected this at turn 219: "please don't ask me what to update. Please read the readme and determine yourself what needs to be updated." In session `870ef05c` (2026-02-15, 360 lines), the assistant asked "Want me to delete the feature branch?" then 4 turns later re-asked the same question. The user responded: "i am waiting." In session `ba6c3984`, the assistant asked "Want me to remove them?" after the user had already said "if so fucking revert that" — a redundant confirmation that amplified frustration. Across the full dataset: 111 occurrences of "shall I" / "should I" / "want me to" / "would you like" across 40 session files.
- **Root cause:** The assistant defaults to asking rather than inspecting and acting. The user's interaction style is to give high-level direction and expect autonomous execution. When the user says "update the README", they expect Claude to read it, determine what's stale, fix it, and report — not ask "what specifically should I update?"
- **Structural fix:** CLAUDE.md addition: "For general directives ('update the README', 'fix the tests'), inspect the current state, determine what needs changing, execute, and report what you did. Do not ask 'what specifically?' — figure it out. Only ask clarifying questions when there are genuinely ambiguous choices with different tradeoffs."
- **Severity:** HIGH frequency (4+ sessions), HIGH cost (~30+ turns), LOW fix effort (one CLAUDE.md directive).

**What to include in each finding:**
- Session IDs with dates — traceable to the inventory
- Quoted messages showing the antipattern in action
- Turn cost per occurrence and total across sessions
- Root cause — why this antipattern emerges
- Structural fix with effort level — concrete, not generic advice
- Severity triple: frequency, cost, fixability

**Prioritization:** Order antipatterns by composite score:
high-frequency + high-cost + low-fix-effort items first.

## False Positives to Avoid

- Exploratory sessions (brainstorming, design discussions) will look like "vague
  prompts" and "no clear outcome" — this is fine, exploration is valuable
- Some gold plating is welcome — developers sometimes appreciate proactive improvements.
  Only flag it if the developer explicitly rejected the additions
- Long sessions aren't automatically bad if the work progressed steadily with few
  corrections
- Context re-loading is sometimes necessary (codebase changed, different part of
  the project) — only flag it when the same context is loaded repeatedly
