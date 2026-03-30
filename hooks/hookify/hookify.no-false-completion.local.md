---
name: no-false-completion
enabled: true
event: stop
pattern: (?i)(all done|all set|we'?re all set|we'?re good|you'?re all set|that'?s everything|nothing else needs|no other changes|the fix is complete|implementation is complete|fully implemented|fully working|everything is working|everything works)
action: block
---

**Stop - unverified completion claim detected.**

You claimed the work is complete (e.g., "all done", "fully implemented", "everything works") without showing verification. Don't claim completion without evidence:
1. **Run the tests** or relevant verification commands.
2. **Show the output** proving it works.
3. Only claim completion after verification succeeds.
