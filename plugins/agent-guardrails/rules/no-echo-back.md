---
name: no-echo-back
pattern: (?i)(I'll (now |first |start by |proceed to |begin by )|Here's (what I'll|my plan|the plan)|Let me (start|begin) by |First,? I'll |I'm going to (start|begin) by |Let me (now )?go ahead and |I'll go ahead and |Let me walk (you )?through)
message: "The user said go. Execute — don't restate the plan."
---

**Stop - you're echoing back the plan instead of executing.**

You restated what you're about to do (e.g., "I'll now proceed to...", "Here's what I'll do", "Let me start by...") instead of just doing it. When the user triggers execution ("yes", "do it", "go"), the context is loaded — the message is just the trigger:
1. **Execute immediately** — don't restate or summarize the plan.
2. **Use tools directly** — call Read, Edit, Bash, Write without narrating your intent first.
3. **Report results, not intentions** — say what happened, not what you're about to do.
