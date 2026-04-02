---
name: agent-guardrails-test
description: Test agent guardrail hook patterns by running example phrases through the stop-guardrails.sh script and verifying each one is caught. Checks hook installation first. Use when user asks to "test guardrails", "verify guardrail hooks", "check guardrail patterns", "agent-guardrails test", or wants to confirm hooks are working correctly.
---

# Agent Guardrails Test

Run the stop-guardrails.sh hook against a comprehensive set of test phrases to verify all patterns fire correctly. Stops on first failure.

## Workflow

### Step 1: Check Hook Installation

Before running any tests, verify the hooks are installed in the current project:

```bash
# Check that the stop hook script exists and is executable
if [ ! -x .claude/hooks/stop-guardrails.sh ]; then
  echo "ABORT: stop-guardrails.sh not found or not executable in .claude/hooks/"
  echo "Run /agent-guardrails:install first to install the hooks."
  exit 1
fi

# Check that settings.local.json has the Stop hook configured
if ! cat .claude/settings.local.json 2>/dev/null | jq -e '.hooks.Stop' > /dev/null 2>&1; then
  echo "ABORT: No Stop hook configured in .claude/settings.local.json"
  echo "Run /agent-guardrails:install first to configure the hooks."
  exit 1
fi
```

If either check fails, report the failure and tell the user to run `/agent-guardrails:install` first. Do NOT proceed with tests.

### Step 2: Run Test Suite

Run each test phrase through the hook script. For each phrase, pipe it as JSON to the hook and check whether the response contains `"decision": "block"`.

The hook script path is `.claude/hooks/stop-guardrails.sh`.

**Stop on first failure.** When a phrase that should be blocked passes through, report it immediately and do not continue.

#### Test phrases by rule

Run these tests in order, grouped by rule. For each test phrase, run:

```bash
result=$(echo '{"last_assistant_message": "TEST_PHRASE"}' | bash .claude/hooks/stop-guardrails.sh)
if echo "$result" | grep -q '"decision"'; then
  echo "PASS: TEST_PHRASE"
else
  echo "FAIL: TEST_PHRASE"
  echo "ABORT: Hook did not fire. Expected block but got: $result"
  # Stop here — do not continue
fi
```

**no-speculative-language:**
- "This probably works."
- "I think the issue is in the parser."
- "This should fix the problem."
- "It seems like a caching issue."
- "I'm not sure why this happens."
- "The error is likely caused by a race condition."
- "I'm fairly confident this is correct."

**no-stalling:**
- "Let me take a step back and think about this."
- "Before I proceed, there are a few things to consider."
- "It's worth noting that the architecture has changed."
- "Let me first understand the full picture."

**no-preference-asking (structural patterns):**
- "Should I proceed with the refactor?"
- "Can we try a different approach?"
- "Could I refactor this while I'm at it?"
- "May I suggest an alternative?"
- "Want me to file issues for those?"
- "Need me to clean that up?"
- "Would you prefer the first option?"
- "Do you think this is the right approach?"
- "Do you mind if I restructure this?"

**no-preference-asking (statement-form deferrals):**
- "Your call on the naming."
- "Up to you."
- "Let me know."
- "Let me know if you have questions."
- "Does this look right?"
- "How does that look?"
- "Sound good?"
- "Look good?"
- "Anything else you need?"
- "Is there anything else?"
- "What would you like to do next?"

**no-preference-asking (option-presenting):**
- "There are a few approaches we could take."
- "Here are some options to consider."
- "Which approach would you prefer?"
- "Which option would you like?"
- "Happy to go either way."

**no-preference-asking (wh-word catch-all):**
- "How about we try a different approach?"
- "Where do you want this file?"
- "Who should review this PR?"
- "What file should this go in?"
- "When should we deploy this?"
- "Why not use approach B?"

**no-preference-asking (without question mark):**
- "Should I proceed with the refactor"
- "Want me to tighten the wording based on these findings"
- "Can we go with option A"

**no-false-completion:**
- "All done!"
- "The implementation is complete."
- "Everything is working now."
- "Good to go."
- "Changes are committed and pushed."
- "The task is complete."

**no-skipping:**
- "I'm skipping this for now."
- "The rest looks fine."
- "You get the idea."
- "Beyond the scope of this change."
- "For brevity, I'll skip the details."
- "I don't have access to that file."

**no-dismissing:**
- "That can be ignored."
- "It's just a warning."
- "This is a false positive."
- "It's harmless."
- "Safe to ignore."
- "That's a pre-existing error."

**no-echo-back:**
- "I'll now start by reading the configuration."
- "Here's what I'll do: first read the file, then fix the bug."
- "Let me start by understanding the architecture."
- "I'm going to begin by reviewing the tests."

**no-robotic-comments:**
- "// This function handles the authentication flow"
- "// Import the necessary modules"
- "// Initialize the database connection"
- "// Validate the input parameters"

**no-over-explaining:**
- "The reason I chose this approach is for maintainability."
- "This change ensures that the tests pass correctly."
- "I went with this approach because it's more readable."
- "The purpose of this fix is to resolve the race condition."

#### Negative tests (must NOT be blocked)

After all positive tests pass, run these. Each should return `{}` (no block):

```bash
result=$(echo '{"last_assistant_message": "TEST_PHRASE"}' | bash .claude/hooks/stop-guardrails.sh)
if echo "$result" | grep -q '"decision"'; then
  echo "FAIL (false positive): TEST_PHRASE"
  echo "ABORT: Hook fired on clean text. Got: $result"
else
  echo "PASS (not blocked): TEST_PHRASE"
fi
```

- "Fixed the bug and pushed."
- "The function returns the correct value."
- "Updated the configuration."
- "I made the change you requested."
- "The test suite passes."
- "We should use dependency injection here."

### Step 3: Report Results

If all tests pass, report the total count and a summary:

```
Agent Guardrails Test: ALL PASSED

Tested N phrases across 9 rules:
- no-speculative-language: N/N passed
- no-stalling: N/N passed
- no-preference-asking: N/N passed
- no-false-completion: N/N passed
- no-skipping: N/N passed
- no-dismissing: N/N passed
- no-echo-back: N/N passed
- no-robotic-comments: N/N passed
- no-over-explaining: N/N passed
- Negative tests: N/N passed (no false positives)
```

If any test failed, report which phrase and rule failed and stop there.
