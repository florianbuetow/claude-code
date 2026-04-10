#!/bin/bash
set -euo pipefail

input=$(cat)

# Prevent infinite loop: if hook already fired on this response, let it through
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active // false')
if [ "$stop_hook_active" = "true" ]; then
  echo '{}'
  exit 0
fi

message=$(echo "$input" | jq -r '.last_assistant_message // ""')

if [ -z "$message" ]; then
  echo '{}'
  exit 0
fi

blocked=()

# no-guessing
if echo "$message" | grep -qiE '(probably|most likely|possibly|perhaps|presumably|I believe|I think|I'\''m (fairly |not entirely |pretty )?confident|if I recall correctly|as far as I know|from my understanding|it (seems|appears) (like|that|to be)|it looks like|this (looks|seems) (correct|right)|that looks right|I'\''ll? assume|assuming that|this should (work|fix|resolve|handle|do the trick)|should be fine|everything should be working|that should do it|likely caused by|might be happening because|could be (due to|a|caused)|one possible explanation|a common cause|may have (already|been)|may be (a|the|related|caused)|might have|could have been|not sure (if|whether|why|what)|I'\''m not certain)'; then
  blocked+=("You made a claim you haven't verified. Investigate to confirm or deny it before proceeding.")
fi

# no-stalling
if echo "$message" | grep -qiE '(let me take a step back|taking a step back|before I proceed|before we proceed|before I continue|a few things to consider|there are some considerations|it'\''s worth noting|it'\''s important to note|one thing to keep in mind|let me (first )?explain|to summarize what|to clarify what|let me first understand|now let me also)'; then
  blocked+=("Your task is not complete. Continue working. If you need information, retrieve it now. If you have the information, act on it now.")
fi

# no-preference-asking
if echo "$message" | grep -qiE '(would you prefer|would you like me to|would you rather|do you want me to|want me to\b.*\?|should I\b.*\?|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think))'; then
  blocked+=("Re-read the requirements, specifications, and instructions you have been given. The answer to your question can be derived from the context. Make the best engineering decision based on what you already know. If after thorough review you genuinely cannot determine the answer, write on a single line: ESCALATING QUESTION: I am requiring an answer to the following — [state your question without a question mark]")
fi

# no-false-completion
if echo "$message" | grep -qiE '(all done|all set|we'\''re all set|we'\''re good|you'\''re all set|that'\''s everything|nothing else needs|no other changes|the fix is complete|implementation is complete|fully implemented|fully working|everything is working|everything works)'; then
  blocked+=("That sounds great. However, did you verify your results. Run all available tests and show their output. Do a manual check of the changes. If this is a web project, use Playwright MCP or CLI to manually test the changes and features you implemented. Show the verification output, then restate your completion claim.")
fi

# no-skipping
if echo "$message" | grep -qiE '(i('\''m| am) skipping|skip(ping)? this|let('\''s| us) skip|we('\''ll| will) skip|i('\''ll| will) skip|the rest (looks|seems|is) fine|everything else (seems|looks|is) (correct|fine|ok)|that part should be fine|should be straightforward|without (seeing|running|testing)|I haven'\''t tested this|have not (verified|confirmed|checked|validated|tested)|haven'\''t (verified|confirmed|checked|validated|tested)|similar changes would be needed|you get the idea|the pattern is the same|and so on|the other files don'\''t need|don'\''t think we need to change|I won'\''t go through every|and similar for the (other|rest)|the same (approach|pattern|logic) (applies|works) for|I'\''ll leave (that|the rest|it) (to|for|as)|left as an exercise|beyond the scope|outside the scope|for brevity|I don'\''t have access|I can'\''t access)'; then
  blocked+=("Your task is not complete. Do the work instead of describing it. If something cannot be done, explain exactly why. If it can be done, do it now.")
fi

# no-dismissing
if echo "$message" | grep -qiE '(not a real (bug|issue|error|problem)|can be ignored|just a warning|(is a |just a |only a )pre-existing|the only (failure|error|issue|problem|warning|bug) (is|was|being|comes from)|safe to ignore|not worth (fixing|investigating|worrying)|doesn'\''t matter|not important|harmless|benign|false positive|not a concern|don'\''t worry about|nothing to worry about|expected (error|warning|failure))'; then
  blocked+=("Do not dismiss issues without investigation. Diagnose the root cause and show evidence for your conclusion — test output, code references, or logs. No evidence means no dismissal.")
fi

if [ ${#blocked[@]} -eq 0 ]; then
  echo '{}'
  exit 0
fi

# Build block response
reason=$(printf '%s\n' "${blocked[@]}")

jq -n --arg reason "$reason" '{
  "decision": "block",
  "reason": $reason
}'
