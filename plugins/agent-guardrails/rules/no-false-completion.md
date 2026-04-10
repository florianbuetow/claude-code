---
name: no-false-completion
pattern: (?i)(all done|all set|we'?re all set|we'?re good|you'?re all set|that'?s everything|nothing else needs|no other changes|the fix is complete|implementation is complete|fully implemented|fully working|everything is working|everything works)
message: "That sounds great. However, did you verify your results. Run all available tests and show their output. Do a manual check of the changes. If this is a web project, use Playwright MCP or CLI to manually test the changes and features you implemented. Show the verification output, then restate your completion claim."
---

Did you verify your results.

1. Run all available tests and show their output.
2. Do a manual check of the changes.
3. If this is a web project, use Playwright MCP or CLI to manually test the changes and features you implemented.
4. Show the verification output, then restate your completion claim.
