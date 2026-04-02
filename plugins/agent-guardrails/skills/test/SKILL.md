---
name: agent-guardrails-test
description: Test installed agent guardrail hooks by sending trigger phrases through the stop hook script. Checks hook installation first, then runs two test phrases per rule. Use when user asks to "test guardrails", "verify hooks", "check guardrail patterns", "agent-guardrails test", or wants to confirm hooks are working.
---

# Agent Guardrails Test

Verify that the installed stop-guardrails.sh hook catches all six rules by sending test phrases through it.

## Workflow

### Step 1: Check Hook Installation

Verify the hook is installed and executable:

```bash
if [ ! -x .claude/hooks/stop-guardrails.sh ]; then
  echo "FAIL: .claude/hooks/stop-guardrails.sh not found or not executable"
  exit 1
fi

if ! cat .claude/settings.local.json 2>/dev/null | jq -e '.hooks.Stop' > /dev/null 2>&1; then
  echo "FAIL: No Stop hook configured in .claude/settings.local.json"
  exit 1
fi
```

If either check fails, tell the user to run `/agent-guardrails:install` first. Do not proceed.

### Step 2: Run Tests

For each rule, send two test phrases through the hook individually. Each test is a separate bash command:

```bash
result=$(echo '{"last_assistant_message": "TEST_PHRASE"}' | bash .claude/hooks/stop-guardrails.sh)
if echo "$result" | grep -q '"decision"'; then
  echo "PASS: TEST_PHRASE"
else
  echo "FAIL: TEST_PHRASE — expected block, got: $result"
fi
```

**Stop on first failure.** Do not continue after a FAIL.

#### Test phrases (2 per rule)

**no-speculative-language:**
1. `I think the issue is in the parser.`
2. `This should fix the problem.`

**no-stalling:**
1. `Before I proceed, there are a few things to consider.`
2. `Let me take a step back and think about this.`

**no-preference-asking:**
1. `Would you like me to refactor this?`
2. `Should I proceed with the fix?`

**no-false-completion:**
1. `Everything is working now.`
2. `The implementation is complete.`

**no-skipping:**
1. `The rest looks fine.`
2. `For brevity, I'll skip the details.`

**no-dismissing:**
1. `It's just a warning.`
2. `Safe to ignore.`

#### Negative tests (must NOT be blocked)

After all positive tests pass, run these. Each must return `{}`:

```bash
result=$(echo '{"last_assistant_message": "TEST_PHRASE"}' | bash .claude/hooks/stop-guardrails.sh)
if echo "$result" | grep -q '"decision"'; then
  echo "FAIL (false positive): TEST_PHRASE — got: $result"
else
  echo "PASS (clean): TEST_PHRASE"
fi
```

1. `Fixed the null pointer and pushed.`
2. `The function returns the expected value.`
3. `Updated the retry logic to handle timeouts.`
4. `The test suite runs in 4.2 seconds.`

### Step 3: Report Results

```
Agent Guardrails Test Results

| Rule | Test 1 | Test 2 |
|------|--------|--------|
| no-speculative-language | PASS | PASS |
| no-stalling | PASS | PASS |
| no-preference-asking | PASS | PASS |
| no-false-completion | PASS | PASS |
| no-skipping | PASS | PASS |
| no-dismissing | PASS | PASS |
| Negative tests | 4/4 clean |

All N tests passed.
```

If any test failed, show which phrase and rule failed and stop there.
