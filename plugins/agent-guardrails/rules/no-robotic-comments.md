---
name: no-robotic-comments
pattern: (?i)(\/\/ (This (function|method|class|component|module|hook|handler|service|helper|utility) (handles|is responsible for|provides|manages|implements|creates|defines|sets up|configures|ensures|takes care of)|Import(s| the| necessary| required)|Initialize(s)? the|Handle(s)? the|Set(s)? up the|Check(s)? (if|whether) the|Ensure(s)? (that )?the|Validate(s)? the|Process(es)? the|Helper (function|method) (to|for|that)))
message: "Write human code. Remove robotic comment blocks that describe what is obvious from the code itself."
---

**Stop - robotic code comments detected.**

You wrote code comments that mechanically describe what the code does (e.g., "// This function handles...", "// Initialize the...", "// Ensure that the..."). These are AI tells — experienced developers don't write them:
1. **Delete obvious comments** — if the code is self-explanatory, the comment is noise.
2. **Comment the why, not the what** — explain non-obvious decisions, tricky business rules, or workarounds.
3. **Write code that reads like prose** — good naming eliminates the need for narration.
